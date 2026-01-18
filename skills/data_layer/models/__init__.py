# fokha_data/models/__init__.py
# =============================================================================
# TEMPLATE: Data Models Package
# =============================================================================
# This package contains all data model definitions for the fokha_data layer.
# Models are organized by domain and include classification metadata.
#
# USAGE:
#   from fokha_data.models import DataRecord, DataMeta, DataSource, Validity
#   from fokha_data.models.market import MarketData, OHLCV
#   from fokha_data.models.signal import SignalData
# =============================================================================

from .enums import (
    DataSource,
    Validity,
    Intensity,
    Origin,
    GenerationMode,
    SchemaType,
)

from .base import (
    DataMeta,
    DataRecord,
    GenerationConfig,
    QualityScore,
)

# Domain-specific models (uncomment as needed)
# from .market import MarketData, OHLCV, Tick
# from .signal import SignalData, Prediction
# from .user import UserData, Preferences

__all__ = [
    # Enums
    "DataSource",
    "Validity",
    "Intensity",
    "Origin",
    "GenerationMode",
    "SchemaType",
    # Base Classes
    "DataMeta",
    "DataRecord",
    "GenerationConfig",
    "QualityScore",
]
