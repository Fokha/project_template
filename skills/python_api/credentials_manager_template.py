"""
Credentials Manager Template
============================

Secure credential storage and retrieval using encryption.

Usage:
    from services.credentials_manager import CredentialsManager

    creds = CredentialsManager()
    creds.store('api_key', 'secret_value')
    value = creds.get('api_key')

Features:
- Fernet symmetric encryption
- SQLite storage with encrypted values
- Environment variable fallback
- Automatic key generation
"""

import os
import sqlite3
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Optional: pip install cryptography
try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class CredentialsManager:
    """Secure credential storage with encryption."""

    def __init__(self, db_path: str = "data/credentials.db", key_path: str = "data/.credential_key"):
        self.db_path = db_path
        self.key_path = key_path
        self.fernet: Optional[Any] = None

        # Ensure directories exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        Path(key_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize encryption
        if CRYPTO_AVAILABLE:
            self._init_encryption()

        # Initialize database
        self._init_db()

    def _init_encryption(self):
        """Initialize or load encryption key."""
        if os.path.exists(self.key_path):
            with open(self.key_path, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_path, 'wb') as f:
                f.write(key)
            os.chmod(self.key_path, 0o600)  # Secure permissions

        self.fernet = Fernet(key)

    def _init_db(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credentials (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                encrypted BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credential_access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                credential_key TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def _encrypt(self, value: str) -> str:
        """Encrypt a value."""
        if self.fernet and CRYPTO_AVAILABLE:
            return self.fernet.encrypt(value.encode()).decode()
        return value  # Fallback: no encryption

    def _decrypt(self, value: str) -> str:
        """Decrypt a value."""
        if self.fernet and CRYPTO_AVAILABLE:
            try:
                return self.fernet.decrypt(value.encode()).decode()
            except Exception:
                return value  # Already decrypted or invalid
        return value

    def store(self, key: str, value: str, encrypt: bool = True) -> bool:
        """Store a credential securely."""
        try:
            stored_value = self._encrypt(value) if encrypt else value

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO credentials (key, value, encrypted, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (key, stored_value, encrypt, datetime.now()))

            # Log access
            cursor.execute('''
                INSERT INTO credential_access_log (credential_key, action)
                VALUES (?, 'STORE')
            ''', (key,))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error storing credential: {e}")
            return False

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve a credential."""
        # First check environment variables
        env_key = key.upper().replace('.', '_').replace('-', '_')
        env_value = os.environ.get(env_key)
        if env_value:
            return env_value

        # Then check database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT value, encrypted FROM credentials WHERE key = ?
            ''', (key,))

            row = cursor.fetchone()

            if row:
                value, encrypted = row

                # Log access
                cursor.execute('''
                    INSERT INTO credential_access_log (credential_key, action)
                    VALUES (?, 'READ')
                ''', (key,))
                conn.commit()

                conn.close()
                return self._decrypt(value) if encrypted else value

            conn.close()
        except Exception as e:
            print(f"Error retrieving credential: {e}")

        return default

    def delete(self, key: str) -> bool:
        """Delete a credential."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('DELETE FROM credentials WHERE key = ?', (key,))

            # Log access
            cursor.execute('''
                INSERT INTO credential_access_log (credential_key, action)
                VALUES (?, 'DELETE')
            ''', (key,))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting credential: {e}")
            return False

    def list_keys(self) -> list:
        """List all credential keys (not values)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT key FROM credentials')
            keys = [row[0] for row in cursor.fetchall()]

            conn.close()
            return keys
        except Exception:
            return []

    def exists(self, key: str) -> bool:
        """Check if a credential exists."""
        return key in self.list_keys() or os.environ.get(key.upper().replace('.', '_'))

    def get_access_log(self, key: Optional[str] = None, limit: int = 100) -> list:
        """Get credential access log."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if key:
                cursor.execute('''
                    SELECT credential_key, action, timestamp
                    FROM credential_access_log
                    WHERE credential_key = ?
                    ORDER BY timestamp DESC LIMIT ?
                ''', (key, limit))
            else:
                cursor.execute('''
                    SELECT credential_key, action, timestamp
                    FROM credential_access_log
                    ORDER BY timestamp DESC LIMIT ?
                ''', (limit,))

            logs = [{'key': r[0], 'action': r[1], 'timestamp': r[2]} for r in cursor.fetchall()]
            conn.close()
            return logs
        except Exception:
            return []


# Convenience functions
_manager: Optional[CredentialsManager] = None

def get_manager() -> CredentialsManager:
    """Get singleton credentials manager."""
    global _manager
    if _manager is None:
        _manager = CredentialsManager()
    return _manager

def get_credential(key: str, default: Optional[str] = None) -> Optional[str]:
    """Quick access to get a credential."""
    return get_manager().get(key, default)

def set_credential(key: str, value: str) -> bool:
    """Quick access to set a credential."""
    return get_manager().store(key, value)


# Example usage
if __name__ == "__main__":
    creds = CredentialsManager()

    # Store credentials
    creds.store("api_key", "sk-1234567890")
    creds.store("database_url", "postgresql://user:pass@localhost/db")

    # Retrieve credentials
    api_key = creds.get("api_key")
    print(f"API Key: {api_key[:10]}...")

    # List all keys
    print(f"Stored keys: {creds.list_keys()}")

    # Check access log
    print(f"Access log: {creds.get_access_log(limit=5)}")
