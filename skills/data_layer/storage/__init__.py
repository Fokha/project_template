# fokha_data/storage/__init__.py
# =============================================================================
# TEMPLATE: Data Storage Package
# =============================================================================
# Storage layer provides persistence abstractions for data records.
# Supports multiple backends through a common interface.
#
# Components:
#   - BaseStorage: Abstract interface for all storage implementations
#   - MemoryStorage: In-memory storage (for testing/caching)
#   - FileStorage: JSON/CSV file-based storage
#   - SQLiteStorage: SQLite database storage
#   - Repository: Higher-level data access patterns
#
# USAGE:
#   from fokha_data.storage import MemoryStorage, SQLiteStorage
#
#   # In-memory for testing
#   storage = MemoryStorage()
#   storage.save(record)
#
#   # SQLite for production
#   storage = SQLiteStorage("data.db")
#   storage.save(record)
# =============================================================================

from .interfaces.base_storage import BaseStorage, StorageConfig
from .implementations.memory_storage import MemoryStorage
from .implementations.file_storage import FileStorage, JSONStorage, CSVStorage
from .implementations.sqlite_storage import SQLiteStorage
from .repositories.base_repository import BaseRepository

__all__ = [
    # Interfaces
    "BaseStorage",
    "StorageConfig",
    # Implementations
    "MemoryStorage",
    "FileStorage",
    "JSONStorage",
    "CSVStorage",
    "SQLiteStorage",
    # Repositories
    "BaseRepository",
]
