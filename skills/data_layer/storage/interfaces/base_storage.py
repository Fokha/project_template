# fokha_data/storage/interfaces/base_storage.py
# =============================================================================
# TEMPLATE: Base Storage Interface
# =============================================================================
# Abstract interface that all storage implementations must follow.
# Defines the contract for CRUD operations and querying.
# =============================================================================

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, TypeVar, Generic, Iterator
from enum import Enum


class StorageType(Enum):
    """Types of storage backends."""
    MEMORY = "memory"
    FILE = "file"
    SQLITE = "sqlite"
    POSTGRES = "postgres"
    REDIS = "redis"
    CUSTOM = "custom"


@dataclass
class StorageConfig:
    """
    Configuration for storage initialization.

    Attributes:
        storage_type: Type of storage backend
        connection_string: Connection string or file path
        options: Additional storage-specific options
    """
    storage_type: StorageType = StorageType.MEMORY
    connection_string: Optional[str] = None
    table_name: str = "data_records"
    options: Dict[str, Any] = field(default_factory=dict)

    # Common options:
    # - auto_create: bool - Auto-create tables/files
    # - batch_size: int - Batch operation size
    # - cache_enabled: bool - Enable caching
    # - compression: bool - Enable compression


@dataclass
class QueryFilter:
    """
    Filter for querying records.

    Attributes:
        field: Field to filter on
        operator: Comparison operator
        value: Value to compare against
    """
    field: str
    operator: str  # eq, ne, gt, gte, lt, lte, in, like, is_null
    value: Any

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "operator": self.operator,
            "value": self.value,
        }


@dataclass
class QueryOptions:
    """
    Options for querying records.

    Attributes:
        filters: List of filters to apply
        order_by: Field to order by
        order_dir: Order direction (asc/desc)
        limit: Maximum records to return
        offset: Number of records to skip
    """
    filters: List[QueryFilter] = field(default_factory=list)
    order_by: Optional[str] = None
    order_dir: str = "asc"
    limit: Optional[int] = None
    offset: int = 0

    def add_filter(self, field: str, operator: str, value: Any) -> "QueryOptions":
        self.filters.append(QueryFilter(field, operator, value))
        return self

    def eq(self, field: str, value: Any) -> "QueryOptions":
        return self.add_filter(field, "eq", value)

    def ne(self, field: str, value: Any) -> "QueryOptions":
        return self.add_filter(field, "ne", value)

    def gt(self, field: str, value: Any) -> "QueryOptions":
        return self.add_filter(field, "gt", value)

    def lt(self, field: str, value: Any) -> "QueryOptions":
        return self.add_filter(field, "lt", value)

    def contains(self, field: str, value: Any) -> "QueryOptions":
        return self.add_filter(field, "like", f"%{value}%")


T = TypeVar('T')


class BaseStorage(ABC, Generic[T]):
    """
    Abstract base class for all storage implementations.

    All storage backends must implement these methods to ensure
    consistent behavior across different persistence layers.

    Type parameter T represents the type of records being stored.

    Usage (implementation):
        class MyStorage(BaseStorage[DataRecord]):
            def save(self, record: DataRecord) -> str:
                # Implementation
                pass

    Usage (consumer):
        storage: BaseStorage[DataRecord] = SQLiteStorage("data.db")
        storage.save(record)
        record = storage.get("some-id")
    """

    def __init__(self, config: Optional[StorageConfig] = None):
        self.config = config or StorageConfig()
        self._is_connected = False

    # =========================================================================
    # CONNECTION LIFECYCLE
    # =========================================================================

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to storage backend."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to storage backend."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if storage is connected."""
        pass

    # =========================================================================
    # CRUD OPERATIONS
    # =========================================================================

    @abstractmethod
    def save(self, record: T) -> str:
        """
        Save a record to storage.

        Args:
            record: Record to save

        Returns:
            ID of saved record
        """
        pass

    @abstractmethod
    def save_many(self, records: List[T]) -> List[str]:
        """
        Save multiple records to storage.

        Args:
            records: List of records to save

        Returns:
            List of IDs of saved records
        """
        pass

    @abstractmethod
    def get(self, id: str) -> Optional[T]:
        """
        Retrieve a record by ID.

        Args:
            id: Record ID

        Returns:
            Record if found, None otherwise
        """
        pass

    @abstractmethod
    def get_many(self, ids: List[str]) -> List[T]:
        """
        Retrieve multiple records by IDs.

        Args:
            ids: List of record IDs

        Returns:
            List of found records (may be shorter than ids if some not found)
        """
        pass

    @abstractmethod
    def update(self, id: str, record: T) -> bool:
        """
        Update an existing record.

        Args:
            id: Record ID
            record: Updated record data

        Returns:
            True if updated, False if not found
        """
        pass

    @abstractmethod
    def delete(self, id: str) -> bool:
        """
        Delete a record by ID.

        Args:
            id: Record ID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def delete_many(self, ids: List[str]) -> int:
        """
        Delete multiple records by IDs.

        Args:
            ids: List of record IDs

        Returns:
            Number of records deleted
        """
        pass

    # =========================================================================
    # QUERYING
    # =========================================================================

    @abstractmethod
    def find(self, options: QueryOptions) -> List[T]:
        """
        Find records matching query options.

        Args:
            options: Query options (filters, ordering, pagination)

        Returns:
            List of matching records
        """
        pass

    @abstractmethod
    def find_one(self, options: QueryOptions) -> Optional[T]:
        """
        Find first record matching query options.

        Args:
            options: Query options

        Returns:
            First matching record or None
        """
        pass

    @abstractmethod
    def count(self, options: Optional[QueryOptions] = None) -> int:
        """
        Count records matching query options.

        Args:
            options: Query options (only filters used)

        Returns:
            Number of matching records
        """
        pass

    @abstractmethod
    def exists(self, id: str) -> bool:
        """
        Check if a record exists.

        Args:
            id: Record ID

        Returns:
            True if exists, False otherwise
        """
        pass

    # =========================================================================
    # BULK OPERATIONS
    # =========================================================================

    @abstractmethod
    def clear(self) -> int:
        """
        Delete all records.

        Returns:
            Number of records deleted
        """
        pass

    def upsert(self, record: T) -> str:
        """
        Insert or update a record.

        Default implementation; can be overridden for efficiency.

        Args:
            record: Record to upsert

        Returns:
            ID of upserted record
        """
        record_id = getattr(record, 'id', None)
        if record_id and self.exists(record_id):
            self.update(record_id, record)
            return record_id
        return self.save(record)

    def upsert_many(self, records: List[T]) -> List[str]:
        """
        Insert or update multiple records.

        Args:
            records: Records to upsert

        Returns:
            List of IDs
        """
        return [self.upsert(record) for record in records]

    # =========================================================================
    # ITERATION
    # =========================================================================

    def iterate(self, batch_size: int = 100) -> Iterator[T]:
        """
        Iterate over all records in batches.

        Args:
            batch_size: Number of records per batch

        Yields:
            Records one at a time
        """
        offset = 0
        while True:
            options = QueryOptions(limit=batch_size, offset=offset)
            batch = self.find(options)
            if not batch:
                break
            for record in batch:
                yield record
            offset += batch_size

    # =========================================================================
    # CONTEXT MANAGER
    # =========================================================================

    def __enter__(self) -> "BaseStorage[T]":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.disconnect()

    # =========================================================================
    # UTILITY
    # =========================================================================

    def health_check(self) -> Dict[str, Any]:
        """
        Check storage health.

        Returns:
            Health status dictionary
        """
        try:
            connected = self.is_connected()
            count = self.count() if connected else -1
            return {
                "healthy": connected,
                "connected": connected,
                "record_count": count,
                "storage_type": self.config.storage_type.value,
            }
        except Exception as e:
            return {
                "healthy": False,
                "connected": False,
                "error": str(e),
                "storage_type": self.config.storage_type.value,
            }
