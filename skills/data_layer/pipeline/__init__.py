# fokha_data/pipeline/__init__.py
# =============================================================================
# TEMPLATE: Data Pipeline Package
# =============================================================================
# Orchestrates the complete data flow from request to output.
# Composes processors, storage, and stages into a coherent pipeline.
#
# Components:
#   - Pipeline: Main orchestrator
#   - Stage: Individual pipeline step
#   - Requester: Data fetching
#   - Gatherer: Data collection
#
# USAGE:
#   from fokha_data.pipeline import Pipeline, Stage
#
#   pipeline = Pipeline()
#   pipeline.add_stage(Stage("validate", validator.validate))
#   pipeline.add_stage(Stage("format", formatter.format))
#   pipeline.add_stage(Stage("store", storage.save))
#
#   result = pipeline.execute(data)
# =============================================================================

from .orchestrator import Pipeline, PipelineConfig, PipelineResult
from .stages.base_stage import Stage, StageResult, StageStatus
from .requester import Requester, RequestConfig
from .gatherer import Gatherer, GatherConfig

__all__ = [
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
