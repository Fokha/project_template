# fokha_data/storage/implementations/file_storage.py
# =============================================================================
# TEMPLATE: File-Based Storage
# =============================================================================
# File-based storage for JSON and CSV formats.
# Good for simple persistence without database setup.
# =============================================================================

from typing import Dict, Any, List, Optional, TypeVar
from pathlib import Path
import json
import csv
import os

from ..interfaces.base_storage import BaseStorage, StorageConfig, QueryOptions, StorageType

T = TypeVar('T')


class FileStorage(BaseStorage[T]):
    """
    Base file storage implementation.

    Provides common functionality for file-based storage.
    Subclasses implement specific formats (JSON, CSV).
    """

    def __init__(self, file_path: str, config: Optional[StorageConfig] = None):
        if config is None:
            config = StorageConfig(storage_type=StorageType.FILE, connection_string=file_path)
        super().__init__(config)
        self.file_path = Path(file_path)
        self._data: Dict[str, T] = {}
        self._is_connected = False

    def connect(self) -> None:
        """Load data from file."""
        self._is_connected = True
        if self.file_path.exists():
            self._load()

    def disconnect(self) -> None:
        """Save data to file and disconnect."""
        if self._is_connected:
            self._save()
        self._is_connected = False

    def is_connected(self) -> bool:
        return self._is_connected

    def _load(self) -> None:
        """Load data from file. Override in subclass."""
        raise NotImplementedError

    def _save(self) -> None:
        """Save data to file. Override in subclass."""
        raise NotImplementedError

    # CRUD operations (same as MemoryStorage)
    def save(self, record: T) -> str:
        record_id = self._get_record_id(record)
        self._data[record_id] = record
        if self.config.options.get("auto_save", True):
            self._save()
        return record_id

    def save_many(self, records: List[T]) -> List[str]:
        ids = [self._get_record_id(r) for r in records]
        for record, record_id in zip(records, ids):
            self._data[record_id] = record
        if self.config.options.get("auto_save", True):
            self._save()
        return ids

    def get(self, id: str) -> Optional[T]:
        return self._data.get(id)

    def get_many(self, ids: List[str]) -> List[T]:
        return [self._data[id] for id in ids if id in self._data]

    def update(self, id: str, record: T) -> bool:
        if id not in self._data:
            return False
        self._data[id] = record
        if self.config.options.get("auto_save", True):
            self._save()
        return True

    def delete(self, id: str) -> bool:
        if id not in self._data:
            return False
        del self._data[id]
        if self.config.options.get("auto_save", True):
            self._save()
        return True

    def delete_many(self, ids: List[str]) -> int:
        deleted = sum(1 for id in ids if id in self._data)
        for id in ids:
            self._data.pop(id, None)
        if deleted > 0 and self.config.options.get("auto_save", True):
            self._save()
        return deleted

    def find(self, options: QueryOptions) -> List[T]:
        results = list(self._data.values())
        for filter in options.filters:
            results = [r for r in results if self._matches_filter(r, filter)]
        if options.order_by:
            reverse = options.order_dir.lower() == "desc"
            results.sort(key=lambda r: self._get_field_value(r, options.order_by) or "", reverse=reverse)
        if options.offset:
            results = results[options.offset:]
        if options.limit:
            results = results[:options.limit]
        return results

    def find_one(self, options: QueryOptions) -> Optional[T]:
        options.limit = 1
        results = self.find(options)
        return results[0] if results else None

    def count(self, options: Optional[QueryOptions] = None) -> int:
        if options is None or not options.filters:
            return len(self._data)
        results = list(self._data.values())
        for filter in options.filters:
            results = [r for r in results if self._matches_filter(r, filter)]
        return len(results)

    def exists(self, id: str) -> bool:
        return id in self._data

    def clear(self) -> int:
        count = len(self._data)
        self._data.clear()
        if self.config.options.get("auto_save", True):
            self._save()
        return count

    def _get_record_id(self, record: T) -> str:
        if hasattr(record, 'id'):
            return record.id
        if isinstance(record, dict) and 'id' in record:
            return record['id']
        import uuid
        return str(uuid.uuid4())

    def _get_field_value(self, record: T, field: str) -> Any:
        if hasattr(record, 'payload'):
            if field in ('id', 'created_at', 'updated_at'):
                return getattr(record, field, None)
            record = record.payload
        if isinstance(record, dict):
            keys = field.split(".")
            current = record
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return None
            return current
        return getattr(record, field, None)

    def _matches_filter(self, record: T, filter) -> bool:
        value = self._get_field_value(record, filter.field)
        filter_value = filter.value
        op = filter.operator.lower()
        if op == "eq":
            return value == filter_value
        elif op == "ne":
            return value != filter_value
        elif op == "gt":
            return value is not None and value > filter_value
        elif op == "lt":
            return value is not None and value < filter_value
        elif op == "in":
            return value in filter_value
        elif op == "like":
            if value is None:
                return False
            pattern = filter_value.replace("%", "")
            return pattern.lower() in str(value).lower()
        return True


class JSONStorage(FileStorage[T]):
    """
    JSON file storage implementation.

    Stores all records in a single JSON file.

    Usage:
        storage = JSONStorage("data.json")
        storage.connect()
        storage.save(record)
        storage.disconnect()  # Saves to file
    """

    def _load(self) -> None:
        """Load data from JSON file."""
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    # Array format: [{...}, {...}]
                    self._data = {self._get_record_id(r): r for r in data}
                else:
                    # Object format: {"id": {...}, ...}
                    self._data = data
        except (json.JSONDecodeError, FileNotFoundError):
            self._data = {}

    def _save(self) -> None:
        """Save data to JSON file."""
        # Ensure directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        format = self.config.options.get("format", "object")
        indent = self.config.options.get("indent", 2)

        with open(self.file_path, 'w') as f:
            if format == "array":
                json.dump(list(self._data.values()), f, indent=indent, default=str)
            else:
                json.dump(self._data, f, indent=indent, default=str)


class CSVStorage(FileStorage[Dict[str, Any]]):
    """
    CSV file storage implementation.

    Stores records as rows in a CSV file.
    Best for flat, tabular data.

    Usage:
        storage = CSVStorage("data.csv")
        storage.connect()
        storage.save({"id": "1", "name": "Test", "value": 100})
        storage.disconnect()
    """

    def __init__(self, file_path: str, config: Optional[StorageConfig] = None):
        super().__init__(file_path, config)
        self._fieldnames: List[str] = []

    def _load(self) -> None:
        """Load data from CSV file."""
        try:
            with open(self.file_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                self._fieldnames = reader.fieldnames or []
                for row in reader:
                    record_id = row.get('id', str(len(self._data)))
                    self._data[record_id] = row
        except FileNotFoundError:
            self._data = {}

    def _save(self) -> None:
        """Save data to CSV file."""
        if not self._data:
            return

        # Ensure directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Collect all fieldnames
        all_fields = set()
        for record in self._data.values():
            if isinstance(record, dict):
                all_fields.update(record.keys())

        # Ensure 'id' is first
        fieldnames = ['id'] if 'id' in all_fields else []
        fieldnames.extend(sorted(f for f in all_fields if f != 'id'))

        with open(self.file_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in self._data.values():
                if isinstance(record, dict):
                    writer.writerow(record)
