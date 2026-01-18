# fokha_data/pipeline/stages/base_stage.py
# =============================================================================
# TEMPLATE: Pipeline Stage
# =============================================================================
# Individual step in the data pipeline.
# Each stage transforms data and reports status.
# =============================================================================

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Dict, List
from enum import Enum
from datetime import datetime


class StageStatus(Enum):
    """Status of a stage execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StageResult:
    """
    Result of a stage execution.

    Attributes:
        status: Execution status
        data: Output data (if successful)
        error: Error message (if failed)
        duration_ms: Execution time in milliseconds
        metadata: Additional execution metadata
    """
    status: StageStatus
    data: Any = None
    error: Optional[str] = None
    duration_ms: float = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        return self.status == StageStatus.SUCCESS

    @property
    def is_failed(self) -> bool:
        return self.status == StageStatus.FAILED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }


class Stage:
    """
    A single stage in the data pipeline.

    Stages are the building blocks of pipelines. Each stage:
    - Receives data from the previous stage
    - Transforms/processes the data
    - Passes data to the next stage

    Usage:
        # Simple stage with function
        validate_stage = Stage("validate", lambda data: validator.validate(data))

        # Stage with condition
        format_stage = Stage(
            name="format",
            handler=formatter.format,
            condition=lambda data: data is not None,
        )

        # Stage with error handling
        store_stage = Stage(
            name="store",
            handler=storage.save,
            on_error=lambda e, data: logger.error(f"Failed to store: {e}"),
        )
    """

    def __init__(
        self,
        name: str,
        handler: Callable[[Any], Any],
        condition: Optional[Callable[[Any], bool]] = None,
        on_error: Optional[Callable[[Exception, Any], Any]] = None,
        timeout_ms: Optional[int] = None,
        retry_count: int = 0,
        retry_delay_ms: int = 1000,
    ):
        """
        Initialize a pipeline stage.

        Args:
            name: Stage name (for logging/debugging)
            handler: Function to process data
            condition: Optional condition to check before executing
            on_error: Optional error handler
            timeout_ms: Optional timeout in milliseconds
            retry_count: Number of retries on failure
            retry_delay_ms: Delay between retries
        """
        self.name = name
        self.handler = handler
        self.condition = condition
        self.on_error = on_error
        self.timeout_ms = timeout_ms
        self.retry_count = retry_count
        self.retry_delay_ms = retry_delay_ms

        # Execution state
        self._execution_count = 0
        self._last_result: Optional[StageResult] = None

    def execute(self, data: Any) -> StageResult:
        """
        Execute the stage with the given data.

        Args:
            data: Input data to process

        Returns:
            StageResult with status and output data
        """
        start_time = datetime.utcnow()
        self._execution_count += 1

        # Check condition
        if self.condition and not self.condition(data):
            return StageResult(
                status=StageStatus.SKIPPED,
                data=data,
                metadata={"reason": "condition not met"},
            )

        # Execute with retries
        last_error = None
        for attempt in range(self.retry_count + 1):
            try:
                result_data = self.handler(data)

                duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                result = StageResult(
                    status=StageStatus.SUCCESS,
                    data=result_data,
                    duration_ms=duration,
                    metadata={"attempt": attempt + 1},
                )
                self._last_result = result
                return result

            except Exception as e:
                last_error = e

                # Call error handler if provided
                if self.on_error:
                    try:
                        recovery_data = self.on_error(e, data)
                        if recovery_data is not None:
                            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                            return StageResult(
                                status=StageStatus.SUCCESS,
                                data=recovery_data,
                                duration_ms=duration,
                                metadata={"recovered": True, "attempt": attempt + 1},
                            )
                    except Exception:
                        pass

                # Wait before retry
                if attempt < self.retry_count:
                    import time
                    time.sleep(self.retry_delay_ms / 1000)

        # All retries failed
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        result = StageResult(
            status=StageStatus.FAILED,
            data=data,  # Return original data
            error=str(last_error),
            duration_ms=duration,
            metadata={"attempts": self.retry_count + 1},
        )
        self._last_result = result
        return result

    def reset(self) -> None:
        """Reset stage state."""
        self._execution_count = 0
        self._last_result = None

    @property
    def execution_count(self) -> int:
        """Number of times this stage has been executed."""
        return self._execution_count

    @property
    def last_result(self) -> Optional[StageResult]:
        """Result of the last execution."""
        return self._last_result

    def __repr__(self) -> str:
        return f"Stage(name='{self.name}')"


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_stage(
    name: str,
    handler: Callable[[Any], Any],
    **kwargs,
) -> Stage:
    """Create a stage with the given configuration."""
    return Stage(name, handler, **kwargs)


def create_validation_stage(validator, name: str = "validate") -> Stage:
    """Create a validation stage."""
    def validate_handler(data):
        result = validator.validate(data)
        if not result.is_valid:
            raise ValueError(f"Validation failed: {result.errors}")
        return data

    return Stage(name, validate_handler)


def create_format_stage(formatter, name: str = "format") -> Stage:
    """Create a formatting stage."""
    return Stage(name, formatter.format)


def create_store_stage(storage, name: str = "store") -> Stage:
    """Create a storage stage."""
    def store_handler(data):
        record_id = storage.save(data)
        return {"id": record_id, "data": data}

    return Stage(name, store_handler)
