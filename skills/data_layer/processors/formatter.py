# fokha_data/processors/formatter.py
# =============================================================================
# TEMPLATE: Data Formatter
# =============================================================================
# Normalizes and formats data into consistent structure.
# Handles type conversions, null handling, and format standardization.
#
# Features:
#   - Type coercion/conversion
#   - Null/default value handling
#   - Date/time normalization
#   - String trimming and casing
#   - Nested object formatting
# =============================================================================

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime
import copy


@dataclass
class FormatConfig:
    """
    Configuration for formatting a field.

    Attributes:
        field: Field path (dot notation supported)
        format_type: Type of formatting to apply
        params: Parameters for formatting
    """
    field: str
    format_type: str
    params: Dict[str, Any] = field(default_factory=dict)

    # Format types:
    # - "string": Convert to string
    # - "int"/"integer": Convert to int
    # - "float"/"number": Convert to float
    # - "bool"/"boolean": Convert to bool
    # - "datetime": Parse and format datetime
    # - "date": Parse and format date
    # - "trim": Trim whitespace
    # - "lower"/"upper"/"title": Case conversion
    # - "default": Set default if null
    # - "round": Round number
    # - "truncate": Truncate string
    # - "custom": Custom function


class Formatter:
    """
    Formats and normalizes data.

    Usage:
        formatter = Formatter()

        # Add format rules
        formatter.add_format(FormatConfig("name", "trim"))
        formatter.add_format(FormatConfig("name", "title"))
        formatter.add_format(FormatConfig("price", "round", {"decimals": 2}))
        formatter.add_format(FormatConfig("status", "default", {"value": "pending"}))

        # Format data
        formatted = formatter.format(data)
    """

    def __init__(self):
        self.formats: List[FormatConfig] = []
        self.custom_formatters: Dict[str, Callable] = {}
        self._default_formats: List[FormatConfig] = []

    # =========================================================================
    # CONFIGURATION
    # =========================================================================

    def add_format(self, config: FormatConfig) -> "Formatter":
        """Add a format configuration."""
        self.formats.append(config)
        return self

    def add_formats(self, configs: List[FormatConfig]) -> "Formatter":
        """Add multiple format configurations."""
        self.formats.extend(configs)
        return self

    def clear_formats(self) -> "Formatter":
        """Clear all format configurations."""
        self.formats = []
        return self

    def register_custom_formatter(self, name: str, func: Callable[[Any, Dict], Any]) -> "Formatter":
        """
        Register a custom formatter function.

        Args:
            name: Name to reference the formatter
            func: Function(value, params) -> formatted_value
        """
        self.custom_formatters[name] = func
        return self

    def set_default_formats(self, formats: List[FormatConfig]) -> "Formatter":
        """Set default formats applied to all data."""
        self._default_formats = formats
        return self

    # =========================================================================
    # FORMATTING
    # =========================================================================

    def format(self, data: Union[Dict[str, Any], Any]) -> Union[Dict[str, Any], Any]:
        """
        Format data according to configured rules.

        Args:
            data: Data to format (dict or DataRecord)

        Returns:
            Formatted data
        """
        # Handle DataRecord
        is_record = hasattr(data, 'payload')
        if is_record:
            payload = copy.deepcopy(data.payload) if isinstance(data.payload, dict) else data.payload
        elif isinstance(data, dict):
            payload = copy.deepcopy(data)
        else:
            payload = data

        # Apply default formats first
        for config in self._default_formats:
            payload = self._apply_format(payload, config)

        # Apply configured formats
        for config in self.formats:
            payload = self._apply_format(payload, config)

        # Return in same format as input
        if is_record:
            return data.with_payload(payload)
        return payload

    def format_field(self, value: Any, format_type: str, params: Dict[str, Any] = None) -> Any:
        """Format a single value."""
        config = FormatConfig("_value", format_type, params or {})
        result = self._apply_format({"_value": value}, config)
        return result.get("_value", value)

    def _apply_format(self, data: Any, config: FormatConfig) -> Any:
        """Apply a single format configuration."""
        if not isinstance(data, dict):
            # For non-dict data, apply to the value directly
            if config.field == "_value" or config.field == "*":
                return self._format_value(data, config)
            return data

        # Get current value
        value = self._get_nested_value(data, config.field)

        # Format the value
        formatted = self._format_value(value, config)

        # Set the formatted value back
        self._set_nested_value(data, config.field, formatted)

        return data

    def _format_value(self, value: Any, config: FormatConfig) -> Any:
        """Apply formatting to a single value."""
        format_type = config.format_type.lower()
        params = config.params

        # Handle None based on format type
        if value is None:
            if format_type == "default":
                return params.get("value")
            return None

        # Type conversions
        if format_type in ("string", "str"):
            return str(value)

        elif format_type in ("int", "integer"):
            try:
                return int(float(value))
            except (ValueError, TypeError):
                return params.get("default", 0)

        elif format_type in ("float", "number"):
            try:
                return float(value)
            except (ValueError, TypeError):
                return params.get("default", 0.0)

        elif format_type in ("bool", "boolean"):
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes", "on")
            return bool(value)

        # DateTime formatting
        elif format_type == "datetime":
            return self._format_datetime(value, params)

        elif format_type == "date":
            return self._format_date(value, params)

        # String operations
        elif format_type == "trim":
            return str(value).strip() if isinstance(value, str) else value

        elif format_type == "lower":
            return str(value).lower() if isinstance(value, str) else value

        elif format_type == "upper":
            return str(value).upper() if isinstance(value, str) else value

        elif format_type == "title":
            return str(value).title() if isinstance(value, str) else value

        elif format_type == "truncate":
            max_len = params.get("max_length", params.get("length", 100))
            suffix = params.get("suffix", "...")
            if isinstance(value, str) and len(value) > max_len:
                return value[:max_len - len(suffix)] + suffix
            return value

        # Number operations
        elif format_type == "round":
            decimals = params.get("decimals", params.get("precision", 2))
            try:
                return round(float(value), decimals)
            except (ValueError, TypeError):
                return value

        elif format_type == "abs":
            try:
                return abs(float(value))
            except (ValueError, TypeError):
                return value

        # Default value
        elif format_type == "default":
            return params.get("value") if value is None else value

        # Replace
        elif format_type == "replace":
            if isinstance(value, str):
                old = params.get("old", "")
                new = params.get("new", "")
                return value.replace(old, new)
            return value

        # Custom formatter
        elif format_type == "custom":
            formatter_name = params.get("formatter")
            if formatter_name and formatter_name in self.custom_formatters:
                return self.custom_formatters[formatter_name](value, params)
            return value

        # Passthrough for unknown types
        return value

    def _format_datetime(self, value: Any, params: Dict[str, Any]) -> str:
        """Format datetime value."""
        output_format = params.get("format", "%Y-%m-%dT%H:%M:%SZ")
        input_formats = params.get("input_formats", [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ])

        if isinstance(value, datetime):
            return value.strftime(output_format)

        if isinstance(value, str):
            for fmt in input_formats:
                try:
                    dt = datetime.strptime(value.replace("+00:00", "Z"), fmt)
                    return dt.strftime(output_format)
                except ValueError:
                    continue

        return str(value)

    def _format_date(self, value: Any, params: Dict[str, Any]) -> str:
        """Format date value."""
        output_format = params.get("format", "%Y-%m-%d")
        params_copy = {**params, "format": output_format}
        result = self._format_datetime(value, params_copy)
        return result[:10] if len(result) >= 10 else result

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get value from nested dict using dot notation."""
        if path == "*":
            return data

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
        if path == "*":
            return

        keys = path.split(".")
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value


# =============================================================================
# CONVENIENCE FACTORY FUNCTIONS
# =============================================================================

def trim(field: str) -> FormatConfig:
    """Create a trim format config."""
    return FormatConfig(field, "trim")


def to_lower(field: str) -> FormatConfig:
    """Create a lowercase format config."""
    return FormatConfig(field, "lower")


def to_upper(field: str) -> FormatConfig:
    """Create an uppercase format config."""
    return FormatConfig(field, "upper")


def round_to(field: str, decimals: int = 2) -> FormatConfig:
    """Create a round format config."""
    return FormatConfig(field, "round", {"decimals": decimals})


def default_value(field: str, value: Any) -> FormatConfig:
    """Create a default value format config."""
    return FormatConfig(field, "default", {"value": value})


def to_datetime(field: str, format: str = "%Y-%m-%dT%H:%M:%SZ") -> FormatConfig:
    """Create a datetime format config."""
    return FormatConfig(field, "datetime", {"format": format})
