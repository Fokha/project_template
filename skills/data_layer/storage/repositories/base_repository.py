# fokha_data/storage/repositories/base_repository.py
# =============================================================================
# TEMPLATE: Base Repository
# =============================================================================
# Repository pattern provides higher-level data access abstractions.
# Wraps storage with domain-specific methods.
# =============================================================================

from typing import Dict, Any, List, Optional, TypeVar, Generic, Callable
from datetime import datetime

from ..interfaces.base_storage import BaseStorage, QueryOptions

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Base repository providing domain-oriented data access.

    Repositories add:
    - Domain-specific query methods
    - Caching
    - Validation before persistence
    - Event hooks (before/after save, etc.)

    Usage:
        # Create a domain-specific repository
        class UserRepository(BaseRepository[User]):
            def find_by_email(self, email: str) -> Optional[User]:
                return self.find_one_by("email", email)

            def find_active_users(self) -> List[User]:
                return self.find_by("status", "active")

        # Use it
        repo = UserRepository(storage)
        user = repo.find_by_email("test@example.com")
    """

    def __init__(self, storage: BaseStorage[T]):
        self.storage = storage
        self._cache: Dict[str, T] = {}
        self._cache_enabled = False

        # Hooks
        self._before_save: List[Callable[[T], T]] = []
        self._after_save: List[Callable[[T], None]] = []
        self._before_delete: List[Callable[[str], bool]] = []
        self._after_delete: List[Callable[[str], None]] = []

    # =========================================================================
    # CONFIGURATION
    # =========================================================================

    def enable_cache(self, enabled: bool = True) -> "BaseRepository[T]":
        """Enable/disable caching."""
        self._cache_enabled = enabled
        if not enabled:
            self._cache.clear()
        return self

    def clear_cache(self) -> "BaseRepository[T]":
        """Clear the cache."""
        self._cache.clear()
        return self

    def on_before_save(self, hook: Callable[[T], T]) -> "BaseRepository[T]":
        """Register a before-save hook."""
        self._before_save.append(hook)
        return self

    def on_after_save(self, hook: Callable[[T], None]) -> "BaseRepository[T]":
        """Register an after-save hook."""
        self._after_save.append(hook)
        return self

    def on_before_delete(self, hook: Callable[[str], bool]) -> "BaseRepository[T]":
        """Register a before-delete hook. Return False to cancel."""
        self._before_delete.append(hook)
        return self

    def on_after_delete(self, hook: Callable[[str], None]) -> "BaseRepository[T]":
        """Register an after-delete hook."""
        self._after_delete.append(hook)
        return self

    # =========================================================================
    # CRUD
    # =========================================================================

    def save(self, record: T) -> str:
        """Save a record with hooks."""
        # Apply before-save hooks
        for hook in self._before_save:
            record = hook(record)

        # Save
        record_id = self.storage.save(record)

        # Update cache
        if self._cache_enabled:
            self._cache[record_id] = record

        # Apply after-save hooks
        for hook in self._after_save:
            hook(record)

        return record_id

    def save_all(self, records: List[T]) -> List[str]:
        """Save multiple records."""
        return [self.save(record) for record in records]

    def get(self, id: str) -> Optional[T]:
        """Get a record by ID with caching."""
        # Check cache
        if self._cache_enabled and id in self._cache:
            return self._cache[id]

        # Fetch from storage
        record = self.storage.get(id)

        # Update cache
        if self._cache_enabled and record:
            self._cache[id] = record

        return record

    def get_or_fail(self, id: str) -> T:
        """Get a record or raise exception."""
        record = self.get(id)
        if record is None:
            raise ValueError(f"Record not found: {id}")
        return record

    def delete(self, id: str) -> bool:
        """Delete a record with hooks."""
        # Apply before-delete hooks
        for hook in self._before_delete:
            if not hook(id):
                return False

        # Delete
        result = self.storage.delete(id)

        # Clear from cache
        if self._cache_enabled:
            self._cache.pop(id, None)

        # Apply after-delete hooks
        if result:
            for hook in self._after_delete:
                hook(id)

        return result

    # =========================================================================
    # QUERYING
    # =========================================================================

    def find_all(self, limit: int = None, offset: int = 0) -> List[T]:
        """Find all records with pagination."""
        options = QueryOptions(limit=limit, offset=offset)
        return self.storage.find(options)

    def find_by(self, field: str, value: Any) -> List[T]:
        """Find records where field equals value."""
        options = QueryOptions().eq(field, value)
        return self.storage.find(options)

    def find_one_by(self, field: str, value: Any) -> Optional[T]:
        """Find first record where field equals value."""
        options = QueryOptions().eq(field, value)
        options.limit = 1
        results = self.storage.find(options)
        return results[0] if results else None

    def find_by_ids(self, ids: List[str]) -> List[T]:
        """Find records by list of IDs."""
        # Check cache first
        if self._cache_enabled:
            cached = []
            missing_ids = []
            for id in ids:
                if id in self._cache:
                    cached.append(self._cache[id])
                else:
                    missing_ids.append(id)

            if not missing_ids:
                return cached

            # Fetch missing from storage
            fetched = self.storage.get_many(missing_ids)

            # Update cache
            for record in fetched:
                record_id = getattr(record, 'id', None) or record.get('id')
                if record_id:
                    self._cache[record_id] = record

            return cached + fetched

        return self.storage.get_many(ids)

    def exists(self, id: str) -> bool:
        """Check if record exists."""
        if self._cache_enabled and id in self._cache:
            return True
        return self.storage.exists(id)

    def count(self) -> int:
        """Count all records."""
        return self.storage.count()

    def count_by(self, field: str, value: Any) -> int:
        """Count records where field equals value."""
        options = QueryOptions().eq(field, value)
        return self.storage.count(options)

    # =========================================================================
    # BATCH OPERATIONS
    # =========================================================================

    def delete_all(self) -> int:
        """Delete all records."""
        count = self.storage.clear()
        if self._cache_enabled:
            self._cache.clear()
        return count

    def delete_by(self, field: str, value: Any) -> int:
        """Delete records where field equals value."""
        records = self.find_by(field, value)
        ids = [getattr(r, 'id', None) or r.get('id') for r in records]
        return self.storage.delete_many([id for id in ids if id])

    # =========================================================================
    # UTILITY
    # =========================================================================

    def refresh(self, record: T) -> Optional[T]:
        """Refresh a record from storage."""
        record_id = getattr(record, 'id', None) or record.get('id')
        if not record_id:
            return None

        # Clear from cache
        if self._cache_enabled:
            self._cache.pop(record_id, None)

        return self.get(record_id)

    def with_storage(self, storage: BaseStorage[T]) -> "BaseRepository[T]":
        """Create a new repository with different storage."""
        repo = BaseRepository(storage)
        repo._cache_enabled = self._cache_enabled
        repo._before_save = self._before_save.copy()
        repo._after_save = self._after_save.copy()
        repo._before_delete = self._before_delete.copy()
        repo._after_delete = self._after_delete.copy()
        return repo
