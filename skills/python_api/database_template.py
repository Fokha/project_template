# ═══════════════════════════════════════════════════════════════
# DATABASE TEMPLATE
# SQLite CRUD operations with connection pooling and migrations
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Define your tables in SCHEMA
# 3. Use DatabaseManager for all DB operations
#
# ═══════════════════════════════════════════════════════════════

import sqlite3
import logging
import threading
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from contextlib import contextmanager
from pathlib import Path
import json

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DATABASE CONFIGURATION
# ═══════════════════════════════════════════════════════════════


@dataclass
class DatabaseConfig:
    """Database configuration."""
    db_path: str = "data/app.db"
    timeout: float = 30.0
    check_same_thread: bool = False
    isolation_level: str = None  # Autocommit mode


# ═══════════════════════════════════════════════════════════════
# CONNECTION POOL
# ═══════════════════════════════════════════════════════════════


class ConnectionPool:
    """Thread-safe SQLite connection pool."""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._local = threading.local()
        self._lock = threading.Lock()

        # Ensure directory exists
        Path(config.db_path).parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Get connection for current thread."""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = self._create_connection()
        return self._local.connection

    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection."""
        conn = sqlite3.connect(
            self.config.db_path,
            timeout=self.config.timeout,
            check_same_thread=self.config.check_same_thread,
            isolation_level=self.config.isolation_level,
        )

        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")

        # Return rows as dictionaries
        conn.row_factory = sqlite3.Row

        return conn

    def close(self):
        """Close connection for current thread."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None


# ═══════════════════════════════════════════════════════════════
# DATABASE MANAGER
# ═══════════════════════════════════════════════════════════════


class DatabaseManager:
    """
    SQLite database manager with CRUD operations.

    Features:
    - Thread-safe connection pooling
    - Automatic schema migrations
    - Transaction support
    - Query builder helpers
    """

    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self.pool = ConnectionPool(self.config)
        self._schema_version = 0

    @property
    def conn(self) -> sqlite3.Connection:
        """Get current thread's connection."""
        return self.pool.get_connection()

    @contextmanager
    def transaction(self):
        """Context manager for transactions."""
        conn = self.conn
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    # ═══════════════════════════════════════════════════════════
    # SCHEMA MANAGEMENT
    # ═══════════════════════════════════════════════════════════

    def initialize_schema(self, schema: str):
        """Initialize database schema."""
        with self.transaction() as conn:
            conn.executescript(schema)
        logger.info(f"Database schema initialized: {self.config.db_path}")

    def migrate(self, migrations: List[Tuple[int, str]]):
        """
        Run database migrations.

        Args:
            migrations: List of (version, sql) tuples
        """
        # Create migrations table if not exists
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS _migrations (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL
            )
        """)

        # Get current version
        result = self.conn.execute(
            "SELECT MAX(version) FROM _migrations"
        ).fetchone()
        current_version = result[0] or 0

        # Apply pending migrations
        for version, sql in sorted(migrations):
            if version > current_version:
                logger.info(f"Applying migration {version}")
                with self.transaction() as conn:
                    conn.executescript(sql)
                    conn.execute(
                        "INSERT INTO _migrations (version, applied_at) VALUES (?, ?)",
                        (version, datetime.utcnow().isoformat())
                    )

        logger.info(f"Migrations complete. Version: {version if migrations else current_version}")

    # ═══════════════════════════════════════════════════════════
    # CRUD OPERATIONS
    # ═══════════════════════════════════════════════════════════

    def insert(
        self,
        table: str,
        data: Dict[str, Any],
        returning: str = "id"
    ) -> Any:
        """
        Insert a row into a table.

        Args:
            table: Table name
            data: Column-value dictionary
            returning: Column to return (default: id)

        Returns:
            Value of returning column (usually inserted ID)
        """
        columns = list(data.keys())
        placeholders = ", ".join(["?" for _ in columns])
        column_names = ", ".join(columns)

        sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"

        with self.transaction() as conn:
            cursor = conn.execute(sql, list(data.values()))
            return cursor.lastrowid

    def insert_many(self, table: str, rows: List[Dict[str, Any]]) -> int:
        """
        Insert multiple rows.

        Returns:
            Number of rows inserted
        """
        if not rows:
            return 0

        columns = list(rows[0].keys())
        placeholders = ", ".join(["?" for _ in columns])
        column_names = ", ".join(columns)

        sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"

        with self.transaction() as conn:
            cursor = conn.executemany(sql, [list(r.values()) for r in rows])
            return cursor.rowcount

    def select(
        self,
        table: str,
        columns: List[str] = None,
        where: Dict[str, Any] = None,
        order_by: str = None,
        limit: int = None,
        offset: int = None
    ) -> List[Dict]:
        """
        Select rows from a table.

        Args:
            table: Table name
            columns: Columns to select (default: all)
            where: Filter conditions (column=value)
            order_by: Order by clause
            limit: Max rows to return
            offset: Rows to skip

        Returns:
            List of row dictionaries
        """
        col_str = ", ".join(columns) if columns else "*"
        sql = f"SELECT {col_str} FROM {table}"
        params = []

        if where:
            conditions = [f"{k} = ?" for k in where.keys()]
            sql += " WHERE " + " AND ".join(conditions)
            params.extend(where.values())

        if order_by:
            sql += f" ORDER BY {order_by}"

        if limit:
            sql += f" LIMIT {limit}"

        if offset:
            sql += f" OFFSET {offset}"

        cursor = self.conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def select_one(
        self,
        table: str,
        columns: List[str] = None,
        where: Dict[str, Any] = None
    ) -> Optional[Dict]:
        """Select a single row."""
        rows = self.select(table, columns, where, limit=1)
        return rows[0] if rows else None

    def update(
        self,
        table: str,
        data: Dict[str, Any],
        where: Dict[str, Any]
    ) -> int:
        """
        Update rows in a table.

        Returns:
            Number of rows updated
        """
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        where_clause = " AND ".join([f"{k} = ?" for k in where.keys()])

        sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        params = list(data.values()) + list(where.values())

        with self.transaction() as conn:
            cursor = conn.execute(sql, params)
            return cursor.rowcount

    def delete(self, table: str, where: Dict[str, Any]) -> int:
        """
        Delete rows from a table.

        Returns:
            Number of rows deleted
        """
        where_clause = " AND ".join([f"{k} = ?" for k in where.keys()])
        sql = f"DELETE FROM {table} WHERE {where_clause}"

        with self.transaction() as conn:
            cursor = conn.execute(sql, list(where.values()))
            return cursor.rowcount

    def execute(self, sql: str, params: Tuple = None) -> sqlite3.Cursor:
        """Execute raw SQL."""
        return self.conn.execute(sql, params or ())

    def count(self, table: str, where: Dict[str, Any] = None) -> int:
        """Count rows in a table."""
        sql = f"SELECT COUNT(*) FROM {table}"
        params = []

        if where:
            conditions = [f"{k} = ?" for k in where.keys()]
            sql += " WHERE " + " AND ".join(conditions)
            params.extend(where.values())

        result = self.conn.execute(sql, params).fetchone()
        return result[0]

    def exists(self, table: str, where: Dict[str, Any]) -> bool:
        """Check if a row exists."""
        return self.count(table, where) > 0

    # ═══════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════════

    def get_tables(self) -> List[str]:
        """Get list of tables in database."""
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        return [row[0] for row in cursor.fetchall()]

    def get_columns(self, table: str) -> List[Dict]:
        """Get column info for a table."""
        cursor = self.conn.execute(f"PRAGMA table_info({table})")
        return [
            {
                "name": row[1],
                "type": row[2],
                "nullable": not row[3],
                "default": row[4],
                "primary_key": bool(row[5]),
            }
            for row in cursor.fetchall()
        ]

    def vacuum(self):
        """Optimize database file size."""
        self.conn.execute("VACUUM")
        logger.info("Database vacuumed")

    def backup(self, backup_path: str):
        """Create database backup."""
        import shutil
        shutil.copy2(self.config.db_path, backup_path)
        logger.info(f"Database backed up to: {backup_path}")


# ═══════════════════════════════════════════════════════════════
# BASE MODEL CLASS
# ═══════════════════════════════════════════════════════════════


class BaseModel:
    """
    Base class for database models.

    Provides ORM-like interface for database operations.
    """

    _table: str = None  # Override in subclass
    _db: DatabaseManager = None  # Set via set_database()

    @classmethod
    def set_database(cls, db: DatabaseManager):
        """Set database manager for all models."""
        cls._db = db

    @classmethod
    def create(cls, **kwargs) -> 'BaseModel':
        """Create and save a new record."""
        kwargs['created_at'] = datetime.utcnow().isoformat()
        kwargs['updated_at'] = kwargs['created_at']

        id = cls._db.insert(cls._table, kwargs)
        kwargs['id'] = id
        return cls(**kwargs)

    @classmethod
    def find(cls, id: int) -> Optional['BaseModel']:
        """Find record by ID."""
        row = cls._db.select_one(cls._table, where={"id": id})
        return cls(**row) if row else None

    @classmethod
    def find_by(cls, **kwargs) -> Optional['BaseModel']:
        """Find record by attributes."""
        row = cls._db.select_one(cls._table, where=kwargs)
        return cls(**row) if row else None

    @classmethod
    def all(cls, limit: int = None, offset: int = None) -> List['BaseModel']:
        """Get all records."""
        rows = cls._db.select(cls._table, limit=limit, offset=offset)
        return [cls(**row) for row in rows]

    @classmethod
    def where(cls, **kwargs) -> List['BaseModel']:
        """Find records matching conditions."""
        rows = cls._db.select(cls._table, where=kwargs)
        return [cls(**row) for row in rows]

    @classmethod
    def count(cls, **kwargs) -> int:
        """Count records."""
        return cls._db.count(cls._table, where=kwargs if kwargs else None)

    def save(self) -> 'BaseModel':
        """Save record to database."""
        data = self.to_dict()
        data['updated_at'] = datetime.utcnow().isoformat()

        if hasattr(self, 'id') and self.id:
            self._db.update(self._table, data, {"id": self.id})
        else:
            data['created_at'] = data['updated_at']
            self.id = self._db.insert(self._table, data)

        return self

    def delete(self) -> bool:
        """Delete record from database."""
        if hasattr(self, 'id') and self.id:
            return self._db.delete(self._table, {"id": self.id}) > 0
        return False

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


# Example schema
EXAMPLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id);
"""


# Example model
class User(BaseModel):
    _table = "users"

    def __init__(self, id=None, email=None, name=None, created_at=None, updated_at=None):
        self.id = id
        self.email = email
        self.name = name
        self.created_at = created_at
        self.updated_at = updated_at


if __name__ == "__main__":
    # Initialize database
    config = DatabaseConfig(db_path="test_db.db")
    db = DatabaseManager(config)
    db.initialize_schema(EXAMPLE_SCHEMA)

    # Set database for models
    BaseModel.set_database(db)

    print("=" * 60)
    print("DATABASE TEMPLATE DEMO")
    print("=" * 60)

    # CRUD with DatabaseManager
    print("\n--- Direct CRUD ---")

    # Insert
    user_id = db.insert("users", {
        "email": "test@example.com",
        "name": "Test User",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    })
    print(f"Inserted user ID: {user_id}")

    # Select
    users = db.select("users", where={"id": user_id})
    print(f"Selected users: {users}")

    # Update
    updated = db.update("users", {"name": "Updated User"}, {"id": user_id})
    print(f"Updated rows: {updated}")

    # Count
    count = db.count("users")
    print(f"Total users: {count}")

    # ORM-style with BaseModel
    print("\n--- ORM-style ---")

    # Create
    user = User.create(email="orm@example.com", name="ORM User")
    print(f"Created user: {user.to_dict()}")

    # Find
    found = User.find(user.id)
    print(f"Found user: {found.to_dict()}")

    # Update
    found.name = "Modified User"
    found.save()
    print(f"Updated user: {found.to_dict()}")

    # Count
    print(f"Total users: {User.count()}")

    # Cleanup
    import os
    os.remove("test_db.db")
    print("\nTest database cleaned up.")
