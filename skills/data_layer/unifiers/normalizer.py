# fokha_data/unifiers/normalizer.py
# =============================================================================
# TEMPLATE: Data Normalizer
# =============================================================================
# Standardizes data formats across different sources.
# =============================================================================

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
import copy


@dataclass
class NormalizeConfig:
    """Configuration for normalization."""
    lowercase_keys: bool = False
    strip_whitespace: bool = True
    remove_null: bool = False
    flatten: bool = False
    field_mapping: Dict[str, str] = field(default_factory=dict)


class Normalizer:
    """
    Normalizes data to a standard format.

    Usage:
        normalizer = Normalizer()

        # Normalize with field mapping
        result = normalizer.normalize(
            data,
            NormalizeConfig(field_mapping={
                "userName": "user_name",
                "firstName": "first_name",
            })
        )

        # Apply to multiple records
        results = normalizer.normalize_many(records)
    """

    def __init__(self, default_config: Optional[NormalizeConfig] = None):
        self.default_config = default_config or NormalizeConfig()

    def normalize(
        self,
        data: Dict[str, Any],
        config: Optional[NormalizeConfig] = None,
    ) -> Dict[str, Any]:
        """
        Normalize a dictionary.

        Args:
            data: Data to normalize
            config: Normalization configuration

        Returns:
            Normalized dictionary
        """
        config = config or self.default_config
        result = copy.deepcopy(data)

        # Apply field mapping
        if config.field_mapping:
            result = self._apply_mapping(result, config.field_mapping)

        # Lowercase keys
        if config.lowercase_keys:
            result = self._lowercase_keys(result)

        # Strip whitespace from string values
        if config.strip_whitespace:
            result = self._strip_whitespace(result)

        # Remove null values
        if config.remove_null:
            result = self._remove_null(result)

        # Flatten nested structures
        if config.flatten:
            result = self._flatten(result)

        return result

    def normalize_many(
        self,
        records: List[Dict[str, Any]],
        config: Optional[NormalizeConfig] = None,
    ) -> List[Dict[str, Any]]:
        """Normalize multiple records."""
        return [self.normalize(record, config) for record in records]

    def _apply_mapping(
        self,
        data: Dict[str, Any],
        mapping: Dict[str, str],
    ) -> Dict[str, Any]:
        """Apply field name mapping."""
        result = {}
        for key, value in data.items():
            new_key = mapping.get(key, key)
            if isinstance(value, dict):
                result[new_key] = self._apply_mapping(value, mapping)
            else:
                result[new_key] = value
        return result

    def _lowercase_keys(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert all keys to lowercase."""
        result = {}
        for key, value in data.items():
            new_key = key.lower()
            if isinstance(value, dict):
                result[new_key] = self._lowercase_keys(value)
            else:
                result[new_key] = value
        return result

    def _strip_whitespace(self, data: Any) -> Any:
        """Strip whitespace from string values."""
        if isinstance(data, str):
            return data.strip()
        elif isinstance(data, dict):
            return {k: self._strip_whitespace(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._strip_whitespace(item) for item in data]
        return data

    def _remove_null(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove keys with null values."""
        result = {}
        for key, value in data.items():
            if value is None:
                continue
            if isinstance(value, dict):
                result[key] = self._remove_null(value)
            else:
                result[key] = value
        return result

    def _flatten(
        self,
        data: Dict[str, Any],
        separator: str = ".",
        prefix: str = "",
    ) -> Dict[str, Any]:
        """Flatten nested dictionary."""
        result = {}
        for key, value in data.items():
            new_key = f"{prefix}{separator}{key}" if prefix else key
            if isinstance(value, dict):
                result.update(self._flatten(value, separator, new_key))
            else:
                result[new_key] = value
        return result
