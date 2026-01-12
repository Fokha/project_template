"""
Secrets Management Template
===========================
Patterns for secure secrets management.

Use when:
- API keys need secure storage
- Credentials rotation required
- Environment-based secrets
- Audit trail needed

Placeholders:
- {{SECRETS_BACKEND}}: Secrets storage backend
- {{ROTATION_INTERVAL}}: Secret rotation interval
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime, timedelta
import logging
import os
import json
import base64
import hashlib

logger = logging.getLogger(__name__)


class SecretType(Enum):
    API_KEY = "api_key"
    PASSWORD = "password"
    TOKEN = "token"
    CERTIFICATE = "certificate"
    PRIVATE_KEY = "private_key"
    CONNECTION_STRING = "connection_string"


@dataclass
class Secret:
    """A secret value."""
    name: str
    value: str
    secret_type: SecretType
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class SecretAccess:
    """Record of secret access."""
    secret_name: str
    accessor: str
    action: str  # read, write, delete
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    ip_address: Optional[str] = None


class SecretsProvider(ABC):
    """Abstract secrets provider."""

    @abstractmethod
    def get(self, name: str) -> Optional[str]:
        """Get a secret value."""
        pass

    @abstractmethod
    def set(self, secret: Secret) -> bool:
        """Set a secret."""
        pass

    @abstractmethod
    def delete(self, name: str) -> bool:
        """Delete a secret."""
        pass

    @abstractmethod
    def list(self) -> List[str]:
        """List all secret names."""
        pass


class EnvironmentSecretsProvider(SecretsProvider):
    """Environment variable based secrets."""

    def __init__(self, prefix: str = ""):
        self.prefix = prefix

    def get(self, name: str) -> Optional[str]:
        """Get secret from environment."""
        env_name = f"{self.prefix}{name}".upper()
        return os.environ.get(env_name)

    def set(self, secret: Secret) -> bool:
        """Set environment variable (runtime only)."""
        env_name = f"{self.prefix}{secret.name}".upper()
        os.environ[env_name] = secret.value
        return True

    def delete(self, name: str) -> bool:
        """Remove environment variable."""
        env_name = f"{self.prefix}{name}".upper()
        if env_name in os.environ:
            del os.environ[env_name]
            return True
        return False

    def list(self) -> List[str]:
        """List secrets with prefix."""
        prefix_upper = self.prefix.upper()
        return [k for k in os.environ.keys() if k.startswith(prefix_upper)]


class FileSecretsProvider(SecretsProvider):
    """File-based encrypted secrets."""

    def __init__(self, secrets_file: str, encryption_key: Optional[str] = None):
        self.secrets_file = secrets_file
        self.encryption_key = encryption_key
        self._secrets: Dict[str, Secret] = {}
        self._load()

    def get(self, name: str) -> Optional[str]:
        """Get secret value."""
        secret = self._secrets.get(name)
        if secret:
            # Check expiration
            if secret.expires_at and datetime.now() > secret.expires_at:
                logger.warning(f"Secret {name} has expired")
                return None
            return secret.value
        return None

    def set(self, secret: Secret) -> bool:
        """Set a secret."""
        self._secrets[secret.name] = secret
        self._save()
        return True

    def delete(self, name: str) -> bool:
        """Delete a secret."""
        if name in self._secrets:
            del self._secrets[name]
            self._save()
            return True
        return False

    def list(self) -> List[str]:
        """List all secret names."""
        return list(self._secrets.keys())

    def _load(self):
        """Load secrets from file."""
        try:
            if os.path.exists(self.secrets_file):
                with open(self.secrets_file, 'r') as f:
                    data = json.load(f)

                if self.encryption_key:
                    data = self._decrypt(data)

                for name, secret_data in data.items():
                    self._secrets[name] = Secret(
                        name=name,
                        value=secret_data['value'],
                        secret_type=SecretType(secret_data.get('type', 'api_key')),
                        version=secret_data.get('version', 1),
                        metadata=secret_data.get('metadata', {}),
                        tags=secret_data.get('tags', [])
                    )
        except Exception as e:
            logger.error(f"Failed to load secrets: {e}")

    def _save(self):
        """Save secrets to file."""
        try:
            data = {}
            for name, secret in self._secrets.items():
                data[name] = {
                    'value': secret.value,
                    'type': secret.secret_type.value,
                    'version': secret.version,
                    'metadata': secret.metadata,
                    'tags': secret.tags
                }

            if self.encryption_key:
                data = self._encrypt(data)

            with open(self.secrets_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save secrets: {e}")

    def _encrypt(self, data: Dict) -> Dict:
        """Simple encryption (use proper encryption in production)."""
        # This is a placeholder - use proper encryption like Fernet in production
        json_str = json.dumps(data)
        encoded = base64.b64encode(json_str.encode()).decode()
        return {"encrypted": True, "data": encoded}

    def _decrypt(self, data: Dict) -> Dict:
        """Simple decryption."""
        if data.get("encrypted"):
            decoded = base64.b64decode(data["data"]).decode()
            return json.loads(decoded)
        return data


class SecretsManager:
    """
    Manage secrets with audit logging.

    Example:
        manager = SecretsManager(FileSecretsProvider("secrets.json"))

        manager.set_secret(Secret(
            name="API_KEY",
            value="sk-xxx",
            secret_type=SecretType.API_KEY
        ))

        key = manager.get_secret("API_KEY")
    """

    def __init__(self, provider: SecretsProvider, enable_audit: bool = True):
        self.provider = provider
        self.enable_audit = enable_audit
        self.access_log: List[SecretAccess] = []
        self.rotation_callbacks: Dict[str, Callable[[str], str]] = {}

    def get_secret(self, name: str, accessor: str = "system") -> Optional[str]:
        """Get a secret with audit logging."""
        value = self.provider.get(name)

        if self.enable_audit:
            self.access_log.append(SecretAccess(
                secret_name=name,
                accessor=accessor,
                action="read",
                success=value is not None
            ))

        return value

    def set_secret(self, secret: Secret, accessor: str = "system") -> bool:
        """Set a secret with audit logging."""
        result = self.provider.set(secret)

        if self.enable_audit:
            self.access_log.append(SecretAccess(
                secret_name=secret.name,
                accessor=accessor,
                action="write",
                success=result
            ))

        return result

    def delete_secret(self, name: str, accessor: str = "system") -> bool:
        """Delete a secret with audit logging."""
        result = self.provider.delete(name)

        if self.enable_audit:
            self.access_log.append(SecretAccess(
                secret_name=name,
                accessor=accessor,
                action="delete",
                success=result
            ))

        return result

    def list_secrets(self) -> List[str]:
        """List all secret names."""
        return self.provider.list()

    def register_rotation_callback(self, name: str, callback: Callable[[str], str]):
        """Register a callback for secret rotation."""
        self.rotation_callbacks[name] = callback

    def rotate_secret(self, name: str, accessor: str = "system") -> bool:
        """Rotate a secret."""
        if name not in self.rotation_callbacks:
            logger.warning(f"No rotation callback for {name}")
            return False

        current = self.provider.get(name)
        if not current:
            return False

        try:
            new_value = self.rotation_callbacks[name](current)

            # Get current secret metadata
            secrets = getattr(self.provider, '_secrets', {})
            old_secret = secrets.get(name)

            new_secret = Secret(
                name=name,
                value=new_value,
                secret_type=old_secret.secret_type if old_secret else SecretType.API_KEY,
                version=(old_secret.version + 1) if old_secret else 2,
                metadata=old_secret.metadata if old_secret else {}
            )

            result = self.provider.set(new_secret)

            if self.enable_audit:
                self.access_log.append(SecretAccess(
                    secret_name=name,
                    accessor=accessor,
                    action="rotate",
                    success=result
                ))

            logger.info(f"Rotated secret {name} to version {new_secret.version}")
            return result

        except Exception as e:
            logger.error(f"Failed to rotate secret {name}: {e}")
            return False

    def get_audit_log(
        self,
        secret_name: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[SecretAccess]:
        """Get audit log entries."""
        log = self.access_log

        if secret_name:
            log = [a for a in log if a.secret_name == secret_name]

        if since:
            log = [a for a in log if a.timestamp >= since]

        return log


class SecretValidator:
    """Validate secret values."""

    @staticmethod
    def validate_api_key(value: str) -> bool:
        """Validate API key format."""
        # Basic validation - customize for specific APIs
        return len(value) >= 20 and value.isalnum()

    @staticmethod
    def validate_password(value: str, min_length: int = 12) -> Dict[str, Any]:
        """Validate password strength."""
        issues = []

        if len(value) < min_length:
            issues.append(f"Must be at least {min_length} characters")
        if not any(c.isupper() for c in value):
            issues.append("Must contain uppercase letter")
        if not any(c.islower() for c in value):
            issues.append("Must contain lowercase letter")
        if not any(c.isdigit() for c in value):
            issues.append("Must contain digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in value):
            issues.append("Must contain special character")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "strength": max(0, 100 - len(issues) * 20)
        }

    @staticmethod
    def validate_connection_string(value: str) -> bool:
        """Validate connection string format."""
        required_parts = ["host", "port", "database"]
        return all(part in value.lower() for part in required_parts)


def create_trading_secrets_manager(secrets_path: str) -> SecretsManager:
    """Create secrets manager for trading system."""
    provider = FileSecretsProvider(secrets_path)
    manager = SecretsManager(provider, enable_audit=True)

    # Register rotation callbacks
    def rotate_api_key(current: str) -> str:
        # In real implementation, would call API to generate new key
        import secrets
        return f"sk-{secrets.token_hex(16)}"

    manager.register_rotation_callback("TRADING_API_KEY", rotate_api_key)
    manager.register_rotation_callback("ML_API_KEY", rotate_api_key)

    return manager


# Example usage
if __name__ == "__main__":
    import tempfile

    # Create temp secrets file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        secrets_file = f.name

    # Create manager
    manager = create_trading_secrets_manager(secrets_file)

    # Set some secrets
    manager.set_secret(Secret(
        name="TRADING_API_KEY",
        value="sk-12345678901234567890",
        secret_type=SecretType.API_KEY,
        tags=["production", "trading"]
    ))

    manager.set_secret(Secret(
        name="DB_PASSWORD",
        value="SuperSecure123!@#",
        secret_type=SecretType.PASSWORD
    ))

    # Get secrets
    print("Secrets:")
    print("-" * 50)
    for name in manager.list_secrets():
        value = manager.get_secret(name, accessor="demo")
        masked = value[:4] + "****" if value else "None"
        print(f"  {name}: {masked}")

    # Validate password
    print("\nPassword Validation:")
    result = SecretValidator.validate_password("weak")
    print(f"  'weak': {result}")

    result = SecretValidator.validate_password("SuperSecure123!@#")
    print(f"  'SuperSecure123!@#': {result}")

    # Show audit log
    print("\nAudit Log:")
    for access in manager.get_audit_log():
        print(f"  {access.timestamp}: {access.accessor} {access.action} {access.secret_name}")

    # Cleanup
    os.unlink(secrets_file)
