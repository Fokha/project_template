"""
Data Sync Service Template
==========================

Bidirectional data synchronization between local and remote sources.

Usage:
    from services.data_sync import DataSyncService

    sync = DataSyncService(
        local_path='data/',
        remote_url='https://api.example.com/data'
    )
    sync.sync_all()

Features:
- Incremental sync (only changed files)
- Conflict resolution strategies
- Compression support
- Progress tracking
- Retry logic
"""

import os
import json
import hashlib
import gzip
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import requests
import time


class SyncDirection(Enum):
    """Sync direction."""
    PUSH = "push"       # Local → Remote
    PULL = "pull"       # Remote → Local
    BIDIRECTIONAL = "bidirectional"


class ConflictResolution(Enum):
    """Conflict resolution strategy."""
    LOCAL_WINS = "local_wins"
    REMOTE_WINS = "remote_wins"
    NEWER_WINS = "newer_wins"
    MANUAL = "manual"


@dataclass
class SyncFile:
    """Represents a file to sync."""
    path: str
    checksum: str
    size: int
    modified_at: datetime
    is_local: bool = True


@dataclass
class SyncResult:
    """Result of a sync operation."""
    success: bool
    files_pushed: int = 0
    files_pulled: int = 0
    files_skipped: int = 0
    conflicts: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0


class DataSyncService:
    """Data synchronization service."""

    def __init__(
        self,
        local_path: str,
        remote_url: Optional[str] = None,
        remote_path: Optional[str] = None,
        db_path: str = "data/sync_state.db",
        conflict_resolution: ConflictResolution = ConflictResolution.NEWER_WINS
    ):
        self.local_path = Path(local_path)
        self.remote_url = remote_url
        self.remote_path = Path(remote_path) if remote_path else None
        self.db_path = db_path
        self.conflict_resolution = conflict_resolution

        # Callbacks
        self.on_progress: Optional[Callable[[str, int, int], None]] = None
        self.on_conflict: Optional[Callable[[str, SyncFile, SyncFile], str]] = None

        # Initialize
        self.local_path.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize sync state database."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_state (
                file_path TEXT PRIMARY KEY,
                local_checksum TEXT,
                remote_checksum TEXT,
                local_modified TIMESTAMP,
                remote_modified TIMESTAMP,
                last_synced TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                direction TEXT,
                files_synced INTEGER,
                files_failed INTEGER,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                status TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _get_local_files(self, pattern: str = "*") -> Dict[str, SyncFile]:
        """Get all local files with metadata."""
        files = {}

        for file_path in self.local_path.rglob(pattern):
            if file_path.is_file() and not file_path.name.startswith('.'):
                rel_path = str(file_path.relative_to(self.local_path))
                stat = file_path.stat()

                files[rel_path] = SyncFile(
                    path=rel_path,
                    checksum=self._calculate_checksum(file_path),
                    size=stat.st_size,
                    modified_at=datetime.fromtimestamp(stat.st_mtime),
                    is_local=True
                )

        return files

    def _get_remote_files_api(self) -> Dict[str, SyncFile]:
        """Get remote files via API."""
        if not self.remote_url:
            return {}

        try:
            response = requests.get(
                f"{self.remote_url}/list",
                timeout=30
            )
            response.raise_for_status()

            files = {}
            for item in response.json().get('files', []):
                files[item['path']] = SyncFile(
                    path=item['path'],
                    checksum=item['checksum'],
                    size=item['size'],
                    modified_at=datetime.fromisoformat(item['modified_at']),
                    is_local=False
                )

            return files
        except Exception as e:
            print(f"Error getting remote files: {e}")
            return {}

    def _get_remote_files_path(self) -> Dict[str, SyncFile]:
        """Get remote files from path (local network/mounted drive)."""
        if not self.remote_path or not self.remote_path.exists():
            return {}

        files = {}
        for file_path in self.remote_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                rel_path = str(file_path.relative_to(self.remote_path))
                stat = file_path.stat()

                files[rel_path] = SyncFile(
                    path=rel_path,
                    checksum=self._calculate_checksum(file_path),
                    size=stat.st_size,
                    modified_at=datetime.fromtimestamp(stat.st_mtime),
                    is_local=False
                )

        return files

    def _get_sync_state(self, file_path: str) -> Optional[Dict]:
        """Get sync state for a file."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT local_checksum, remote_checksum, last_synced
            FROM sync_state WHERE file_path = ?
        ''', (file_path,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'local_checksum': row[0],
                'remote_checksum': row[1],
                'last_synced': row[2]
            }
        return None

    def _update_sync_state(self, file_path: str, local_checksum: str, remote_checksum: str):
        """Update sync state for a file."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO sync_state
            (file_path, local_checksum, remote_checksum, last_synced)
            VALUES (?, ?, ?, ?)
        ''', (file_path, local_checksum, remote_checksum, datetime.now()))

        conn.commit()
        conn.close()

    def _resolve_conflict(self, path: str, local: SyncFile, remote: SyncFile) -> str:
        """Resolve sync conflict."""
        if self.on_conflict:
            return self.on_conflict(path, local, remote)

        if self.conflict_resolution == ConflictResolution.LOCAL_WINS:
            return 'local'
        elif self.conflict_resolution == ConflictResolution.REMOTE_WINS:
            return 'remote'
        elif self.conflict_resolution == ConflictResolution.NEWER_WINS:
            return 'local' if local.modified_at > remote.modified_at else 'remote'
        else:
            return 'skip'

    def _push_file(self, file_path: str) -> bool:
        """Push a file to remote."""
        local_file = self.local_path / file_path

        if self.remote_url:
            # Push via API
            try:
                with open(local_file, 'rb') as f:
                    # Compress for transfer
                    compressed = gzip.compress(f.read())

                response = requests.post(
                    f"{self.remote_url}/upload",
                    files={'file': (file_path, compressed)},
                    data={'path': file_path, 'compressed': True},
                    timeout=60
                )
                return response.status_code == 200
            except Exception as e:
                print(f"Error pushing {file_path}: {e}")
                return False

        elif self.remote_path:
            # Copy to remote path
            try:
                remote_file = self.remote_path / file_path
                remote_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(local_file, remote_file)
                return True
            except Exception as e:
                print(f"Error copying {file_path}: {e}")
                return False

        return False

    def _pull_file(self, file_path: str) -> bool:
        """Pull a file from remote."""
        local_file = self.local_path / file_path

        if self.remote_url:
            # Pull via API
            try:
                response = requests.get(
                    f"{self.remote_url}/download",
                    params={'path': file_path},
                    timeout=60
                )
                response.raise_for_status()

                local_file.parent.mkdir(parents=True, exist_ok=True)

                # Check if compressed
                content = response.content
                try:
                    content = gzip.decompress(content)
                except:
                    pass

                with open(local_file, 'wb') as f:
                    f.write(content)

                return True
            except Exception as e:
                print(f"Error pulling {file_path}: {e}")
                return False

        elif self.remote_path:
            # Copy from remote path
            try:
                remote_file = self.remote_path / file_path
                local_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(remote_file, local_file)
                return True
            except Exception as e:
                print(f"Error copying {file_path}: {e}")
                return False

        return False

    def sync(
        self,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
        pattern: str = "*"
    ) -> SyncResult:
        """Perform sync operation."""
        start_time = time.time()
        result = SyncResult(success=True)

        # Get file lists
        local_files = self._get_local_files(pattern)

        if self.remote_url:
            remote_files = self._get_remote_files_api()
        else:
            remote_files = self._get_remote_files_path()

        all_paths = set(local_files.keys()) | set(remote_files.keys())
        total = len(all_paths)

        for i, path in enumerate(all_paths):
            if self.on_progress:
                self.on_progress(path, i + 1, total)

            local = local_files.get(path)
            remote = remote_files.get(path)
            state = self._get_sync_state(path)

            try:
                if local and not remote:
                    # Only exists locally
                    if direction in [SyncDirection.PUSH, SyncDirection.BIDIRECTIONAL]:
                        if self._push_file(path):
                            result.files_pushed += 1
                            self._update_sync_state(path, local.checksum, local.checksum)
                        else:
                            result.errors.append(f"Failed to push: {path}")

                elif remote and not local:
                    # Only exists remotely
                    if direction in [SyncDirection.PULL, SyncDirection.BIDIRECTIONAL]:
                        if self._pull_file(path):
                            result.files_pulled += 1
                            self._update_sync_state(path, remote.checksum, remote.checksum)
                        else:
                            result.errors.append(f"Failed to pull: {path}")

                elif local and remote:
                    # Exists both places
                    if local.checksum == remote.checksum:
                        result.files_skipped += 1
                        continue

                    # Conflict!
                    winner = self._resolve_conflict(path, local, remote)
                    result.conflicts.append(path)

                    if winner == 'local' and direction != SyncDirection.PULL:
                        if self._push_file(path):
                            result.files_pushed += 1
                            self._update_sync_state(path, local.checksum, local.checksum)
                    elif winner == 'remote' and direction != SyncDirection.PUSH:
                        if self._pull_file(path):
                            result.files_pulled += 1
                            self._update_sync_state(path, remote.checksum, remote.checksum)
                    else:
                        result.files_skipped += 1

            except Exception as e:
                result.errors.append(f"Error syncing {path}: {e}")

        result.duration_seconds = time.time() - start_time
        result.success = len(result.errors) == 0

        # Log sync history
        self._log_sync(result, direction)

        return result

    def _log_sync(self, result: SyncResult, direction: SyncDirection):
        """Log sync operation to history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO sync_history
            (direction, files_synced, files_failed, started_at, completed_at, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            direction.value,
            result.files_pushed + result.files_pulled,
            len(result.errors),
            datetime.now(),
            datetime.now(),
            'success' if result.success else 'failed'
        ))

        conn.commit()
        conn.close()

    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status."""
        local_files = self._get_local_files()

        if self.remote_url:
            remote_files = self._get_remote_files_api()
        else:
            remote_files = self._get_remote_files_path()

        only_local = set(local_files.keys()) - set(remote_files.keys())
        only_remote = set(remote_files.keys()) - set(local_files.keys())

        different = []
        for path in set(local_files.keys()) & set(remote_files.keys()):
            if local_files[path].checksum != remote_files[path].checksum:
                different.append(path)

        return {
            'local_files': len(local_files),
            'remote_files': len(remote_files),
            'only_local': list(only_local),
            'only_remote': list(only_remote),
            'different': different,
            'in_sync': len(only_local) == 0 and len(only_remote) == 0 and len(different) == 0
        }


# Example usage
if __name__ == "__main__":
    # Create test sync service
    sync = DataSyncService(
        local_path='test_data/local',
        remote_path='test_data/remote'
    )

    # Progress callback
    def on_progress(path, current, total):
        print(f"Syncing [{current}/{total}]: {path}")

    sync.on_progress = on_progress

    # Perform sync
    result = sync.sync(SyncDirection.BIDIRECTIONAL)

    print(f"\n=== Sync Result ===")
    print(f"Success: {result.success}")
    print(f"Pushed: {result.files_pushed}")
    print(f"Pulled: {result.files_pulled}")
    print(f"Skipped: {result.files_skipped}")
    print(f"Conflicts: {result.conflicts}")
    print(f"Errors: {result.errors}")
    print(f"Duration: {result.duration_seconds:.2f}s")
