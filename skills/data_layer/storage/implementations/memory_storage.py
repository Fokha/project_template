# fokha_data/storage/implementations/memory_storage.py
# =============================================================================
# TEMPLATE: In-Memory Storage
# =============================================================================
# Fast in-memory storage for testing and caching.
# Data is lost when process ends.
# =============================================================================

from typing import Dict, Any, List, Optional, TypeVar
from datetime import datetime
import copy

from ..interfaces.base_storage import BaseStorage, StorageConfig, QueryOptions, StorageType

T = TypeVar('T')


class MemoryStorage(BaseStorage[T]):
    """
    In-memory storage implementation.

    Fast, ephemeral storage ideal for:
    - Unit testing
    - Caching layer
    - Development/prototyping
    - Short-lived data

    Usage:
        storage = MemoryStorage()
        storage.connect()

        # Save
        record_id = storage.save(my_record)

        # Retrieve
        record = storage.get(record_id)

        # Query
        results = storage.find(QueryOptions().eq("status", "active"))
    """

    def __init__(self, config: Optional[StorageConfig] = None):
        if config is None:
            config = StorageConfig(storage_type=StorageType.MEMORY)
        super().__init__(config)
        self._data: Dict[str, T] = {}
        self._is_connected = False

    # =========================================================================
    # CONNECTION
    # =========================================================================

    def connect(self) -> None:
        """Connect (no-op for memory storage)."""
        self._is_connected = True

    def disconnect(self) -> None:
        """Disconnect and optionally clear data."""
        self._is_connected = False
        if self.config.options.get("clear_on_disconnect", False):
            self._data.clear()

    def is_connected(self) -> bool:
        return self._is_connected

    # =========================================================================
    # CRUD
    # =========================================================================

    def save(self, record: T) -> str:
        """Save a record."""
        record_id = self._get_record_id(record)
        self._data[record_id] = copy.deepcopy(record)
        return record_id

    def save_many(self, records: List[T]) -> List[str]:
        """Save multiple records."""
        return [self.save(record) for record in records]

    def get(self, id: str) -> Optional[T]:
        """Get a record by ID."""
        record = self._data.get(id)
        return copy.deepcopy(record) if record else None

    def get_many(self, ids: List[str]) -> List[T]:
        """Get multiple records by IDs."""
        return [copy.deepcopy(self._data[id]) for id in ids if id in self._data]

    def update(self, id: str, record: T) -> bool:
        """Update a record."""
        if id not in self._data:
            return False
        self._data[id] = copy.deepcopy(record)
        return True

    def delete(self, id: str) -> bool:
        """Delete a record."""
        if id not in self._data:
            return False
        del self._data[id]
        return True

    def delete_many(self, ids: List[str]) -> int:
        """Delete multiple records."""
        deleted = 0
        for id in ids:
            if self.delete(id):
                deleted += 1
        return deleted

    # =========================================================================
    # QUERYING
    # =========================================================================

    def find(self, options: QueryOptions) -> List[T]:
        """Find records matching filters."""
        results = list(self._data.values())

        # Apply filters
        for filter in options.filters:
            results = [r for r in results if self._matches_filter(r, filter)]

        # Apply ordering
        if options.order_by:
            reverse = options.order_dir.lower() == "desc"
            results.sort(key=lambda r: self._get_field_value(r, options.order_by) or "", reverse=reverse)

        # Apply pagination
        if options.offset:
            results = results[options.offset:]
        if options.limit:
            results = results[:options.limit]

        return [copy.deepcopy(r) for r in results]

    def find_one(self, options: QueryOptions) -> Optional[T]:
        """Find first matching record."""
        options.limit = 1
        results = self.find(options)
        return results[0] if results else None

    def count(self, options: Optional[QueryOptions] = None) -> int:
        """Count matching records."""
        if options is None or not options.filters:
            return len(self._data)

        results = list(self._data.values())
        for filter in options.filters:
            results = [r for r in results if self._matches_filter(r, filter)]
        return len(results)

    def exists(self, id: str) -> bool:
        """Check if record exists."""
        return id in self._data

    def clear(self) -> int:
        """Clear all records."""
        count = len(self._data)
        self._data.clear()
        return count

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _get_record_id(self, record: T) -> str:
        """Extract ID from record."""
        if hasattr(record, 'id'):
            return record.id
        if isinstance(record, dict) and 'id' in record:
            return record['id']
        # Generate ID
        import uuid
        return str(uuid.uuid4())

    def _get_field_value(self, record: T, field: str) -> Any:
        """Get field value from record (supports dot notation)."""
        # Handle DataRecord
        if hasattr(record, 'payload'):
            if field in ('id', 'created_at', 'updated_at'):
                return getattr(record, field, None)
            record = record.payload

        # Handle dict
        if isinstance(record, dict):
            keys = field.split(".")
            current = record
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return None
            return current

        # Handle object
        return getattr(record, field, None)

    def _matches_filter(self, record: T, filter) -> bool:
        """Check if record matches a filter."""
        value = self._get_field_value(record, filter.field)
        filter_value = filter.value
        op = filter.operator.lower()

        if op == "eq":
            return value == filter_value
        elif op == "ne":
            return value != filter_value
        elif op == "gt":
            return value is not None and value > filter_value
        elif op == "gte":
            return value is not None and value >= filter_value
        elif op == "lt":
            return value is not None and value < filter_value
        elif op == "lte":
            return value is not None and value <= filter_value
        elif op == "in":
            return value in filter_value
        elif op == "like":
            if value is None:
                return False
            pattern = filter_value.replace("%", "")
            return pattern.lower() in str(value).lower()
        elif op == "is_null":
            return value is None if filter_value else value is not None

        return True

    # =========================================================================
    # DEBUG/TESTING HELPERS
    # =========================================================================

    def get_all(self) -> List[T]:
        """Get all records (for testing)."""
        return [copy.deepcopy(r) for r in self._data.values()]

    def get_all_ids(self) -> List[str]:
        """Get all record IDs (for testing)."""
        return list(self._data.keys())

    def snapshot(self) -> Dict[str, T]:
        """Get a snapshot of all data (for testing)."""
        return copy.deepcopy(self._data)

    def restore(self, snapshot: Dict[str, T]) -> None:
        """Restore from a snapshot (for testing)."""
        self._data = copy.deepcopy(snapshot)
