# fokha_data/factory/generators/dynamic_generator.py
# =============================================================================
# TEMPLATE: Dynamic Data Generator
# =============================================================================
# Generates randomized, variable data.
# Each call can produce different output.
# Supports seeds for reproducibility.
# Useful for:
#   - Stress testing with varied data
#   - Fuzzing and property-based testing
#   - Realistic data simulation
# =============================================================================

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import random
import string
import copy
import uuid


class DynamicGenerator:
    """
    Generates randomized, variable data.

    Features:
        - Random values within constraints
        - Seeded generation for reproducibility
        - Type-aware random generation
        - Supports templates with randomization hints

    Usage:
        generator = DynamicGenerator()

        # Random data
        data = generator.generate(
            template={"name": "User_{random}", "score": {"_type": "int", "_min": 0, "_max": 100}},
        )
        # Result: {"name": "User_a7x9k", "score": 42}

        # Seeded (reproducible)
        data1 = generator.generate(template={"value": {"_type": "int"}}, seed=42)
        data2 = generator.generate(template={"value": {"_type": "int"}}, seed=42)
        # data1 == data2 (same seed = same output)
    """

    def __init__(self):
        self._rng = random.Random()

    def generate(
        self,
        template: Optional[Dict[str, Any]] = None,
        overrides: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate data from template with randomization.

        Args:
            template: Base template (can include randomization hints)
            overrides: Values to override (not randomized)
            seed: Random seed for reproducibility

        Returns:
            Generated data dictionary
        """
        # Set seed if provided
        if seed is not None:
            self._rng.seed(seed)

        if template is None:
            template = {}

        # Deep copy and process template
        result = self._process_template(copy.deepcopy(template))

        # Apply overrides (overrides are NOT randomized)
        if overrides:
            overrides_clean = {k: v for k, v in overrides.items() if not k.startswith("_")}
            result = self._apply_overrides(result, overrides_clean)

        return result

    def generate_default(self, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate random default payload.

        Args:
            overrides: Values to include

        Returns:
            Random default payload
        """
        result = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.utcnow().isoformat(),
            "data": {
                "random_string": self.random_string(10),
                "random_int": self.random_int(0, 1000),
                "random_float": self.random_float(0, 100),
            },
        }

        if overrides:
            overrides_clean = {k: v for k, v in overrides.items() if not k.startswith("_")}
            result["data"].update(overrides_clean)

        return result

    def _process_template(self, data: Any) -> Any:
        """
        Process template, replacing randomization hints with random values.

        Hint format:
            {"_type": "int", "_min": 0, "_max": 100}
            {"_type": "string", "_length": 10}
            {"_type": "choice", "_options": ["a", "b", "c"]}
            "{random}" in strings -> replaced with random suffix
        """
        if isinstance(data, dict):
            # Check if this is a randomization hint
            if "_type" in data:
                return self._generate_by_type(data)
            else:
                return {k: self._process_template(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._process_template(item) for item in data]
        elif isinstance(data, str):
            return self._process_string(data)
        else:
            return data

    def _generate_by_type(self, hint: Dict[str, Any]) -> Any:
        """Generate a value based on type hint."""
        type_name = hint.get("_type", "string")

        if type_name == "int" or type_name == "integer":
            return self.random_int(
                hint.get("_min", 0),
                hint.get("_max", 1000),
            )
        elif type_name == "float" or type_name == "number":
            return self.random_float(
                hint.get("_min", 0.0),
                hint.get("_max", 1000.0),
                hint.get("_precision", 2),
            )
        elif type_name == "string":
            return self.random_string(
                hint.get("_length", 10),
                hint.get("_charset", "alphanumeric"),
            )
        elif type_name == "bool" or type_name == "boolean":
            return self.random_bool(hint.get("_probability", 0.5))
        elif type_name == "choice":
            options = hint.get("_options", [])
            return self.random_choice(options) if options else None
        elif type_name == "uuid":
            return str(uuid.uuid4())
        elif type_name == "datetime":
            return self.random_datetime(
                hint.get("_start"),
                hint.get("_end"),
            ).isoformat()
        elif type_name == "date":
            return self.random_datetime(
                hint.get("_start"),
                hint.get("_end"),
            ).date().isoformat()
        elif type_name == "email":
            return self.random_email()
        elif type_name == "array":
            item_template = hint.get("_item", {"_type": "string"})
            count = hint.get("_count", self.random_int(1, 5))
            return [self._generate_by_type(item_template) for _ in range(count)]
        else:
            return self.random_string(10)

    def _process_string(self, s: str) -> str:
        """Process string, replacing {random} placeholders."""
        if "{random}" in s:
            s = s.replace("{random}", self.random_string(5))
        if "{uuid}" in s:
            s = s.replace("{uuid}", str(uuid.uuid4()))
        if "{now}" in s:
            s = s.replace("{now}", datetime.utcnow().isoformat())
        return s

    def _apply_overrides(self, data: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Apply overrides to data."""
        result = copy.deepcopy(data)
        for key, value in overrides.items():
            if "." in key:
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

    # =========================================================================
    # RANDOM VALUE GENERATORS
    # =========================================================================

    def random_int(self, min_val: int = 0, max_val: int = 1000) -> int:
        """Generate random integer in range."""
        return self._rng.randint(min_val, max_val)

    def random_float(self, min_val: float = 0.0, max_val: float = 1000.0, precision: int = 2) -> float:
        """Generate random float in range with precision."""
        value = self._rng.uniform(min_val, max_val)
        return round(value, precision)

    def random_string(self, length: int = 10, charset: str = "alphanumeric") -> str:
        """
        Generate random string.

        Charsets:
            - alphanumeric: a-z, A-Z, 0-9
            - alpha: a-z, A-Z
            - lowercase: a-z
            - uppercase: A-Z
            - numeric: 0-9
            - hex: 0-9, a-f
        """
        charsets = {
            "alphanumeric": string.ascii_letters + string.digits,
            "alpha": string.ascii_letters,
            "lowercase": string.ascii_lowercase,
            "uppercase": string.ascii_uppercase,
            "numeric": string.digits,
            "hex": string.hexdigits[:16],
        }
        chars = charsets.get(charset, charsets["alphanumeric"])
        return ''.join(self._rng.choice(chars) for _ in range(length))

    def random_bool(self, probability: float = 0.5) -> bool:
        """Generate random boolean with given probability of True."""
        return self._rng.random() < probability

    def random_choice(self, options: List[Any]) -> Any:
        """Choose random item from list."""
        if not options:
            return None
        return self._rng.choice(options)

    def random_datetime(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> datetime:
        """
        Generate random datetime in range.

        Args:
            start: Start datetime ISO string (default: 1 year ago)
            end: End datetime ISO string (default: now)
        """
        if start:
            start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
        else:
            start_dt = datetime.utcnow() - timedelta(days=365)

        if end:
            end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
        else:
            end_dt = datetime.utcnow()

        delta = end_dt - start_dt
        random_seconds = self._rng.randint(0, int(delta.total_seconds()))
        return start_dt + timedelta(seconds=random_seconds)

    def random_email(self) -> str:
        """Generate random email address."""
        username = self.random_string(8, "lowercase")
        domains = ["example.com", "test.com", "mock.org", "fake.net"]
        return f"{username}@{self.random_choice(domains)}"

    def random_phone(self, format: str = "+1-XXX-XXX-XXXX") -> str:
        """Generate random phone number."""
        result = ""
        for char in format:
            if char == "X":
                result += str(self._rng.randint(0, 9))
            else:
                result += char
        return result

    def random_from_distribution(
        self,
        distribution: str = "uniform",
        **kwargs,
    ) -> float:
        """
        Generate value from statistical distribution.

        Distributions:
            - uniform: min, max
            - normal/gaussian: mean, std
            - exponential: lambd
        """
        if distribution == "uniform":
            return self._rng.uniform(kwargs.get("min", 0), kwargs.get("max", 1))
        elif distribution in ("normal", "gaussian"):
            return self._rng.gauss(kwargs.get("mean", 0), kwargs.get("std", 1))
        elif distribution == "exponential":
            return self._rng.expovariate(kwargs.get("lambd", 1))
        else:
            return self._rng.random()
