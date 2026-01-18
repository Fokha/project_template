# fokha_data/processors/transformer.py
# =============================================================================
# TEMPLATE: Data Transformer
# =============================================================================
# Applies business logic transformations to data.
# Maps, filters, aggregates, and transforms data structures.
#
# Features:
#   - Field mapping/renaming
#   - Computed fields
#   - Filtering
#   - Aggregation
#   - Flattening/nesting
#   - Pipeline composition
# =============================================================================

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable, Union
from enum import Enum
import copy


class TransformType(Enum):
    """Types of transformations."""
    MAP = "map"           # Transform each item
    FILTER = "filter"     # Filter items
    REDUCE = "reduce"     # Aggregate to single value
    FLATTEN = "flatten"   # Flatten nested structure
    NEST = "nest"         # Create nested structure
    RENAME = "rename"     # Rename fields
    COMPUTE = "compute"   # Add computed fields
    REMOVE = "remove"     # Remove fields
    MERGE = "merge"       # Merge with other data
    CUSTOM = "custom"     # Custom transform


@dataclass
class TransformConfig:
    """
    Configuration for a transformation.

    Attributes:
        transform_type: Type of transformation
        params: Parameters for the transformation
        condition: Optional condition for applying transform
    """
    transform_type: TransformType
    params: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[Callable[[Any], bool]] = None

    @staticmethod
    def map_fields(mapping: Dict[str, str]) -> "TransformConfig":
        """Create a field mapping transform."""
        return TransformConfig(TransformType.RENAME, {"mapping": mapping})

    @staticmethod
    def compute_field(field: str, func: Callable[[Dict], Any]) -> "TransformConfig":
        """Create a computed field transform."""
        return TransformConfig(TransformType.COMPUTE, {"field": field, "func": func})

    @staticmethod
    def remove_fields(*fields: str) -> "TransformConfig":
        """Create a field removal transform."""
        return TransformConfig(TransformType.REMOVE, {"fields": list(fields)})

    @staticmethod
    def filter_by(func: Callable[[Any], bool]) -> "TransformConfig":
        """Create a filter transform."""
        return TransformConfig(TransformType.FILTER, {"func": func})


class Transformer:
    """
    Applies transformations to data.

    Usage:
        transformer = Transformer()

        # Add transformations
        transformer.add_transform(TransformConfig.map_fields({
            "old_name": "new_name",
            "user.email": "contact_email",
        }))

        transformer.add_transform(TransformConfig.compute_field(
            "full_name",
            lambda x: f"{x.get('first_name', '')} {x.get('last_name', '')}".strip()
        ))

        transformer.add_transform(TransformConfig.remove_fields(
            "internal_id", "debug_info"
        ))

        # Apply transformations
        result = transformer.transform(data)

        # Or use fluent API
        result = (transformer
            .rename("old", "new")
            .compute("total", lambda x: x["a"] + x["b"])
            .remove("temp")
            .apply(data))
    """

    def __init__(self):
        self.transforms: List[TransformConfig] = []
        self.custom_transforms: Dict[str, Callable] = {}

    # =========================================================================
    # CONFIGURATION
    # =========================================================================

    def add_transform(self, config: TransformConfig) -> "Transformer":
        """Add a transformation configuration."""
        self.transforms.append(config)
        return self

    def clear_transforms(self) -> "Transformer":
        """Clear all transformations."""
        self.transforms = []
        return self

    def register_custom_transform(self, name: str, func: Callable[[Any, Dict], Any]) -> "Transformer":
        """
        Register a custom transformation function.

        Args:
            name: Name to reference the transform
            func: Function(data, params) -> transformed_data
        """
        self.custom_transforms[name] = func
        return self

    # =========================================================================
    # FLUENT API
    # =========================================================================

    def rename(self, old_name: str, new_name: str) -> "Transformer":
        """Rename a field (fluent API)."""
        self.transforms.append(TransformConfig(
            TransformType.RENAME,
            {"mapping": {old_name: new_name}}
        ))
        return self

    def compute(self, field: str, func: Callable[[Dict], Any]) -> "Transformer":
        """Add a computed field (fluent API)."""
        self.transforms.append(TransformConfig(
            TransformType.COMPUTE,
            {"field": field, "func": func}
        ))
        return self

    def remove(self, *fields: str) -> "Transformer":
        """Remove fields (fluent API)."""
        self.transforms.append(TransformConfig(
            TransformType.REMOVE,
            {"fields": list(fields)}
        ))
        return self

    def filter(self, func: Callable[[Any], bool]) -> "Transformer":
        """Add a filter (fluent API)."""
        self.transforms.append(TransformConfig(
            TransformType.FILTER,
            {"func": func}
        ))
        return self

    def apply(self, data: Any) -> Any:
        """Apply all transformations (fluent API terminus)."""
        return self.transform(data)

    # =========================================================================
    # TRANSFORMATION
    # =========================================================================

    def transform(self, data: Any) -> Any:
        """
        Apply all configured transformations to data.

        Args:
            data: Data to transform (dict, list, or DataRecord)

        Returns:
            Transformed data
        """
        # Handle DataRecord
        is_record = hasattr(data, 'payload')
        if is_record:
            working_data = copy.deepcopy(data.payload)
        else:
            working_data = copy.deepcopy(data)

        # Apply each transformation
        for config in self.transforms:
            # Check condition
            if config.condition and not config.condition(working_data):
                continue

            working_data = self._apply_transform(working_data, config)

        # Return in same format
        if is_record:
            return data.with_payload(working_data)
        return working_data

    def transform_one(self, item: Dict[str, Any], config: TransformConfig) -> Dict[str, Any]:
        """Apply a single transformation to one item."""
        return self._apply_transform(copy.deepcopy(item), config)

    def _apply_transform(self, data: Any, config: TransformConfig) -> Any:
        """Apply a single transformation."""
        transform_type = config.transform_type
        params = config.params

        if transform_type == TransformType.RENAME:
            return self._transform_rename(data, params.get("mapping", {}))

        elif transform_type == TransformType.COMPUTE:
            return self._transform_compute(data, params.get("field"), params.get("func"))

        elif transform_type == TransformType.REMOVE:
            return self._transform_remove(data, params.get("fields", []))

        elif transform_type == TransformType.FILTER:
            return self._transform_filter(data, params.get("func"))

        elif transform_type == TransformType.FLATTEN:
            return self._transform_flatten(data, params.get("separator", "."))

        elif transform_type == TransformType.NEST:
            return self._transform_nest(data, params.get("mapping", {}))

        elif transform_type == TransformType.MAP:
            return self._transform_map(data, params.get("func"))

        elif transform_type == TransformType.MERGE:
            return self._transform_merge(data, params.get("other", {}))

        elif transform_type == TransformType.CUSTOM:
            transform_name = params.get("name")
            if transform_name and transform_name in self.custom_transforms:
                return self.custom_transforms[transform_name](data, params)

        return data

    # =========================================================================
    # TRANSFORM IMPLEMENTATIONS
    # =========================================================================

    def _transform_rename(self, data: Any, mapping: Dict[str, str]) -> Any:
        """Rename fields according to mapping."""
        if isinstance(data, list):
            return [self._transform_rename(item, mapping) for item in data]

        if not isinstance(data, dict):
            return data

        result = {}
        for key, value in data.items():
            new_key = mapping.get(key, key)
            result[new_key] = value

        # Handle nested mappings (e.g., "user.name" -> "username")
        for old_path, new_key in mapping.items():
            if "." in old_path:
                value = self._get_nested_value(data, old_path)
                if value is not None:
                    result[new_key] = value

        return result

    def _transform_compute(self, data: Any, field: str, func: Callable) -> Any:
        """Add a computed field."""
        if isinstance(data, list):
            return [self._transform_compute(item, field, func) for item in data]

        if not isinstance(data, dict):
            return data

        if func:
            data[field] = func(data)
        return data

    def _transform_remove(self, data: Any, fields: List[str]) -> Any:
        """Remove specified fields."""
        if isinstance(data, list):
            return [self._transform_remove(item, fields) for item in data]

        if not isinstance(data, dict):
            return data

        result = copy.deepcopy(data)
        for field in fields:
            if "." in field:
                self._remove_nested_value(result, field)
            elif field in result:
                del result[field]

        return result

    def _transform_filter(self, data: Any, func: Callable[[Any], bool]) -> Any:
        """Filter items in a list."""
        if isinstance(data, list):
            return [item for item in data if func(item)]
        return data

    def _transform_flatten(self, data: Dict[str, Any], separator: str = ".") -> Dict[str, Any]:
        """Flatten nested dict to single level."""
        if not isinstance(data, dict):
            return data

        result = {}

        def flatten(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{prefix}{separator}{key}" if prefix else key
                    flatten(value, new_key)
            else:
                result[prefix] = obj

        flatten(data)
        return result

    def _transform_nest(self, data: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
        """Nest flat fields into nested structure."""
        if not isinstance(data, dict):
            return data

        result = copy.deepcopy(data)

        for flat_key, nested_path in mapping.items():
            if flat_key in result:
                value = result.pop(flat_key)
                self._set_nested_value(result, nested_path, value)

        return result

    def _transform_map(self, data: Any, func: Callable[[Any], Any]) -> Any:
        """Apply function to each item."""
        if isinstance(data, list):
            return [func(item) for item in data]
        return func(data)

    def _transform_merge(self, data: Dict[str, Any], other: Dict[str, Any]) -> Dict[str, Any]:
        """Merge other dict into data."""
        if not isinstance(data, dict):
            return data

        result = copy.deepcopy(data)
        result.update(other)
        return result

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get value from nested dict using dot notation."""
        keys = path.split(".")
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """Set value in nested dict using dot notation."""
        keys = path.split(".")
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    def _remove_nested_value(self, data: Dict[str, Any], path: str) -> None:
        """Remove value from nested dict using dot notation."""
        keys = path.split(".")
        current = data
        for key in keys[:-1]:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return
        if isinstance(current, dict) and keys[-1] in current:
            del current[keys[-1]]


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def map_fields(data: Any, mapping: Dict[str, str]) -> Any:
    """Quick field rename."""
    return Transformer().rename_fields(data, mapping)


def pick_fields(data: Dict[str, Any], *fields: str) -> Dict[str, Any]:
    """Pick only specified fields from data."""
    return {k: v for k, v in data.items() if k in fields}


def omit_fields(data: Dict[str, Any], *fields: str) -> Dict[str, Any]:
    """Omit specified fields from data."""
    return {k: v for k, v in data.items() if k not in fields}
