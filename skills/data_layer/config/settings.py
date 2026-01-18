# fokha_data/config/settings.py
# =============================================================================
# TEMPLATE: Global Settings
# =============================================================================
# Centralized configuration for the fokha_data package.
# Override these settings in your project's configuration.
# =============================================================================

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path


@dataclass
class FokhaDataSettings:
    """
    Global settings for fokha_data.

    These can be overridden by:
    1. Creating an instance with custom values
    2. Environment variables (FOKHA_DATA_*)
    3. Config file
    """

    # ==========================================================================
    # General
    # ==========================================================================
    debug: bool = False
    log_level: str = "INFO"

    # ==========================================================================
    # Models
    # ==========================================================================
    default_version: str = "1.0.0"
    auto_generate_ids: bool = True
    id_prefix: str = ""

    # ==========================================================================
    # Factory
    # ==========================================================================
    templates_dir: Optional[str] = None
    default_seed: Optional[int] = None
    cache_templates: bool = True

    # ==========================================================================
    # Processors
    # ==========================================================================
    validation_strict_mode: bool = False
    format_dates_as_iso: bool = True
    default_date_format: str = "%Y-%m-%dT%H:%M:%SZ"

    # ==========================================================================
    # Storage
    # ==========================================================================
    default_storage_type: str = "memory"  # memory, sqlite, file
    sqlite_db_path: str = "fokha_data.db"
    auto_create_tables: bool = True
    batch_size: int = 100

    # ==========================================================================
    # Pipeline
    # ==========================================================================
    pipeline_stop_on_failure: bool = True
    pipeline_timeout_ms: int = 300000  # 5 minutes
    collect_metrics: bool = True

    # ==========================================================================
    # Methods
    # ==========================================================================

    def get_templates_path(self) -> Path:
        """Get the templates directory path."""
        if self.templates_dir:
            return Path(self.templates_dir)
        # Default to package templates
        return Path(__file__).parent.parent / "factory" / "templates"

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "debug": self.debug,
            "log_level": self.log_level,
            "default_version": self.default_version,
            "auto_generate_ids": self.auto_generate_ids,
            "default_storage_type": self.default_storage_type,
            "pipeline_stop_on_failure": self.pipeline_stop_on_failure,
            "collect_metrics": self.collect_metrics,
        }

    @classmethod
    def from_env(cls) -> "FokhaDataSettings":
        """Load settings from environment variables."""
        import os

        return cls(
            debug=os.getenv("FOKHA_DATA_DEBUG", "false").lower() == "true",
            log_level=os.getenv("FOKHA_DATA_LOG_LEVEL", "INFO"),
            templates_dir=os.getenv("FOKHA_DATA_TEMPLATES_DIR"),
            sqlite_db_path=os.getenv("FOKHA_DATA_SQLITE_PATH", "fokha_data.db"),
        )


# Global settings instance
settings = FokhaDataSettings()


def configure(**kwargs) -> FokhaDataSettings:
    """
    Configure global settings.

    Usage:
        from fokha_data.config import configure

        configure(
            debug=True,
            sqlite_db_path="my_data.db",
        )
    """
    global settings
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    return settings


def get_settings() -> FokhaDataSettings:
    """Get current settings."""
    return settings
