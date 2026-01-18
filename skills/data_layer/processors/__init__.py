# fokha_data/processors/__init__.py
# =============================================================================
# TEMPLATE: Data Processors Package
# =============================================================================
# Processors transform, validate, and format data as it flows through
# the pipeline. Each processor handles a specific transformation step.
#
# Components:
#   - Validator: Validates data against rules/schemas
#   - Formatter: Normalizes data format
#   - Sorter: Sorts and organizes data
#   - Transformer: Applies business logic transformations
#
# USAGE:
#   from fokha_data.processors import Validator, Formatter, Transformer
#
#   validator = Validator()
#   result = validator.validate(record)
#
#   formatter = Formatter()
#   formatted = formatter.format(record)
# =============================================================================

from .validator import Validator, ValidationResult, ValidationRule
from .formatter import Formatter, FormatConfig
from .sorter import Sorter, SortConfig
from .transformer import Transformer, TransformConfig

__all__ = [
    "Validator",
    "ValidationResult",
    "ValidationRule",
    "Formatter",
    "FormatConfig",
    "Sorter",
    "SortConfig",
    "Transformer",
    "TransformConfig",
]
