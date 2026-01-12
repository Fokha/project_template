"""
Backup & Recovery Template
==========================
Patterns for data backup and disaster recovery.

Use when:
- Data backup automation needed
- Point-in-time recovery required
- Multi-site redundancy
- Compliance requirements

Placeholders:
- {{BACKUP_RETENTION_DAYS}}: Days to retain backups
- {{BACKUP_SCHEDULE}}: Cron schedule for backups
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import logging
import hashlib
import json
import os

logger = logging.getLogger(__name__)


class BackupType(Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"


class BackupStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"


@dataclass
class BackupConfig:
    """Backup configuration."""
    name: str
    source_paths: List[str]
    destination: str
    backup_type: BackupType = BackupType.INCREMENTAL
    retention_days: int = 30
    compression: bool = True
    encryption: bool = False
    verify_after_backup: bool = True
    exclude_patterns: List[str] = field(default_factory=list)


@dataclass
class BackupRecord:
    """Record of a backup."""
    id: str
    config_name: str
    backup_type: BackupType
    status: BackupStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    size_bytes: int = 0
    file_count: int = 0
    location: str = ""
    checksum: str = ""
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BackupProvider(ABC):
    """Abstract backup provider."""

    @abstractmethod
    def backup(self, config: BackupConfig) -> BackupRecord:
        """Execute backup."""
        pass

    @abstractmethod
    def restore(self, record: BackupRecord, target_path: str) -> bool:
        """Restore from backup."""
        pass

    @abstractmethod
    def verify(self, record: BackupRecord) -> bool:
        """Verify backup integrity."""
        pass

    @abstractmethod
    def delete(self, record: BackupRecord) -> bool:
        """Delete a backup."""
        pass


class LocalBackupProvider(BackupProvider):
    """Local filesystem backup provider."""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def backup(self, config: BackupConfig) -> BackupRecord:
        """Execute local backup."""
        backup_id = f"{config.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir = self.base_path / backup_id

        record = BackupRecord(
            id=backup_id,
            config_name=config.name,
            backup_type=config.backup_type,
            status=BackupStatus.IN_PROGRESS,
            started_at=datetime.now()
        )

        try:
            backup_dir.mkdir(parents=True, exist_ok=True)

            total_size = 0
            file_count = 0
            checksums = []

            for source in config.source_paths:
                source_path = Path(source)
                if not source_path.exists():
                    logger.warning(f"Source not found: {source}")
                    continue

                if source_path.is_file():
                    # Copy single file
                    dest = backup_dir / source_path.name
                    self._copy_file(source_path, dest)
                    total_size += dest.stat().st_size
                    file_count += 1
                    checksums.append(self._file_checksum(dest))
                else:
                    # Copy directory
                    for file_path in source_path.rglob("*"):
                        if file_path.is_file():
                            # Check exclusions
                            if self._should_exclude(file_path, config.exclude_patterns):
                                continue

                            relative = file_path.relative_to(source_path)
                            dest = backup_dir / source_path.name / relative
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            self._copy_file(file_path, dest)
                            total_size += dest.stat().st_size
                            file_count += 1
                            checksums.append(self._file_checksum(dest))

            # Create manifest
            manifest = {
                "id": backup_id,
                "config": config.name,
                "timestamp": datetime.now().isoformat(),
                "files": file_count,
                "size": total_size,
                "checksums": checksums
            }
            manifest_path = backup_dir / "manifest.json"
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)

            record.status = BackupStatus.COMPLETED
            record.completed_at = datetime.now()
            record.size_bytes = total_size
            record.file_count = file_count
            record.location = str(backup_dir)
            record.checksum = hashlib.md5("".join(checksums).encode()).hexdigest()

            logger.info(f"Backup completed: {backup_id} ({file_count} files, {total_size} bytes)")

        except Exception as e:
            record.status = BackupStatus.FAILED
            record.error = str(e)
            logger.error(f"Backup failed: {e}")

        return record

    def restore(self, record: BackupRecord, target_path: str) -> bool:
        """Restore from backup."""
        try:
            backup_dir = Path(record.location)
            target = Path(target_path)

            if not backup_dir.exists():
                raise FileNotFoundError(f"Backup not found: {backup_dir}")

            target.mkdir(parents=True, exist_ok=True)

            for item in backup_dir.iterdir():
                if item.name == "manifest.json":
                    continue

                dest = target / item.name
                if item.is_file():
                    self._copy_file(item, dest)
                else:
                    self._copy_directory(item, dest)

            logger.info(f"Restore completed from {record.id} to {target_path}")
            return True

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False

    def verify(self, record: BackupRecord) -> bool:
        """Verify backup integrity."""
        try:
            backup_dir = Path(record.location)
            manifest_path = backup_dir / "manifest.json"

            if not manifest_path.exists():
                return False

            with open(manifest_path) as f:
                manifest = json.load(f)

            # Verify file count
            actual_files = sum(1 for f in backup_dir.rglob("*") if f.is_file() and f.name != "manifest.json")
            if actual_files != manifest["files"]:
                logger.warning(f"File count mismatch: expected {manifest['files']}, got {actual_files}")
                return False

            logger.info(f"Backup {record.id} verified successfully")
            return True

        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False

    def delete(self, record: BackupRecord) -> bool:
        """Delete a backup."""
        try:
            backup_dir = Path(record.location)
            if backup_dir.exists():
                import shutil
                shutil.rmtree(backup_dir)
                logger.info(f"Deleted backup: {record.id}")
            return True
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False

    def _copy_file(self, src: Path, dst: Path):
        """Copy a single file."""
        import shutil
        shutil.copy2(src, dst)

    def _copy_directory(self, src: Path, dst: Path):
        """Copy a directory."""
        import shutil
        shutil.copytree(src, dst, dirs_exist_ok=True)

    def _file_checksum(self, path: Path) -> str:
        """Calculate file checksum."""
        hash_md5 = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _should_exclude(self, path: Path, patterns: List[str]) -> bool:
        """Check if path should be excluded."""
        path_str = str(path)
        for pattern in patterns:
            if pattern in path_str:
                return True
        return False


class BackupScheduler:
    """Schedule and manage backups."""

    def __init__(self, provider: BackupProvider, retention_days: int = 30):
        self.provider = provider
        self.retention_days = retention_days
        self.configs: Dict[str, BackupConfig] = {}
        self.history: List[BackupRecord] = []

    def register_config(self, config: BackupConfig):
        """Register a backup configuration."""
        self.configs[config.name] = config

    def run_backup(self, config_name: str) -> BackupRecord:
        """Run a backup by config name."""
        if config_name not in self.configs:
            raise ValueError(f"Unknown config: {config_name}")

        config = self.configs[config_name]
        record = self.provider.backup(config)
        self.history.append(record)

        # Verify if configured
        if config.verify_after_backup and record.status == BackupStatus.COMPLETED:
            if self.provider.verify(record):
                record.status = BackupStatus.VERIFIED

        return record

    def run_all_backups(self) -> List[BackupRecord]:
        """Run all registered backups."""
        results = []
        for config_name in self.configs:
            result = self.run_backup(config_name)
            results.append(result)
        return results

    def cleanup_old_backups(self) -> int:
        """Remove backups older than retention period."""
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        deleted = 0

        for record in self.history[:]:
            if record.started_at < cutoff and record.status in [BackupStatus.COMPLETED, BackupStatus.VERIFIED]:
                if self.provider.delete(record):
                    self.history.remove(record)
                    deleted += 1

        logger.info(f"Cleaned up {deleted} old backups")
        return deleted

    def get_latest_backup(self, config_name: str) -> Optional[BackupRecord]:
        """Get the latest backup for a config."""
        for record in reversed(self.history):
            if record.config_name == config_name and record.status in [BackupStatus.COMPLETED, BackupStatus.VERIFIED]:
                return record
        return None


def create_trading_backup_scheduler(backup_path: str) -> BackupScheduler:
    """Create backup scheduler for trading system."""
    provider = LocalBackupProvider(backup_path)
    scheduler = BackupScheduler(provider, retention_days=30)

    # ML Models backup
    scheduler.register_config(BackupConfig(
        name="ml_models",
        source_paths=["models/", "trained_models/"],
        destination=backup_path,
        backup_type=BackupType.FULL,
        retention_days=90,
        exclude_patterns=["__pycache__", ".pyc"]
    ))

    # Database backup
    scheduler.register_config(BackupConfig(
        name="databases",
        source_paths=["data/trading.db", "data/signals.db", "knowledge_base/"],
        destination=backup_path,
        backup_type=BackupType.FULL,
        retention_days=60
    ))

    # Configuration backup
    scheduler.register_config(BackupConfig(
        name="config",
        source_paths=["config/", ".env"],
        destination=backup_path,
        backup_type=BackupType.FULL,
        retention_days=30,
        exclude_patterns=[".env.local", "secrets"]
    ))

    return scheduler


# Example usage
if __name__ == "__main__":
    import tempfile

    # Create temp directories for demo
    with tempfile.TemporaryDirectory() as backup_dir:
        with tempfile.TemporaryDirectory() as source_dir:
            # Create some test files
            test_file = Path(source_dir) / "test.txt"
            test_file.write_text("Hello, backup!")

            # Create scheduler
            provider = LocalBackupProvider(backup_dir)
            scheduler = BackupScheduler(provider)

            # Register config
            scheduler.register_config(BackupConfig(
                name="test_backup",
                source_paths=[source_dir],
                destination=backup_dir
            ))

            # Run backup
            print("Running backup...")
            record = scheduler.run_backup("test_backup")

            print(f"Status: {record.status.value}")
            print(f"Files: {record.file_count}")
            print(f"Size: {record.size_bytes} bytes")
            print(f"Location: {record.location}")
            print(f"Checksum: {record.checksum}")
