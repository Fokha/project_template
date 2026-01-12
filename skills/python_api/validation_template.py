# ═══════════════════════════════════════════════════════════════
# VALIDATION TEMPLATE
# Input validation patterns for Flask APIs
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Define schemas for your endpoints
# 3. Use @validate decorator on endpoints
#
# ═══════════════════════════════════════════════════════════════

import re
import logging
from typing import Dict, List, Any, Optional, Callable, Union, Type
from dataclasses import dataclass, field
from functools import wraps
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# VALIDATION ERRORS
# ═══════════════════════════════════════════════════════════════


class ValidationError(Exception):
    """Raised when validation fails."""

    def __init__(self, errors: List[Dict]):
        self.errors = errors
        super().__init__(str(errors))


@dataclass
class FieldError:
    """Single field validation error."""
    field: str
    message: str
    value: Any = None
    code: str = "invalid"

    def to_dict(self) -> Dict:
        return {
            "field": self.field,
            "message": self.message,
            "code": self.code,
        }


# ═══════════════════════════════════════════════════════════════
# FIELD VALIDATORS
# ═══════════════════════════════════════════════════════════════


class Validator:
    """Base validator class."""

    def __init__(self, message: str = None):
        self.message = message

    def __call__(self, value: Any, field_name: str) -> Optional[FieldError]:
        raise NotImplementedError


class Required(Validator):
    """Validate that field is present and not None."""

    def __call__(self, value: Any, field_name: str) -> Optional[FieldError]:
        if value is None:
            return FieldError(
                field=field_name,
                message=self.message or f"{field_name} is required",
                code="required"
            )
        return None


class TypeCheck(Validator):
    """Validate field type."""

    def __init__(self, expected_type: Type, message: str = None):
        super().__init__(message)
        self.expected_type = expected_type

    def __call__(self, value: Any, field_name: str) -> Optional[FieldError]:
        if value is not None and not isinstance(value, self.expected_type):
            return FieldError(
                field=field_name,
                message=self.message or f"{field_name} must be {self.expected_type.__name__}",
                value=value,
                code="type_error"
            )
        return None


class MinLength(Validator):
    """Validate minimum string length."""

    def __init__(self, min_len: int, message: str = None):
        super().__init__(message)
        self.min_len = min_len

    def __call__(self, value: Any, field_name: str) -> Optional[FieldError]:
        if value is not None and len(str(value)) < self.min_len:
            return FieldError(
                field=field_name,
                message=self.message or f"{field_name} must be at least {self.min_len} characters",
                value=value,
                code="min_length"
            )
        return None


class MaxLength(Validator):
    """Validate maximum string length."""

    def __init__(self, max_len: int, message: str = None):
        super().__init__(message)
        self.max_len = max_len

    def __call__(self, value: Any, field_name: str) -> Optional[FieldError]:
        if value is not None and len(str(value)) > self.max_len:
            return FieldError(
                field=field_name,
                message=self.message or f"{field_name} must be at most {self.max_len} characters",
                value=value,
                code="max_length"
            )
        return None


class Range(Validator):
    """Validate numeric range."""

    def __init__(self, min_val: float = None, max_val: float = None, message: str = None):
        super().__init__(message)
        self.min_val = min_val
        self.max_val = max_val

    def __call__(self, value: Any, field_name: str) -> Optional[FieldError]:
        if value is None:
            return None

        try:
            num = float(value)
            if self.min_val is not None and num < self.min_val:
                return FieldError(
                    field=field_name,
                    message=self.message or f"{field_name} must be at least {self.min_val}",
                    value=value,
                    code="min_value"
                )
            if self.max_val is not None and num > self.max_val:
                return FieldError(
                    field=field_name,
                    message=self.message or f"{field_name} must be at most {self.max_val}",
                    value=value,
                    code="max_value"
                )
        except (TypeError, ValueError):
            return FieldError(
                field=field_name,
                message=f"{field_name} must be a number",
                value=value,
                code="type_error"
            )
        return None


class Pattern(Validator):
    """Validate against regex pattern."""

    def __init__(self, pattern: str, message: str = None):
        super().__init__(message)
        self.pattern = re.compile(pattern)

    def __call__(self, value: Any, field_name: str) -> Optional[FieldError]:
        if value is not None and not self.pattern.match(str(value)):
            return FieldError(
                field=field_name,
                message=self.message or f"{field_name} format is invalid",
                value=value,
                code="pattern"
            )
        return None


class Email(Validator):
    """Validate email format."""

    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    def __call__(self, value: Any, field_name: str) -> Optional[FieldError]:
        if value is not None and not self.EMAIL_PATTERN.match(str(value)):
            return FieldError(
                field=field_name,
                message=self.message or f"{field_name} must be a valid email",
                value=value,
                code="email"
            )
        return None


class OneOf(Validator):
    """Validate that value is one of allowed choices."""

    def __init__(self, choices: List[Any], message: str = None):
        super().__init__(message)
        self.choices = choices

    def __call__(self, value: Any, field_name: str) -> Optional[FieldError]:
        if value is not None and value not in self.choices:
            return FieldError(
                field=field_name,
                message=self.message or f"{field_name} must be one of: {', '.join(map(str, self.choices))}",
                value=value,
                code="choice"
            )
        return None


class DateTime(Validator):
    """Validate ISO datetime format."""

    def __init__(self, format: str = None, message: str = None):
        super().__init__(message)
        self.format = format

    def __call__(self, value: Any, field_name: str) -> Optional[FieldError]:
        if value is None:
            return None

        try:
            if self.format:
                datetime.strptime(str(value), self.format)
            else:
                datetime.fromisoformat(str(value))
        except ValueError:
            return FieldError(
                field=field_name,
                message=self.message or f"{field_name} must be a valid datetime",
                value=value,
                code="datetime"
            )
        return None


class Custom(Validator):
    """Custom validation function."""

    def __init__(self, func: Callable[[Any], bool], message: str):
        super().__init__(message)
        self.func = func

    def __call__(self, value: Any, field_name: str) -> Optional[FieldError]:
        if value is not None and not self.func(value):
            return FieldError(
                field=field_name,
                message=self.message,
                value=value,
                code="custom"
            )
        return None


# ═══════════════════════════════════════════════════════════════
# SCHEMA DEFINITION
# ═══════════════════════════════════════════════════════════════


@dataclass
class Field:
    """Schema field definition."""
    validators: List[Validator] = field(default_factory=list)
    default: Any = None
    transform: Callable = None  # Transform value after validation

    def validate(self, value: Any, field_name: str) -> List[FieldError]:
        """Validate field value."""
        errors = []
        for validator in self.validators:
            error = validator(value, field_name)
            if error:
                errors.append(error)
                # Stop on first error for this field
                if isinstance(validator, Required):
                    break
        return errors


class Schema:
    """
    Validation schema for request data.

    Example:
        schema = Schema({
            'email': Field([Required(), Email()]),
            'name': Field([Required(), MinLength(2), MaxLength(100)]),
            'age': Field([Range(0, 150)]),
        })

        errors = schema.validate(request_data)
    """

    def __init__(self, fields: Dict[str, Field], allow_extra: bool = False):
        self.fields = fields
        self.allow_extra = allow_extra

    def validate(self, data: Dict) -> List[FieldError]:
        """Validate data against schema."""
        errors = []
        data = data or {}

        # Validate defined fields
        for field_name, field_def in self.fields.items():
            value = data.get(field_name, field_def.default)
            field_errors = field_def.validate(value, field_name)
            errors.extend(field_errors)

        # Check for extra fields
        if not self.allow_extra:
            extra = set(data.keys()) - set(self.fields.keys())
            for field_name in extra:
                errors.append(FieldError(
                    field=field_name,
                    message=f"Unknown field: {field_name}",
                    code="unknown_field"
                ))

        return errors

    def clean(self, data: Dict) -> Dict:
        """Validate and transform data."""
        data = data or {}
        result = {}

        for field_name, field_def in self.fields.items():
            value = data.get(field_name, field_def.default)

            # Apply transform if defined
            if value is not None and field_def.transform:
                value = field_def.transform(value)

            result[field_name] = value

        return result


# ═══════════════════════════════════════════════════════════════
# FLASK DECORATOR
# ═══════════════════════════════════════════════════════════════


def validate(schema: Schema, source: str = 'json'):
    """
    Decorator to validate request data.

    Args:
        schema: Validation schema
        source: Data source ('json', 'args', 'form')

    Example:
        @app.route('/users', methods=['POST'])
        @validate(user_schema)
        def create_user():
            data = request.validated_data
            # data is validated and cleaned
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            from flask import request, jsonify

            # Get data from appropriate source
            if source == 'json':
                data = request.get_json(silent=True) or {}
            elif source == 'args':
                data = request.args.to_dict()
            elif source == 'form':
                data = request.form.to_dict()
            else:
                data = {}

            # Validate
            errors = schema.validate(data)

            if errors:
                return jsonify({
                    "success": False,
                    "error": "VALIDATION_ERROR",
                    "message": "Validation failed",
                    "details": [e.to_dict() for e in errors],
                }), 400

            # Store cleaned data
            request.validated_data = schema.clean(data)

            return f(*args, **kwargs)
        return decorated
    return decorator


# ═══════════════════════════════════════════════════════════════
# COMMON SCHEMAS
# ═══════════════════════════════════════════════════════════════


# Pagination schema
pagination_schema = Schema({
    'page': Field([Range(1, 10000)], default=1, transform=int),
    'per_page': Field([Range(1, 100)], default=20, transform=int),
    'sort': Field([MaxLength(50)]),
    'order': Field([OneOf(['asc', 'desc'])], default='desc'),
}, allow_extra=True)


# Trading symbol schema
symbol_schema = Schema({
    'symbol': Field([
        Required(),
        Pattern(r'^[A-Z]{3,10}(USD)?$', "Invalid symbol format"),
    ], transform=str.upper),
})


# Date range schema
date_range_schema = Schema({
    'start_date': Field([DateTime()]),
    'end_date': Field([DateTime()]),
})


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    print("=" * 60)
    print("VALIDATION TEMPLATE DEMO")
    print("=" * 60)

    # Define a user schema
    user_schema = Schema({
        'email': Field([Required(), Email()]),
        'name': Field([Required(), MinLength(2), MaxLength(100)]),
        'age': Field([Range(0, 150)], transform=int),
        'role': Field([OneOf(['admin', 'user', 'guest'])], default='user'),
    })

    # Test valid data
    print("\n--- Valid Data ---")
    valid_data = {
        'email': 'test@example.com',
        'name': 'John Doe',
        'age': '30',
        'role': 'admin',
    }
    errors = user_schema.validate(valid_data)
    print(f"Errors: {errors}")
    print(f"Cleaned: {user_schema.clean(valid_data)}")

    # Test invalid data
    print("\n--- Invalid Data ---")
    invalid_data = {
        'email': 'not-an-email',
        'name': 'J',
        'age': 200,
        'role': 'superuser',
    }
    errors = user_schema.validate(invalid_data)
    for error in errors:
        print(f"  {error.field}: {error.message}")

    # Test missing required fields
    print("\n--- Missing Fields ---")
    missing_data = {'age': 25}
    errors = user_schema.validate(missing_data)
    for error in errors:
        print(f"  {error.field}: {error.message}")

    # Test custom validator
    print("\n--- Custom Validator ---")

    def is_even(value):
        return value % 2 == 0

    custom_schema = Schema({
        'number': Field([Required(), Custom(is_even, "Must be an even number")]),
    })

    print(f"5 is even: {custom_schema.validate({'number': 5})}")
    print(f"6 is even: {custom_schema.validate({'number': 6})}")
