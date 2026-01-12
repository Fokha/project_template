"""
Data Synchronization Template
=============================
Patterns for data synchronization across systems.

Use when:
- Multi-system data sync needed
- Incremental sync required
- Conflict resolution needed
- State tracking necessary

Placeholders:
- {{SYNC_INTERVAL}}: Sync interval in seconds
- {{BATCH_SIZE}}: Batch size for sync
"""

from typing import Any, Callable, Dict, List, Optional, Set, TypeVar
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime, timedelta
import logging
import json
import hashlib
import time
import threading

logger = logging.getLogger(__name__)

T = TypeVar('T')


class SyncDirection(Enum):
    PUSH = "push"  # Local to remote
    PULL = "pull"  # Remote to local
    BIDIRECTIONAL = "bidirectional"


class ConflictResolution(Enum):
    LOCAL_WINS = "local_wins"
    REMOTE_WINS = "remote_wins"
    NEWEST_WINS = "newest_wins"
    MANUAL = "manual"


class SyncStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


@dataclass
class SyncItem:
    """Item to be synchronized."""
    id: str
    data: Dict[str, Any]
    checksum: str
    modified_at: datetime
    source: str
    version: int = 1


@dataclass
class SyncConflict:
    """Sync conflict record."""
    item_id: str
    local_item: SyncItem
    remote_item: SyncItem
    resolution: Optional[ConflictResolution] = None
    resolved_at: Optional[datetime] = None


@dataclass
class SyncState:
    """Sync state tracking."""
    last_sync: Optional[datetime] = None
    last_local_cursor: Optional[str] = None
    last_remote_cursor: Optional[str] = None
    items_synced: int = 0
    items_failed: int = 0
    conflicts: int = 0


@dataclass
class SyncResult:
    """Result of a sync operation."""
    status: SyncStatus
    items_pushed: int = 0
    items_pulled: int = 0
    conflicts: List[SyncConflict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0


class DataStore(ABC):
    """Abstract data store for sync."""

    @abstractmethod
    def get_items(
        self,
        since: Optional[datetime] = None,
        cursor: Optional[str] = None,
        limit: int = 100
    ) -> tuple:  # (items, next_cursor)
        """Get items for sync."""
        pass

    @abstractmethod
    def get_item(self, item_id: str) -> Optional[SyncItem]:
        """Get a single item."""
        pass

    @abstractmethod
    def put_item(self, item: SyncItem) -> bool:
        """Put an item."""
        pass

    @abstractmethod
    def delete_item(self, item_id: str) -> bool:
        """Delete an item."""
        pass


class MemoryDataStore(DataStore):
    """In-memory data store for testing."""

    def __init__(self, name: str = "memory"):
        self.name = name
        self.items: Dict[str, SyncItem] = {}
        self._lock = threading.Lock()

    def get_items(
        self,
        since: Optional[datetime] = None,
        cursor: Optional[str] = None,
        limit: int = 100
    ) -> tuple:
        with self._lock:
            items = list(self.items.values())

            if since:
                items = [i for i in items if i.modified_at > since]

            items.sort(key=lambda x: x.modified_at)

            # Simple pagination
            start = 0
            if cursor:
                for i, item in enumerate(items):
                    if item.id == cursor:
                        start = i + 1
                        break

            page = items[start:start + limit]
            next_cursor = page[-1].id if len(page) == limit else None

            return page, next_cursor

    def get_item(self, item_id: str) -> Optional[SyncItem]:
        with self._lock:
            return self.items.get(item_id)

    def put_item(self, item: SyncItem) -> bool:
        with self._lock:
            self.items[item.id] = item
            return True

    def delete_item(self, item_id: str) -> bool:
        with self._lock:
            if item_id in self.items:
                del self.items[item_id]
                return True
            return False


class SyncEngine:
    """
    Data synchronization engine.

    Example:
        engine = SyncEngine(
            local=LocalStore(),
            remote=RemoteStore(),
            direction=SyncDirection.BIDIRECTIONAL
        )

        result = engine.sync()
        print(f"Synced {result.items_pushed + result.items_pulled} items")
    """

    def __init__(
        self,
        local: DataStore,
        remote: DataStore,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
        conflict_resolution: ConflictResolution = ConflictResolution.NEWEST_WINS,
        batch_size: int = 100
    ):
        self.local = local
        self.remote = remote
        self.direction = direction
        self.conflict_resolution = conflict_resolution
        self.batch_size = batch_size
        self.state = SyncState()
        self.sync_history: List[SyncResult] = []
        self._lock = threading.Lock()

    def sync(self, full: bool = False) -> SyncResult:
        """Execute synchronization."""
        start_time = time.time()
        result = SyncResult(status=SyncStatus.IN_PROGRESS)

        try:
            since = None if full else self.state.last_sync

            if self.direction in [SyncDirection.PUSH, SyncDirection.BIDIRECTIONAL]:
                pushed, conflicts = self._sync_direction(
                    source=self.local,
                    target=self.remote,
                    since=since
                )
                result.items_pushed = pushed
                result.conflicts.extend(conflicts)

            if self.direction in [SyncDirection.PULL, SyncDirection.BIDIRECTIONAL]:
                pulled, conflicts = self._sync_direction(
                    source=self.remote,
                    target=self.local,
                    since=since
                )
                result.items_pulled = pulled
                result.conflicts.extend(conflicts)

            # Update state
            self.state.last_sync = datetime.now()
            self.state.items_synced += result.items_pushed + result.items_pulled
            self.state.conflicts += len(result.conflicts)

            result.status = SyncStatus.COMPLETED if not result.conflicts else SyncStatus.CONFLICT

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            result.status = SyncStatus.FAILED
            result.errors.append(str(e))

        result.duration_ms = (time.time() - start_time) * 1000
        self.sync_history.append(result)

        return result

    def _sync_direction(
        self,
        source: DataStore,
        target: DataStore,
        since: Optional[datetime]
    ) -> tuple:
        """Sync items from source to target."""
        synced = 0
        conflicts = []
        cursor = None

        while True:
            items, cursor = source.get_items(
                since=since,
                cursor=cursor,
                limit=self.batch_size
            )

            if not items:
                break

            for item in items:
                existing = target.get_item(item.id)

                if existing:
                    # Check for conflict
                    if existing.checksum != item.checksum:
                        conflict = self._resolve_conflict(item, existing)
                        if conflict:
                            conflicts.append(conflict)
                            continue

                item_copy = SyncItem(
                    id=item.id,
                    data=item.data.copy(),
                    checksum=item.checksum,
                    modified_at=item.modified_at,
                    source=source.__class__.__name__,
                    version=item.version + 1 if existing else 1
                )

                if target.put_item(item_copy):
                    synced += 1

            if not cursor:
                break

        return synced, conflicts

    def _resolve_conflict(
        self,
        source_item: SyncItem,
        target_item: SyncItem
    ) -> Optional[SyncConflict]:
        """Resolve sync conflict."""
        conflict = SyncConflict(
            item_id=source_item.id,
            local_item=source_item,
            remote_item=target_item
        )

        if self.conflict_resolution == ConflictResolution.LOCAL_WINS:
            return None  # Source wins, no conflict
        elif self.conflict_resolution == ConflictResolution.REMOTE_WINS:
            # Skip this item
            conflict.resolution = ConflictResolution.REMOTE_WINS
            conflict.resolved_at = datetime.now()
            return conflict
        elif self.conflict_resolution == ConflictResolution.NEWEST_WINS:
            if source_item.modified_at > target_item.modified_at:
                return None  # Source is newer, proceed
            conflict.resolution = ConflictResolution.NEWEST_WINS
            conflict.resolved_at = datetime.now()
            return conflict
        else:  # MANUAL
            return conflict

    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status."""
        return {
            "last_sync": self.state.last_sync.isoformat() if self.state.last_sync else None,
            "items_synced": self.state.items_synced,
            "items_failed": self.state.items_failed,
            "conflicts": self.state.conflicts,
            "history_count": len(self.sync_history),
            "recent_syncs": [
                {
                    "status": r.status.value,
                    "pushed": r.items_pushed,
                    "pulled": r.items_pulled,
                    "duration_ms": r.duration_ms
                }
                for r in self.sync_history[-5:]
            ]
        }


class ScheduledSync:
    """Scheduled data synchronization."""

    def __init__(
        self,
        engine: SyncEngine,
        interval_seconds: int = 300
    ):
        self.engine = engine
        self.interval = interval_seconds
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Start scheduled sync."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._sync_loop, daemon=True)
        self._thread.start()
        logger.info(f"Scheduled sync started (every {self.interval}s)")

    def stop(self):
        """Stop scheduled sync."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Scheduled sync stopped")

    def _sync_loop(self):
        """Background sync loop."""
        while self._running:
            try:
                result = self.engine.sync()
                logger.info(
                    f"Sync completed: {result.items_pushed} pushed, "
                    f"{result.items_pulled} pulled, {len(result.conflicts)} conflicts"
                )
            except Exception as e:
                logger.error(f"Scheduled sync error: {e}")

            # Wait for next interval
            for _ in range(self.interval):
                if not self._running:
                    break
                time.sleep(1)


def compute_checksum(data: Dict[str, Any]) -> str:
    """Compute checksum for data."""
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.md5(json_str.encode()).hexdigest()


def create_trading_sync_engine(
    local_store: DataStore,
    remote_store: DataStore
) -> SyncEngine:
    """Create sync engine for trading data."""
    return SyncEngine(
        local=local_store,
        remote=remote_store,
        direction=SyncDirection.BIDIRECTIONAL,
        conflict_resolution=ConflictResolution.NEWEST_WINS,
        batch_size=100
    )


# Example usage
if __name__ == "__main__":
    # Create stores
    local = MemoryDataStore("local")
    remote = MemoryDataStore("remote")

    # Add some local items
    for i in range(5):
        item = SyncItem(
            id=f"item_{i}",
            data={"name": f"Local Item {i}", "value": i * 10},
            checksum=compute_checksum({"name": f"Local Item {i}", "value": i * 10}),
            modified_at=datetime.now(),
            source="local"
        )
        local.put_item(item)

    # Add some remote items
    for i in range(3, 8):
        item = SyncItem(
            id=f"item_{i}",
            data={"name": f"Remote Item {i}", "value": i * 20},
            checksum=compute_checksum({"name": f"Remote Item {i}", "value": i * 20}),
            modified_at=datetime.now() + timedelta(seconds=1),  # Newer
            source="remote"
        )
        remote.put_item(item)

    # Create engine and sync
    engine = create_trading_sync_engine(local, remote)

    print("Before sync:")
    print(f"  Local items: {len(local.items)}")
    print(f"  Remote items: {len(remote.items)}")

    result = engine.sync()

    print(f"\nSync result:")
    print(f"  Status: {result.status.value}")
    print(f"  Pushed: {result.items_pushed}")
    print(f"  Pulled: {result.items_pulled}")
    print(f"  Conflicts: {len(result.conflicts)}")
    print(f"  Duration: {result.duration_ms:.1f}ms")

    print(f"\nAfter sync:")
    print(f"  Local items: {len(local.items)}")
    print(f"  Remote items: {len(remote.items)}")

    print(f"\nSync status: {engine.get_sync_status()}")
