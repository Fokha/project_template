# fokha_data/unifiers/merger.py
# =============================================================================
# TEMPLATE: Data Merger
# =============================================================================
# Merges data from multiple sources into a unified structure.
# =============================================================================

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from enum import Enum


class ConflictResolution(Enum):
    """How to resolve conflicts when merging."""
    FIRST = "first"        # Keep first value
    LAST = "last"          # Keep last value
    ERROR = "error"        # Raise error on conflict
    MERGE = "merge"        # Deep merge (for dicts)
    CONCAT = "concat"      # Concatenate (for lists)
    CUSTOM = "custom"      # Use custom resolver


@dataclass
class MergeConfig:
    """Configuration for merging."""
    conflict_resolution: ConflictResolution = ConflictResolution.LAST
    deep_merge: bool = True
    ignore_none: bool = True
    custom_resolver: Optional[Callable[[str, Any, Any], Any]] = None


class Merger:
    """
    Merges data from multiple sources.

    Usage:
        merger = Merger()

        # Simple merge
        result = merger.merge([dict1, dict2, dict3])

        # With conflict resolution
        result = merger.merge(
            [dict1, dict2],
            MergeConfig(conflict_resolution=ConflictResolution.FIRST)
        )

        # Deep merge
        result = merger.deep_merge(dict1, dict2)
    """

    def __init__(self, default_config: Optional[MergeConfig] = None):
        self.default_config = default_config or MergeConfig()

    def merge(
        self,
        sources: List[Dict[str, Any]],
        config: Optional[MergeConfig] = None,
    ) -> Dict[str, Any]:
        """
        Merge multiple dictionaries.

        Args:
            sources: List of dictionaries to merge
            config: Merge configuration

        Returns:
            Merged dictionary
        """
        config = config or self.default_config

        if not sources:
            return {}

        result = {}
        for source in sources:
            if source is None:
                continue
            result = self._merge_two(result, source, config)

        return result

    def deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.

        Args:
            base: Base dictionary
            update: Dictionary to merge in

        Returns:
            Merged dictionary
        """
        return self._merge_two(base, update, MergeConfig(deep_merge=True))

    def _merge_two(
        self,
        base: Dict[str, Any],
        update: Dict[str, Any],
        config: MergeConfig,
    ) -> Dict[str, Any]:
        """Merge two dictionaries."""
        import copy
        result = copy.deepcopy(base)

        for key, value in update.items():
            # Skip None if configured
            if config.ignore_none and value is None:
                continue

            if key not in result:
                result[key] = copy.deepcopy(value)
            else:
                # Handle conflict
                result[key] = self._resolve_conflict(
                    key, result[key], value, config
                )

        return result

    def _resolve_conflict(
        self,
        key: str,
        old_value: Any,
        new_value: Any,
        config: MergeConfig,
    ) -> Any:
        """Resolve a merge conflict."""
        import copy

        if config.conflict_resolution == ConflictResolution.FIRST:
            return old_value

        elif config.conflict_resolution == ConflictResolution.LAST:
            return copy.deepcopy(new_value)

        elif config.conflict_resolution == ConflictResolution.ERROR:
            raise ValueError(f"Merge conflict on key '{key}'")

        elif config.conflict_resolution == ConflictResolution.MERGE:
            if isinstance(old_value, dict) and isinstance(new_value, dict):
                return self._merge_two(old_value, new_value, config)
            return copy.deepcopy(new_value)

        elif config.conflict_resolution == ConflictResolution.CONCAT:
            if isinstance(old_value, list) and isinstance(new_value, list):
                return old_value + new_value
            return copy.deepcopy(new_value)

        elif config.conflict_resolution == ConflictResolution.CUSTOM:
            if config.custom_resolver:
                return config.custom_resolver(key, old_value, new_value)
            return copy.deepcopy(new_value)

        return copy.deepcopy(new_value)

    def merge_records(
        self,
        records: List[Any],
        key_field: str = "id",
    ) -> List[Any]:
        """
        Merge records with the same key.

        Args:
            records: List of records
            key_field: Field to use as merge key

        Returns:
            List of merged records
        """
        merged: Dict[str, Any] = {}

        for record in records:
            # Get key
            if hasattr(record, key_field):
                key = getattr(record, key_field)
            elif isinstance(record, dict):
                key = record.get(key_field)
            else:
                continue

            if key not in merged:
                merged[key] = record
            else:
                # Merge with existing
                if isinstance(record, dict) and isinstance(merged[key], dict):
                    merged[key] = self.deep_merge(merged[key], record)
                else:
                    merged[key] = record

        return list(merged.values())
