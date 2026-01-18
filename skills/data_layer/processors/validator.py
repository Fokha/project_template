# fokha_data/processors/validator.py
# =============================================================================
# TEMPLATE: Data Validator
# =============================================================================
# Validates data records against defined rules and schemas.
# Returns detailed validation results with error information.
#
# Features:
#   - Rule-based validation
#   - Schema validation (JSON Schema compatible)
#   - Custom validation functions
#   - Detailed error reporting
# =============================================================================

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable, Union
from enum import Enum
import re


class ValidationSeverity(Enum):
    """Severity level of validation errors."""
    ERROR = "error"       # Must be fixed, data is invalid
    WARNING = "warning"   # Should be fixed, data is usable
    INFO = "info"         # Informational, no action needed


@dataclass
class ValidationError:
    """A single validation error."""
    field: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    code: Optional[str] = None
    value: Any = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "message": self.message,
            "severity": self.severity.value,
            "code": self.code,
            "value": str(self.value) if self.value is not None else None,
        }


@dataclass
class ValidationResult:
    """Result of validation with errors and metadata."""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    info: List[ValidationError] = field(default_factory=list)
    validated_at: Optional[str] = None

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def all_messages(self) -> List[str]:
        return [e.message for e in self.errors + self.warnings + self.info]

    def add_error(self, field: str, message: str, code: str = None, value: Any = None):
        self.errors.append(ValidationError(field, message, ValidationSeverity.ERROR, code, value))
        self.is_valid = False

    def add_warning(self, field: str, message: str, code: str = None, value: Any = None):
        self.warnings.append(ValidationError(field, message, ValidationSeverity.WARNING, code, value))

    def add_info(self, field: str, message: str, code: str = None, value: Any = None):
        self.info.append(ValidationError(field, message, ValidationSeverity.INFO, code, value))

    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """Merge another validation result into this one."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)
        self.is_valid = self.is_valid and other.is_valid
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "error_count": self.error_count,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [e.to_dict() for e in self.warnings],
            "info": [e.to_dict() for e in self.info],
            "validated_at": self.validated_at,
        }


@dataclass
class ValidationRule:
    """
    A single validation rule.

    Attributes:
        field: Field path to validate (supports dot notation)
        rule_type: Type of rule (required, type, range, pattern, custom)
        params: Parameters for the rule
        message: Custom error message
        severity: Error severity if rule fails
    """
    field: str
    rule_type: str
    params: Dict[str, Any] = field(default_factory=dict)
    message: Optional[str] = None
    severity: ValidationSeverity = ValidationSeverity.ERROR
    code: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "rule_type": self.rule_type,
            "params": self.params,
            "message": self.message,
            "severity": self.severity.value,
            "code": self.code,
        }


class Validator:
    """
    Validates data records against rules.

    Usage:
        validator = Validator()

        # Add rules
        validator.add_rule(ValidationRule("name", "required"))
        validator.add_rule(ValidationRule("age", "range", {"min": 0, "max": 150}))
        validator.add_rule(ValidationRule("email", "pattern", {"regex": r".*@.*"}))

        # Validate
        result = validator.validate(data)
        if not result.is_valid:
            for error in result.errors:
                print(f"{error.field}: {error.message}")
    """

    def __init__(self):
        self.rules: List[ValidationRule] = []
        self.custom_validators: Dict[str, Callable] = {}

    # =========================================================================
    # RULE MANAGEMENT
    # =========================================================================

    def add_rule(self, rule: ValidationRule) -> "Validator":
        """Add a validation rule."""
        self.rules.append(rule)
        return self

    def add_rules(self, rules: List[ValidationRule]) -> "Validator":
        """Add multiple validation rules."""
        self.rules.extend(rules)
        return self

    def clear_rules(self) -> "Validator":
        """Clear all rules."""
        self.rules = []
        return self

    def register_custom_validator(self, name: str, func: Callable[[Any, Dict], bool]) -> "Validator":
        """
        Register a custom validation function.

        Args:
            name: Name to reference the validator
            func: Function(value, params) -> bool
        """
        self.custom_validators[name] = func
        return self

    # =========================================================================
    # VALIDATION
    # =========================================================================

    def validate(self, data: Union[Dict[str, Any], Any]) -> ValidationResult:
        """
        Validate data against all rules.

        Args:
            data: Data to validate (dict or DataRecord)

        Returns:
            ValidationResult with errors and status
        """
        from datetime import datetime

        result = ValidationResult(is_valid=True, validated_at=datetime.utcnow().isoformat())

        # Handle DataRecord
        if hasattr(data, 'payload'):
            data = data.payload if isinstance(data.payload, dict) else {"_value": data.payload}
        elif not isinstance(data, dict):
            data = {"_value": data}

        # Apply each rule
        for rule in self.rules:
            rule_result = self._apply_rule(rule, data)
            result.merge(rule_result)

        return result

    def validate_field(self, field: str, value: Any, rules: List[ValidationRule]) -> ValidationResult:
        """Validate a single field against specific rules."""
        result = ValidationResult(is_valid=True)

        for rule in rules:
            if rule.field == field:
                data = {field: value}
                rule_result = self._apply_rule(rule, data)
                result.merge(rule_result)

        return result

    def _apply_rule(self, rule: ValidationRule, data: Dict[str, Any]) -> ValidationResult:
        """Apply a single rule to data."""
        result = ValidationResult(is_valid=True)

        # Get field value (supports dot notation)
        value = self._get_nested_value(data, rule.field)

        # Apply rule based on type
        rule_type = rule.rule_type.lower()

        if rule_type == "required":
            if not self._check_required(value):
                self._add_error(result, rule, value, f"Field '{rule.field}' is required")

        elif rule_type == "type":
            expected_type = rule.params.get("type", "string")
            if not self._check_type(value, expected_type):
                self._add_error(result, rule, value, f"Field '{rule.field}' must be of type {expected_type}")

        elif rule_type == "range":
            min_val = rule.params.get("min")
            max_val = rule.params.get("max")
            if not self._check_range(value, min_val, max_val):
                self._add_error(result, rule, value, f"Field '{rule.field}' must be between {min_val} and {max_val}")

        elif rule_type == "length":
            min_len = rule.params.get("min", 0)
            max_len = rule.params.get("max", float('inf'))
            if not self._check_length(value, min_len, max_len):
                self._add_error(result, rule, value, f"Field '{rule.field}' length must be between {min_len} and {max_len}")

        elif rule_type == "pattern":
            pattern = rule.params.get("regex", rule.params.get("pattern", ".*"))
            if not self._check_pattern(value, pattern):
                self._add_error(result, rule, value, f"Field '{rule.field}' does not match required pattern")

        elif rule_type == "enum" or rule_type == "in":
            allowed = rule.params.get("values", rule.params.get("allowed", []))
            if not self._check_enum(value, allowed):
                self._add_error(result, rule, value, f"Field '{rule.field}' must be one of: {allowed}")

        elif rule_type == "custom":
            validator_name = rule.params.get("validator")
            if validator_name and validator_name in self.custom_validators:
                if not self.custom_validators[validator_name](value, rule.params):
                    self._add_error(result, rule, value, f"Field '{rule.field}' failed custom validation")

        elif rule_type == "not_null":
            if value is None:
                self._add_error(result, rule, value, f"Field '{rule.field}' cannot be null")

        elif rule_type == "not_empty":
            if value is None or value == "" or value == [] or value == {}:
                self._add_error(result, rule, value, f"Field '{rule.field}' cannot be empty")

        return result

    def _add_error(self, result: ValidationResult, rule: ValidationRule, value: Any, default_message: str):
        """Add error to result based on rule severity."""
        message = rule.message or default_message
        error = ValidationError(
            field=rule.field,
            message=message,
            severity=rule.severity,
            code=rule.code,
            value=value,
        )

        if rule.severity == ValidationSeverity.ERROR:
            result.errors.append(error)
            result.is_valid = False
        elif rule.severity == ValidationSeverity.WARNING:
            result.warnings.append(error)
        else:
            result.info.append(error)

    # =========================================================================
    # CHECK FUNCTIONS
    # =========================================================================

    def _check_required(self, value: Any) -> bool:
        return value is not None

    def _check_type(self, value: Any, expected: str) -> bool:
        if value is None:
            return True  # Let 'required' rule handle None

        type_map = {
            "string": str,
            "str": str,
            "int": int,
            "integer": int,
            "float": float,
            "number": (int, float),
            "bool": bool,
            "boolean": bool,
            "list": list,
            "array": list,
            "dict": dict,
            "object": dict,
        }
        expected_type = type_map.get(expected.lower(), str)
        return isinstance(value, expected_type)

    def _check_range(self, value: Any, min_val: Any, max_val: Any) -> bool:
        if value is None:
            return True
        if not isinstance(value, (int, float)):
            return False
        if min_val is not None and value < min_val:
            return False
        if max_val is not None and value > max_val:
            return False
        return True

    def _check_length(self, value: Any, min_len: int, max_len: Union[int, float]) -> bool:
        if value is None:
            return True
        if not hasattr(value, '__len__'):
            return False
        length = len(value)
        return min_len <= length <= max_len

    def _check_pattern(self, value: Any, pattern: str) -> bool:
        if value is None:
            return True
        if not isinstance(value, str):
            return False
        return bool(re.match(pattern, value))

    def _check_enum(self, value: Any, allowed: List[Any]) -> bool:
        if value is None:
            return True
        return value in allowed

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


# =============================================================================
# CONVENIENCE FACTORY FUNCTIONS
# =============================================================================

def required(field: str, message: str = None) -> ValidationRule:
    """Create a 'required' rule."""
    return ValidationRule(field, "required", message=message)


def type_check(field: str, expected_type: str, message: str = None) -> ValidationRule:
    """Create a 'type' rule."""
    return ValidationRule(field, "type", {"type": expected_type}, message=message)


def range_check(field: str, min_val: float = None, max_val: float = None, message: str = None) -> ValidationRule:
    """Create a 'range' rule."""
    return ValidationRule(field, "range", {"min": min_val, "max": max_val}, message=message)


def pattern(field: str, regex: str, message: str = None) -> ValidationRule:
    """Create a 'pattern' rule."""
    return ValidationRule(field, "pattern", {"regex": regex}, message=message)


def enum_check(field: str, allowed: List[Any], message: str = None) -> ValidationRule:
    """Create an 'enum' rule."""
    return ValidationRule(field, "enum", {"values": allowed}, message=message)
