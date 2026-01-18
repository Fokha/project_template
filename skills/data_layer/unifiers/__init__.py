# fokha_data/unifiers/__init__.py
# =============================================================================
# TEMPLATE: Data Unifiers Package
# =============================================================================
# Tools for combining, merging, and deduplicating data from multiple sources.
#
# Components:
#   - Merger: Combine data from multiple sources
#   - Normalizer: Standardize data formats
#   - Deduplicator: Remove duplicate records
# =============================================================================

from .merger import Merger, MergeConfig
from .normalizer import Normalizer, NormalizeConfig
from .deduplicator import Deduplicator, DedupeConfig

__all__ = [
    "Merger",
    "MergeConfig",
    "Normalizer",
    "NormalizeConfig",
    "Deduplicator",
    "DedupeConfig",
]
