# fokha_data/pipeline/gatherer.py
# =============================================================================
# TEMPLATE: Data Gatherer
# =============================================================================
# Collects and aggregates data from multiple sources.
# Second stage in the data pipeline after requester.
# =============================================================================

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
from datetime import datetime


class GatherStrategy(Enum):
    """Strategy for gathering from multiple sources."""
    ALL = "all"           # Gather from all sources, fail if any fails
    FIRST_SUCCESS = "first_success"  # Return first successful result
    BEST_EFFORT = "best_effort"      # Gather from all, ignore failures
    PARALLEL = "parallel"  # Gather in parallel


class MergeStrategy(Enum):
    """Strategy for merging gathered data."""
    CONCAT = "concat"     # Concatenate lists
    MERGE = "merge"       # Merge dictionaries
    REPLACE = "replace"   # Last source wins
    NESTED = "nested"     # Keep as nested structure


@dataclass
class GatherConfig:
    """
    Configuration for data gathering.

    Attributes:
        strategy: Gathering strategy
        merge_strategy: How to merge multiple results
        timeout_ms: Overall gather timeout
        sources: List of source configurations
    """
    strategy: GatherStrategy = GatherStrategy.ALL
    merge_strategy: MergeStrategy = MergeStrategy.MERGE
    timeout_ms: int = 60000
    sources: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class GatherResult:
    """
    Result of data gathering.

    Attributes:
        success: Whether gathering succeeded
        data: Gathered and merged data
        source_results: Results from each source
        error: Error message if failed
    """
    success: bool
    data: Any = None
    source_results: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def successful_sources(self) -> List[str]:
        """Sources that succeeded."""
        return [name for name, result in self.source_results.items()
                if result.get("success", False)]

    @property
    def failed_sources(self) -> List[str]:
        """Sources that failed."""
        return [name for name, result in self.source_results.items()
                if not result.get("success", False)]


class Gatherer:
    """
    Data gatherer for collecting from multiple sources.

    Usage:
        gatherer = Gatherer()

        # Register sources
        gatherer.add_source("api", lambda: requester.get("https://api.example.com/data"))
        gatherer.add_source("file", lambda: requester.from_file("data.json"))
        gatherer.add_source("cache", lambda: cache.get("data"))

        # Gather from all sources
        result = gatherer.gather()

        # Gather with specific config
        result = gatherer.gather(GatherConfig(
            strategy=GatherStrategy.FIRST_SUCCESS,
        ))

        # Gather specific sources
        result = gatherer.gather_from(["api", "cache"])
    """

    def __init__(self):
        self._sources: Dict[str, Callable[[], Any]] = {}
        self._transformers: Dict[str, Callable[[Any], Any]] = {}
        self._default_config = GatherConfig()

    # =========================================================================
    # CONFIGURATION
    # =========================================================================

    def add_source(
        self,
        name: str,
        fetcher: Callable[[], Any],
        transformer: Optional[Callable[[Any], Any]] = None,
    ) -> "Gatherer":
        """
        Add a data source.

        Args:
            name: Source name
            fetcher: Function that returns data
            transformer: Optional function to transform data after fetching
        """
        self._sources[name] = fetcher
        if transformer:
            self._transformers[name] = transformer
        return self

    def remove_source(self, name: str) -> "Gatherer":
        """Remove a source."""
        self._sources.pop(name, None)
        self._transformers.pop(name, None)
        return self

    def set_default_config(self, config: GatherConfig) -> "Gatherer":
        """Set default gather configuration."""
        self._default_config = config
        return self

    @property
    def source_names(self) -> List[str]:
        """Get list of registered source names."""
        return list(self._sources.keys())

    # =========================================================================
    # GATHERING
    # =========================================================================

    def gather(self, config: Optional[GatherConfig] = None) -> GatherResult:
        """
        Gather data from all registered sources.

        Args:
            config: Optional gather configuration

        Returns:
            GatherResult with merged data
        """
        config = config or self._default_config
        return self.gather_from(list(self._sources.keys()), config)

    def gather_from(
        self,
        source_names: List[str],
        config: Optional[GatherConfig] = None,
    ) -> GatherResult:
        """
        Gather data from specific sources.

        Args:
            source_names: Names of sources to gather from
            config: Optional gather configuration

        Returns:
            GatherResult with merged data
        """
        config = config or self._default_config
        start_time = datetime.utcnow()

        source_results = {}
        gathered_data = []

        for name in source_names:
            if name not in self._sources:
                source_results[name] = {
                    "success": False,
                    "error": f"Unknown source: {name}",
                }
                continue

            try:
                # Fetch data
                fetcher = self._sources[name]
                result = fetcher()

                # Handle RequestResult objects
                if hasattr(result, 'success'):
                    if not result.success:
                        source_results[name] = {
                            "success": False,
                            "error": result.error,
                        }
                        if config.strategy == GatherStrategy.ALL:
                            return GatherResult(
                                success=False,
                                source_results=source_results,
                                error=f"Source '{name}' failed: {result.error}",
                            )
                        continue
                    result = result.data

                # Apply transformer if exists
                if name in self._transformers:
                    result = self._transformers[name](result)

                source_results[name] = {
                    "success": True,
                    "data": result,
                }
                gathered_data.append((name, result))

                # First success strategy
                if config.strategy == GatherStrategy.FIRST_SUCCESS:
                    duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                    return GatherResult(
                        success=True,
                        data=result,
                        source_results=source_results,
                        metadata={"duration_ms": duration, "source": name},
                    )

            except Exception as e:
                source_results[name] = {
                    "success": False,
                    "error": str(e),
                }

                if config.strategy == GatherStrategy.ALL:
                    return GatherResult(
                        success=False,
                        source_results=source_results,
                        error=f"Source '{name}' failed: {e}",
                    )

        # Merge gathered data
        if not gathered_data:
            return GatherResult(
                success=False,
                source_results=source_results,
                error="No data gathered from any source",
            )

        merged_data = self._merge_data(gathered_data, config.merge_strategy)

        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        return GatherResult(
            success=True,
            data=merged_data,
            source_results=source_results,
            metadata={
                "duration_ms": duration,
                "sources_used": len(gathered_data),
            },
        )

    def gather_one(self, source_name: str) -> GatherResult:
        """
        Gather from a single source.

        Args:
            source_name: Name of source

        Returns:
            GatherResult
        """
        return self.gather_from([source_name])

    # =========================================================================
    # MERGING
    # =========================================================================

    def _merge_data(
        self,
        data_list: List[tuple],
        strategy: MergeStrategy,
    ) -> Any:
        """
        Merge gathered data according to strategy.

        Args:
            data_list: List of (source_name, data) tuples
            strategy: Merge strategy

        Returns:
            Merged data
        """
        if not data_list:
            return None

        if len(data_list) == 1:
            return data_list[0][1]

        if strategy == MergeStrategy.REPLACE:
            return data_list[-1][1]

        elif strategy == MergeStrategy.NESTED:
            return {name: data for name, data in data_list}

        elif strategy == MergeStrategy.CONCAT:
            result = []
            for name, data in data_list:
                if isinstance(data, list):
                    result.extend(data)
                else:
                    result.append(data)
            return result

        elif strategy == MergeStrategy.MERGE:
            result = {}
            for name, data in data_list:
                if isinstance(data, dict):
                    result.update(data)
                else:
                    result[name] = data
            return result

        return data_list[-1][1]
