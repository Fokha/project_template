# fokha_data/pipeline/orchestrator.py
# =============================================================================
# TEMPLATE: Pipeline Orchestrator
# =============================================================================
# Main pipeline class that orchestrates data flow through stages.
# =============================================================================

from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict, Callable
from datetime import datetime
from enum import Enum

from .stages.base_stage import Stage, StageResult, StageStatus


class PipelineMode(Enum):
    """Pipeline execution mode."""
    SEQUENTIAL = "sequential"  # Stop on first failure
    BEST_EFFORT = "best_effort"  # Continue on failure
    PARALLEL = "parallel"  # Execute stages in parallel (where possible)


@dataclass
class PipelineConfig:
    """
    Configuration for pipeline execution.

    Attributes:
        mode: Execution mode
        stop_on_failure: Whether to stop on first stage failure
        collect_metrics: Whether to collect execution metrics
        timeout_ms: Overall pipeline timeout
    """
    mode: PipelineMode = PipelineMode.SEQUENTIAL
    stop_on_failure: bool = True
    collect_metrics: bool = True
    timeout_ms: Optional[int] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineResult:
    """
    Result of pipeline execution.

    Attributes:
        success: Whether pipeline completed successfully
        data: Final output data
        stage_results: Results from each stage
        total_duration_ms: Total execution time
        error: Error message if failed
    """
    success: bool
    data: Any = None
    stage_results: Dict[str, StageResult] = field(default_factory=dict)
    total_duration_ms: float = 0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def failed_stages(self) -> List[str]:
        """Get names of failed stages."""
        return [name for name, result in self.stage_results.items() if result.is_failed]

    @property
    def successful_stages(self) -> List[str]:
        """Get names of successful stages."""
        return [name for name, result in self.stage_results.items() if result.is_success]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "total_duration_ms": self.total_duration_ms,
            "error": self.error,
            "stage_results": {name: r.to_dict() for name, r in self.stage_results.items()},
            "metadata": self.metadata,
        }


class Pipeline:
    """
    Data pipeline orchestrator.

    Manages the flow of data through a series of stages,
    handling errors, retries, and collecting metrics.

    Usage:
        # Create pipeline
        pipeline = Pipeline("data_processing")

        # Add stages
        pipeline.add_stage(Stage("validate", validator.validate))
        pipeline.add_stage(Stage("transform", transformer.transform))
        pipeline.add_stage(Stage("store", storage.save))

        # Execute
        result = pipeline.execute(input_data)

        if result.success:
            print(f"Processed in {result.total_duration_ms}ms")
        else:
            print(f"Failed at: {result.failed_stages}")

        # Fluent API
        result = (Pipeline("my_pipeline")
            .add_stage(Stage("step1", func1))
            .add_stage(Stage("step2", func2))
            .execute(data))
    """

    def __init__(
        self,
        name: str = "pipeline",
        config: Optional[PipelineConfig] = None,
    ):
        self.name = name
        self.config = config or PipelineConfig()
        self.stages: List[Stage] = []

        # Hooks
        self._before_pipeline: List[Callable[[Any], Any]] = []
        self._after_pipeline: List[Callable[[PipelineResult], None]] = []
        self._before_stage: List[Callable[[str, Any], Any]] = []
        self._after_stage: List[Callable[[str, StageResult], None]] = []

        # State
        self._execution_count = 0
        self._last_result: Optional[PipelineResult] = None

    # =========================================================================
    # CONFIGURATION
    # =========================================================================

    def add_stage(self, stage: Stage) -> "Pipeline":
        """Add a stage to the pipeline."""
        self.stages.append(stage)
        return self

    def add_stages(self, *stages: Stage) -> "Pipeline":
        """Add multiple stages."""
        self.stages.extend(stages)
        return self

    def insert_stage(self, index: int, stage: Stage) -> "Pipeline":
        """Insert a stage at a specific position."""
        self.stages.insert(index, stage)
        return self

    def remove_stage(self, name: str) -> "Pipeline":
        """Remove a stage by name."""
        self.stages = [s for s in self.stages if s.name != name]
        return self

    def clear_stages(self) -> "Pipeline":
        """Remove all stages."""
        self.stages = []
        return self

    # =========================================================================
    # HOOKS
    # =========================================================================

    def on_before_pipeline(self, hook: Callable[[Any], Any]) -> "Pipeline":
        """Register a before-pipeline hook."""
        self._before_pipeline.append(hook)
        return self

    def on_after_pipeline(self, hook: Callable[[PipelineResult], None]) -> "Pipeline":
        """Register an after-pipeline hook."""
        self._after_pipeline.append(hook)
        return self

    def on_before_stage(self, hook: Callable[[str, Any], Any]) -> "Pipeline":
        """Register a before-stage hook."""
        self._before_stage.append(hook)
        return self

    def on_after_stage(self, hook: Callable[[str, StageResult], None]) -> "Pipeline":
        """Register an after-stage hook."""
        self._after_stage.append(hook)
        return self

    # =========================================================================
    # EXECUTION
    # =========================================================================

    def execute(self, data: Any) -> PipelineResult:
        """
        Execute the pipeline with the given data.

        Args:
            data: Input data to process

        Returns:
            PipelineResult with status and output
        """
        start_time = datetime.utcnow()
        self._execution_count += 1

        stage_results: Dict[str, StageResult] = {}
        current_data = data

        # Before pipeline hooks
        for hook in self._before_pipeline:
            current_data = hook(current_data)

        # Execute stages
        for stage in self.stages:
            # Before stage hooks
            for hook in self._before_stage:
                current_data = hook(stage.name, current_data)

            # Execute stage
            result = stage.execute(current_data)
            stage_results[stage.name] = result

            # After stage hooks
            for hook in self._after_stage:
                hook(stage.name, result)

            # Handle failure
            if result.is_failed:
                if self.config.stop_on_failure:
                    total_duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                    pipeline_result = PipelineResult(
                        success=False,
                        data=current_data,
                        stage_results=stage_results,
                        total_duration_ms=total_duration,
                        error=f"Stage '{stage.name}' failed: {result.error}",
                    )
                    self._last_result = pipeline_result

                    # After pipeline hooks
                    for hook in self._after_pipeline:
                        hook(pipeline_result)

                    return pipeline_result

            # Update data for next stage (unless skipped/failed)
            if result.is_success:
                current_data = result.data

        # Success
        total_duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        pipeline_result = PipelineResult(
            success=True,
            data=current_data,
            stage_results=stage_results,
            total_duration_ms=total_duration,
        )
        self._last_result = pipeline_result

        # After pipeline hooks
        for hook in self._after_pipeline:
            hook(pipeline_result)

        return pipeline_result

    def execute_from(self, stage_name: str, data: Any) -> PipelineResult:
        """
        Execute pipeline starting from a specific stage.

        Useful for resuming after failure.

        Args:
            stage_name: Name of stage to start from
            data: Input data

        Returns:
            PipelineResult
        """
        # Find stage index
        start_index = None
        for i, stage in enumerate(self.stages):
            if stage.name == stage_name:
                start_index = i
                break

        if start_index is None:
            return PipelineResult(
                success=False,
                error=f"Stage not found: {stage_name}",
            )

        # Create temporary pipeline with remaining stages
        temp_pipeline = Pipeline(f"{self.name}_from_{stage_name}", self.config)
        temp_pipeline.stages = self.stages[start_index:]

        return temp_pipeline.execute(data)

    def dry_run(self, data: Any) -> Dict[str, Any]:
        """
        Simulate pipeline execution without actually running.

        Returns information about what would happen.

        Args:
            data: Input data

        Returns:
            Dictionary describing the execution plan
        """
        plan = {
            "pipeline": self.name,
            "input_type": type(data).__name__,
            "stages": [],
        }

        current_data = data
        for stage in self.stages:
            stage_info = {
                "name": stage.name,
                "would_execute": True,
                "has_condition": stage.condition is not None,
                "has_error_handler": stage.on_error is not None,
                "retry_count": stage.retry_count,
            }

            # Check condition
            if stage.condition:
                stage_info["would_execute"] = stage.condition(current_data)
                stage_info["condition_result"] = stage_info["would_execute"]

            plan["stages"].append(stage_info)

        return plan

    # =========================================================================
    # UTILITIES
    # =========================================================================

    def reset(self) -> "Pipeline":
        """Reset pipeline and all stages."""
        self._execution_count = 0
        self._last_result = None
        for stage in self.stages:
            stage.reset()
        return self

    @property
    def execution_count(self) -> int:
        """Number of times pipeline has been executed."""
        return self._execution_count

    @property
    def last_result(self) -> Optional[PipelineResult]:
        """Result of last execution."""
        return self._last_result

    @property
    def stage_names(self) -> List[str]:
        """Names of all stages."""
        return [s.name for s in self.stages]

    def get_stage(self, name: str) -> Optional[Stage]:
        """Get a stage by name."""
        for stage in self.stages:
            if stage.name == name:
                return stage
        return None

    def __repr__(self) -> str:
        return f"Pipeline(name='{self.name}', stages={self.stage_names})"


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_pipeline(*stages: Stage, name: str = "pipeline") -> Pipeline:
    """Create a pipeline with the given stages."""
    pipeline = Pipeline(name)
    for stage in stages:
        pipeline.add_stage(stage)
    return pipeline


def create_etl_pipeline(
    extractor: Callable,
    transformer: Callable,
    loader: Callable,
    name: str = "etl_pipeline",
) -> Pipeline:
    """Create a standard ETL pipeline."""
    return (Pipeline(name)
        .add_stage(Stage("extract", extractor))
        .add_stage(Stage("transform", transformer))
        .add_stage(Stage("load", loader)))
