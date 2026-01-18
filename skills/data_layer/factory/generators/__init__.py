# fokha_data/factory/generators/__init__.py
# =============================================================================
# TEMPLATE: Data Generators Package
# =============================================================================
# Generators are responsible for producing actual data values.
# They take templates and produce concrete data based on the generation mode.
#
# Types:
#   - StaticGenerator: Deterministic, same output every time
#   - DynamicGenerator: Random/variable output each time
# =============================================================================

from .static_generator import StaticGenerator
from .dynamic_generator import DynamicGenerator

__all__ = [
    "StaticGenerator",
    "DynamicGenerator",
]
