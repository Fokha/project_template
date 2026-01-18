# fokha_data/storage/implementations/sqlite_storage.py
# =============================================================================
# TEMPLATE: SQLite Storage
# =============================================================================
# SQLite database storage for persistent, queryable data.
# Good balance of simplicity and capability.
# =============================================================================

from typing import Dict, Any, List, Optional, TypeVar
import sqlite3
import json
from datetime import datetime

from ..interfaces.base_storage import BaseStorage, StorageConfig, QueryOptions, QueryFilter, StorageType

T = TypeVar('T')


class SQLiteStorage(BaseStorage[T]):
    """
    SQLite storage implementation.

    Stores records in a SQLite database with JSON payload.

    Features:
    - ACID transactions
    - SQL querying
    - Indexing support
    - Good performance for medium datasets

    Usage:
        storage = SQLiteStorage("data.db", table_name="records")
        storage.connect()

        # Save with DataRecord
        storage.save(DataRecord(meta=meta, payload={"name": "test"}))

        # Save plain dict
        storage.save({"id": "123", "name": "test"})

        # Query
        results = storage.find(QueryOptions().eq("payload.name", "test"))
    """

    def __init__(
        self,
        db_path: str,
        table_name: str = "data_records",
        config: Optional[StorageConfig] = None,
    ):
        if config is None:
            config = StorageConfig(
                storage_type=StorageType.SQLITE,
                connection_string=db_path,
                table_name=table_name,
            )
        super().__init__(config)
        self.db_path = db_path
        self.table_name = table_name
        self._conn: Optional[sqlite3.Connection] = None

    # =========================================================================
    # CONNECTION
    # =========================================================================

    def connect(self) -> None:
        """Connect to SQLite database."""
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._is_connected = True

        if self.config.options.get("auto_create", True):
            self._create_table()

    def disconnect(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
        self._is_connected = False

    def is_connected(self) -> bool:
        return self._is_connected and self._conn is not None

    def _create_table(self) -> None:
        """Create the records table if it doesn't exist."""
        cursor = self._conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id TEXT PRIMARY KEY,
                meta TEXT,
                payload TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Create indexes
        cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{self.table_name}_created
            ON {self.table_name}(created_at)
        """)

        self._conn.commit()

    # =========================================================================
    # CRUD
    # =========================================================================

    def save(self, record: T) -> str:
        """Save a record."""
        record_id, meta, payload, created_at = self._serialize_record(record)

        cursor = self._conn.cursor()
        cursor.execute(f"""
            INSERT OR REPLACE INTO {self.table_name}
            (id, meta, payload, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (record_id, meta, payload, created_at, datetime.utcnow().isoformat()))

        self._conn.commit()
        return record_id

    def save_many(self, records: List[T]) -> List[str]:
        """Save multiple records in a transaction."""
        cursor = self._conn.cursor()
        ids = []

        for record in records:
            record_id, meta, payload, created_at = self._serialize_record(record)
            cursor.execute(f"""
                INSERT OR REPLACE INTO {self.table_name}
                (id, meta, payload, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (record_id, meta, payload, created_at, datetime.utcnow().isoformat()))
            ids.append(record_id)

        self._conn.commit()
        return ids

    def get(self, id: str) -> Optional[T]:
        """Get a record by ID."""
        cursor = self._conn.cursor()
        cursor.execute(f"""
            SELECT * FROM {self.table_name} WHERE id = ?
        """, (id,))

        row = cursor.fetchone()
        return self._deserialize_row(row) if row else None

    def get_many(self, ids: List[str]) -> List[T]:
        """Get multiple records by IDs."""
        if not ids:
            return []

        placeholders = ",".join("?" * len(ids))
        cursor = self._conn.cursor()
        cursor.execute(f"""
            SELECT * FROM {self.table_name} WHERE id IN ({placeholders})
        """, ids)

        return [self._deserialize_row(row) for row in cursor.fetchall()]

    def update(self, id: str, record: T) -> bool:
        """Update a record."""
        if not self.exists(id):
            return False

        _, meta, payload, _ = self._serialize_record(record)

        cursor = self._conn.cursor()
        cursor.execute(f"""
            UPDATE {self.table_name}
            SET meta = ?, payload = ?, updated_at = ?
            WHERE id = ?
        """, (meta, payload, datetime.utcnow().isoformat(), id))

        self._conn.commit()
        return cursor.rowcount > 0

    def delete(self, id: str) -> bool:
        """Delete a record."""
        cursor = self._conn.cursor()
        cursor.execute(f"""
            DELETE FROM {self.table_name} WHERE id = ?
        """, (id,))

        self._conn.commit()
        return cursor.rowcount > 0

    def delete_many(self, ids: List[str]) -> int:
        """Delete multiple records."""
        if not ids:
            return 0

        placeholders = ",".join("?" * len(ids))
        cursor = self._conn.cursor()
        cursor.execute(f"""
            DELETE FROM {self.table_name} WHERE id IN ({placeholders})
        """, ids)

        self._conn.commit()
        return cursor.rowcount

    # =========================================================================
    # QUERYING
    # =========================================================================

    def find(self, options: QueryOptions) -> List[T]:
        """Find records matching filters."""
        query = f"SELECT * FROM {self.table_name}"
        params = []

        # Build WHERE clause
        if options.filters:
            conditions = []
            for f in options.filters:
                condition, param = self._build_condition(f)
                if condition:
                    conditions.append(condition)
                    if param is not None:
                        params.append(param)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        # ORDER BY
        if options.order_by:
            direction = "DESC" if options.order_dir.lower() == "desc" else "ASC"
            # Handle JSON path for ordering
            if options.order_by.startswith("payload."):
                json_path = "$." + options.order_by[8:]
                query += f" ORDER BY json_extract(payload, '{json_path}') {direction}"
            else:
                query += f" ORDER BY {options.order_by} {direction}"

        # LIMIT and OFFSET
        if options.limit:
            query += f" LIMIT {options.limit}"
        if options.offset:
            query += f" OFFSET {options.offset}"

        cursor = self._conn.cursor()
        cursor.execute(query, params)

        return [self._deserialize_row(row) for row in cursor.fetchall()]

    def find_one(self, options: QueryOptions) -> Optional[T]:
        """Find first matching record."""
        options.limit = 1
        results = self.find(options)
        return results[0] if results else None

    def count(self, options: Optional[QueryOptions] = None) -> int:
        """Count matching records."""
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        params = []

        if options and options.filters:
            conditions = []
            for f in options.filters:
                condition, param = self._build_condition(f)
                if condition:
                    conditions.append(condition)
                    if param is not None:
                        params.append(param)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        cursor = self._conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()[0]

    def exists(self, id: str) -> bool:
        """Check if record exists."""
        cursor = self._conn.cursor()
        cursor.execute(f"""
            SELECT 1 FROM {self.table_name} WHERE id = ? LIMIT 1
        """, (id,))
        return cursor.fetchone() is not None

    def clear(self) -> int:
        """Delete all records."""
        cursor = self._conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
        count = cursor.fetchone()[0]

        cursor.execute(f"DELETE FROM {self.table_name}")
        self._conn.commit()
        return count

    # =========================================================================
    # SERIALIZATION
    # =========================================================================

    def _serialize_record(self, record: T) -> tuple:
        """Serialize record for storage."""
        if hasattr(record, 'id'):
            # DataRecord
            record_id = record.id
            meta = json.dumps(record.meta.to_dict() if hasattr(record.meta, 'to_dict') else {})
            payload = json.dumps(record.payload, default=str)
            created_at = record.created_at if hasattr(record, 'created_at') else datetime.utcnow().isoformat()
        elif isinstance(record, dict):
            record_id = record.get('id', str(id(record)))
            meta = json.dumps(record.get('meta', {}))
            payload = json.dumps(record.get('payload', record), default=str)
            created_at = record.get('created_at', datetime.utcnow().isoformat())
        else:
            import uuid
            record_id = str(uuid.uuid4())
            meta = "{}"
            payload = json.dumps(record, default=str)
            created_at = datetime.utcnow().isoformat()

        return record_id, meta, payload, created_at

    def _deserialize_row(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Deserialize row to record."""
        return {
            "id": row["id"],
            "meta": json.loads(row["meta"]) if row["meta"] else {},
            "payload": json.loads(row["payload"]) if row["payload"] else {},
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def _build_condition(self, filter: QueryFilter) -> tuple:
        """Build SQL condition from filter."""
        field = filter.field
        op = filter.operator.lower()
        value = filter.value

        # Handle JSON payload fields
        if field.startswith("payload."):
            json_path = "$." + field[8:]
            field_expr = f"json_extract(payload, '{json_path}')"
        elif field.startswith("meta."):
            json_path = "$." + field[5:]
            field_expr = f"json_extract(meta, '{json_path}')"
        else:
            field_expr = field

        if op == "eq":
            return f"{field_expr} = ?", value
        elif op == "ne":
            return f"{field_expr} != ?", value
        elif op == "gt":
            return f"{field_expr} > ?", value
        elif op == "gte":
            return f"{field_expr} >= ?", value
        elif op == "lt":
            return f"{field_expr} < ?", value
        elif op == "lte":
            return f"{field_expr} <= ?", value
        elif op == "like":
            return f"{field_expr} LIKE ?", value
        elif op == "in":
            placeholders = ",".join("?" * len(value))
            return f"{field_expr} IN ({placeholders})", None  # Handle multiple params separately
        elif op == "is_null":
            return f"{field_expr} IS NULL" if value else f"{field_expr} IS NOT NULL", None

        return None, None

    # =========================================================================
    # RAW SQL
    # =========================================================================

    def execute_raw(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute raw SQL query."""
        cursor = self._conn.cursor()
        cursor.execute(query, params)

        if query.strip().upper().startswith("SELECT"):
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

        self._conn.commit()
        return []
