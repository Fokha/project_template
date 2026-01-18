# fokha_data/factory/__init__.py
# =============================================================================
# TEMPLATE: Data Factory Package
# =============================================================================
# The factory package provides tools for generating test data, mock data,
# and simulated data for testing, development, and validation purposes.
#
# Key Components:
#   - DataFactory: Main factory class for generating records
#   - StaticGenerator: Deterministic, repeatable generation
#   - DynamicGenerator: Randomized, variable generation
#   - Templates: Pre-defined data shapes in JSON format
#
# USAGE:
#   from fokha_data.factory import DataFactory, StaticGenerator
#
#   factory = DataFactory()
#   records = factory.generate(
#       source=DataSource.MOCK,
#       validity=Validity.VALID,
#       intensity=Intensity.HIGH,
#       count=10,
#   )
# =============================================================================

from .factory import DataFactory
from .generators.static_generator import StaticGenerator
from .generators.dynamic_generator import DynamicGenerator

__all__ = [
    "DataFactory",
    "StaticGenerator",
    "DynamicGenerator",
]
