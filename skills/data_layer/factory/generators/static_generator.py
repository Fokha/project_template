# fokha_data/factory/generators/static_generator.py
# =============================================================================
# TEMPLATE: Static Data Generator
# =============================================================================
# Generates deterministic, repeatable data.
# Same input always produces same output.
# Useful for:
#   - Unit tests that need consistent data
#   - Fixtures and snapshots
#   - Regression testing
# =============================================================================

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import copy


class StaticGenerator:
    """
    Generates deterministic, repeatable data.

    Features:
        - Always produces same output for same input
        - Supports sequential incrementing
        - Supports template interpolation
        - No randomness

    Usage:
        generator = StaticGenerator()

        # From template
        data = generator.generate(
            template={"name": "Test", "value": 100},
            overrides={"name": "Custom"},
        )
        # Result: {"name": "Custom", "value": 100}

        # Sequential
        for i in range(3):
            data = generator.generate(
                template={"id": "{seq}", "name": "Item"},
                overrides={"_sequence_index": i},
            )
        # Results: {"id": "0", ...}, {"id": "1", ...}, {"id": "2", ...}
    """

    def __init__(self):
        self._default_values = {
            "string": "test_value",
            "integer": 0,
            "float": 0.0,
            "boolean": True,
            "null": None,
            "array": [],
            "object": {},
            "datetime": "2024-01-01T00:00:00Z",
            "date": "2024-01-01",
            "uuid": "00000000-0000-0000-0000-000000000000",
            "email": "test@example.com",
            "url": "https://example.com",
        }

    def generate(
        self,
        template: Optional[Dict[str, Any]] = None,
        overrides: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = None,  # Ignored for static
    ) -> Dict[str, Any]:
        """
        Generate data from template with overrides.

        Args:
            template: Base template to start from
            overrides: Values to override in template
            seed: Ignored (for API compatibility)

        Returns:
            Generated data dictionary
        """
        if template is None:
            template = {}

        # Deep copy template to avoid mutation
        result = copy.deepcopy(template)

        # Apply overrides
        if overrides:
            sequence_index = overrides.pop("_sequence_index", 0)
            result = self._apply_overrides(result, overrides)
            result = self._interpolate(result, sequence_index)

        return result

    def generate_default(self, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate default empty payload.

        Args:
            overrides: Values to include in default

        Returns:
            Default payload dictionary
        """
        result = {
            "id": self._default_values["uuid"],
            "created_at": self._default_values["datetime"],
            "data": {},
        }

        if overrides:
            overrides_clean = {k: v for k, v in overrides.items() if not k.startswith("_")}
            result["data"] = overrides_clean

        return result

    def generate_list(
        self,
        template: Dict[str, Any],
        count: int,
        vary_field: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate a list of records with sequential variations.

        Args:
            template: Base template
            count: Number of records
            vary_field: Field to vary (will be incremented)

        Returns:
            List of generated dictionaries
        """
        results = []
        for i in range(count):
            overrides = {"_sequence_index": i}
            if vary_field and vary_field in template:
                base_value = template[vary_field]
                if isinstance(base_value, (int, float)):
                    overrides[vary_field] = base_value + i
                elif isinstance(base_value, str):
                    overrides[vary_field] = f"{base_value}_{i}"

            results.append(self.generate(template, overrides))

        return results

    def _apply_overrides(self, data: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply overrides to data, supporting nested paths.

        Supports dot notation for nested fields:
            {"user.name": "John"} -> {"user": {"name": "John"}}
        """
        result = copy.deepcopy(data)

        for key, value in overrides.items():
            if key.startswith("_"):
                continue  # Skip internal keys

            if "." in key:
                # Nested path
                parts = key.split(".")
                current = result
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                result[key] = value

        return result

    def _interpolate(self, data: Any, sequence_index: int = 0) -> Any:
        """
        Interpolate special placeholders in data.

        Placeholders:
            {seq} - Sequence index
            {now} - Current ISO datetime
            {date} - Current date
            {uuid} - Static UUID
        """
        if isinstance(data, str):
            data = data.replace("{seq}", str(sequence_index))
            data = data.replace("{now}", datetime.utcnow().isoformat())
            data = data.replace("{date}", datetime.utcnow().date().isoformat())
            data = data.replace("{uuid}", f"static-{sequence_index:08d}")
            return data
        elif isinstance(data, dict):
            return {k: self._interpolate(v, sequence_index) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._interpolate(item, sequence_index) for item in data]
        else:
            return data

    def get_default_value(self, type_name: str) -> Any:
        """Get the default value for a type."""
        return self._default_values.get(type_name)

    def set_default_value(self, type_name: str, value: Any) -> None:
        """Set a custom default value for a type."""
        self._default_values[type_name] = value
