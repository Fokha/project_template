# fokha_data/__init__.py
# =============================================================================
# FOKHA_DATA - Unified Data Layer Template
# =============================================================================
# Version: 1.0.0
# Author: Fokha Technologies
#
# A comprehensive data layer template for building consistent, testable,
# and maintainable data pipelines across all Fokha projects.
#
# COMPONENTS:
# -----------
# models/     - Data models with classification (DataRecord, DataMeta)
# factory/    - Test data generation (static/dynamic generators)
# processors/ - Data transformation (validator, formatter, sorter, transformer)
# unifiers/   - Data consolidation (merger, normalizer, deduplicator)
# storage/    - Persistence layer (memory, file, SQLite)
# pipeline/   - Orchestration (stages, pipeline, requester, gatherer)
# contracts/  - JSON schemas for data validation
#
# QUICK START:
# ------------
#   from fokha_data.models import DataRecord, DataMeta, DataSource, Validity
#   from fokha_data.factory import DataFactory
#   from fokha_data.processors import Validator, Formatter
#   from fokha_data.storage import MemoryStorage, SQLiteStorage
#   from fokha_data.pipeline import Pipeline, Stage
#
# EXAMPLE:
# --------
#   # Create a data record
#   record = DataRecord(
#       meta=DataMeta(source=DataSource.LIVE, validity=Validity.VALID),
#       payload={"symbol": "AAPL", "price": 150.0}
#   )
#
#   # Generate test data
#   factory = DataFactory()
#   test_records = factory.generate(count=10, source=DataSource.MOCK)
#
#   # Build a pipeline
#   pipeline = (Pipeline("my_pipeline")
#       .add_stage(Stage("validate", validator.validate))
#       .add_stage(Stage("format", formatter.format))
#       .add_stage(Stage("store", storage.save)))
#
#   result = pipeline.execute(record)
# =============================================================================

__version__ = "1.0.0"
__author__ = "Fokha Technologies"

# Models
from .models import (
    DataSource,
    Validity,
    Intensity,
    Origin,
    GenerationMode,
    SchemaType,
    DataMeta,
    DataRecord,
    GenerationConfig,
    QualityScore,
)

# Factory
from .factory import (
    DataFactory,
    StaticGenerator,
    DynamicGenerator,
)

# Processors
from .processors import (
    Validator,
    ValidationResult,
    ValidationRule,
    Formatter,
    FormatConfig,
    Sorter,
    SortConfig,
    Transformer,
    TransformConfig,
)

# Unifiers
from .unifiers import (
    Merger,
    MergeConfig,
    Normalizer,
    NormalizeConfig,
    Deduplicator,
    DedupeConfig,
)

# Storage
from .storage import (
    BaseStorage,
    StorageConfig,
    MemoryStorage,
    FileStorage,
    JSONStorage,
    CSVStorage,
    SQLiteStorage,
    BaseRepository,
)

# Pipeline
from .pipeline import (
    Pipeline,
    PipelineConfig,
    PipelineResult,
    Stage,
    StageResult,
    StageStatus,
    Requester,
    RequestConfig,
    Gatherer,
    GatherConfig,
)

__all__ = [
    # Version
    "__version__",
    "__author__",
    # Enums
    "DataSource",
    "Validity",
    "Intensity",
    "Origin",
    "GenerationMode",
    "SchemaType",
    # Models
    "DataMeta",
    "DataRecord",
    "GenerationConfig",
    "QualityScore",
    # Factory
    "DataFactory",
    "StaticGenerator",
    "DynamicGenerator",
    # Processors
    "Validator",
    "ValidationResult",
    "ValidationRule",
    "Formatter",
    "FormatConfig",
    "Sorter",
    "SortConfig",
    "Transformer",
    "TransformConfig",
    # Unifiers
    "Merger",
    "MergeConfig",
    "Normalizer",
    "NormalizeConfig",
    "Deduplicator",
    "DedupeConfig",
    # Storage
    "BaseStorage",
    "StorageConfig",
    "MemoryStorage",
    "FileStorage",
    "JSONStorage",
    "CSVStorage",
    "SQLiteStorage",
    "BaseRepository",
    # Pipeline
    "Pipeline",
    "PipelineConfig",
    "PipelineResult",
    "Stage",
    "StageResult",
    "StageStatus",
    "Requester",
    "RequestConfig",
    "Gatherer",
    "GatherConfig",
]
