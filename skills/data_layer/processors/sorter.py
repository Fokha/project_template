# fokha_data/processors/sorter.py
# =============================================================================
# TEMPLATE: Data Sorter
# =============================================================================
# Sorts and organizes data collections.
# Supports multi-key sorting, custom comparators, and grouping.
#
# Features:
#   - Sort by single or multiple fields
#   - Ascending/descending order
#   - Custom sort functions
#   - Grouping by field
#   - Stable sorting
# =============================================================================

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable, Union
from enum import Enum


class SortOrder(Enum):
    """Sort order direction."""
    ASC = "asc"
    DESC = "desc"
    ASCENDING = "asc"
    DESCENDING = "desc"


@dataclass
class SortKey:
    """
    A single sort key configuration.

    Attributes:
        field: Field path to sort by (dot notation)
        order: Sort order (asc/desc)
        null_position: Where to put null values ("first" or "last")
    """
    field: str
    order: SortOrder = SortOrder.ASC
    null_position: str = "last"  # "first" or "last"

    @property
    def is_ascending(self) -> bool:
        return self.order in (SortOrder.ASC, SortOrder.ASCENDING)


@dataclass
class SortConfig:
    """
    Configuration for sorting.

    Attributes:
        keys: List of sort keys (in priority order)
        stable: Whether to use stable sort
    """
    keys: List[SortKey] = field(default_factory=list)
    stable: bool = True

    def add_key(self, field: str, order: SortOrder = SortOrder.ASC) -> "SortConfig":
        self.keys.append(SortKey(field, order))
        return self


class Sorter:
    """
    Sorts data collections.

    Usage:
        sorter = Sorter()

        # Simple sort
        sorted_data = sorter.sort(data, "created_at", SortOrder.DESC)

        # Multi-key sort
        config = SortConfig()
        config.add_key("category", SortOrder.ASC)
        config.add_key("priority", SortOrder.DESC)
        config.add_key("name", SortOrder.ASC)

        sorted_data = sorter.sort_by_config(data, config)

        # Group by
        groups = sorter.group_by(data, "category")
    """

    def __init__(self):
        self.custom_comparators: Dict[str, Callable] = {}

    # =========================================================================
    # SORTING
    # =========================================================================

    def sort(
        self,
        data: List[Dict[str, Any]],
        field: str,
        order: SortOrder = SortOrder.ASC,
        null_position: str = "last",
    ) -> List[Dict[str, Any]]:
        """
        Sort data by a single field.

        Args:
            data: List of dictionaries to sort
            field: Field to sort by
            order: Sort order
            null_position: Where to place null values

        Returns:
            Sorted list
        """
        config = SortConfig(keys=[SortKey(field, order, null_position)])
        return self.sort_by_config(data, config)

    def sort_by_config(
        self,
        data: List[Dict[str, Any]],
        config: SortConfig,
    ) -> List[Dict[str, Any]]:
        """
        Sort data by configuration with multiple keys.

        Args:
            data: List of dictionaries to sort
            config: Sort configuration

        Returns:
            Sorted list
        """
        if not config.keys:
            return data

        def make_sort_key(item: Dict[str, Any]):
            """Create a composite sort key for an item."""
            keys = []
            for sort_key in config.keys:
                value = self._get_nested_value(item, sort_key.field)

                # Handle null values
                if value is None:
                    # Use min/max placeholders based on null_position and order
                    if sort_key.null_position == "first":
                        null_val = (0,)  # Tuple sorts before any value
                    else:
                        null_val = (2,)  # Tuple sorts after any value

                    if not sort_key.is_ascending:
                        null_val = (2,) if sort_key.null_position == "first" else (0,)

                    keys.append(null_val)
                else:
                    # Wrap value for consistent comparison
                    if sort_key.is_ascending:
                        keys.append((1, value))
                    else:
                        keys.append((1, self._negate_for_reverse(value)))

            return tuple(keys)

        return sorted(data, key=make_sort_key)

    def sort_records(
        self,
        records: List[Any],
        field: str,
        order: SortOrder = SortOrder.ASC,
    ) -> List[Any]:
        """
        Sort DataRecord objects by payload field.

        Args:
            records: List of DataRecord objects
            field: Payload field to sort by
            order: Sort order

        Returns:
            Sorted list of records
        """
        def get_value(record):
            payload = record.payload if hasattr(record, 'payload') else record
            if isinstance(payload, dict):
                return self._get_nested_value(payload, field)
            return payload

        reverse = order in (SortOrder.DESC, SortOrder.DESCENDING)
        return sorted(records, key=get_value, reverse=reverse)

    # =========================================================================
    # GROUPING
    # =========================================================================

    def group_by(
        self,
        data: List[Dict[str, Any]],
        field: str,
        sort_groups: bool = True,
    ) -> Dict[Any, List[Dict[str, Any]]]:
        """
        Group data by a field value.

        Args:
            data: List of dictionaries
            field: Field to group by
            sort_groups: Whether to sort group keys

        Returns:
            Dictionary mapping field values to lists of items
        """
        groups: Dict[Any, List[Dict[str, Any]]] = {}

        for item in data:
            key = self._get_nested_value(item, field)
            if key not in groups:
                groups[key] = []
            groups[key].append(item)

        if sort_groups:
            # Sort by keys
            return dict(sorted(groups.items(), key=lambda x: (x[0] is None, x[0])))

        return groups

    def group_and_sort(
        self,
        data: List[Dict[str, Any]],
        group_field: str,
        sort_field: str,
        sort_order: SortOrder = SortOrder.ASC,
    ) -> Dict[Any, List[Dict[str, Any]]]:
        """
        Group data and sort within each group.

        Args:
            data: List of dictionaries
            group_field: Field to group by
            sort_field: Field to sort by within groups
            sort_order: Sort order within groups

        Returns:
            Dictionary of sorted groups
        """
        groups = self.group_by(data, group_field, sort_groups=True)

        for key in groups:
            groups[key] = self.sort(groups[key], sort_field, sort_order)

        return groups

    # =========================================================================
    # CUSTOM COMPARATORS
    # =========================================================================

    def register_comparator(self, name: str, func: Callable[[Any, Any], int]) -> "Sorter":
        """
        Register a custom comparator function.

        Args:
            name: Name to reference the comparator
            func: Function(a, b) -> -1, 0, or 1
        """
        self.custom_comparators[name] = func
        return self

    def sort_with_comparator(
        self,
        data: List[Dict[str, Any]],
        comparator_name: str,
        field: str = None,
    ) -> List[Dict[str, Any]]:
        """
        Sort using a custom comparator.

        Args:
            data: List to sort
            comparator_name: Name of registered comparator
            field: Optional field to extract for comparison
        """
        from functools import cmp_to_key

        if comparator_name not in self.custom_comparators:
            raise ValueError(f"Unknown comparator: {comparator_name}")

        comparator = self.custom_comparators[comparator_name]

        if field:
            def field_comparator(a, b):
                val_a = self._get_nested_value(a, field)
                val_b = self._get_nested_value(b, field)
                return comparator(val_a, val_b)
            return sorted(data, key=cmp_to_key(field_comparator))
        else:
            return sorted(data, key=cmp_to_key(comparator))

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

    def _negate_for_reverse(self, value: Any) -> Any:
        """Negate a value for reverse sorting."""
        if isinstance(value, (int, float)):
            return -value
        elif isinstance(value, str):
            # Create a string that sorts in reverse
            return tuple(-ord(c) for c in value)
        elif isinstance(value, bool):
            return not value
        else:
            # For other types, wrap in tuple with flag
            return (value,)


# =============================================================================
# CONVENIENCE FACTORY FUNCTIONS
# =============================================================================

def asc(field: str) -> SortKey:
    """Create ascending sort key."""
    return SortKey(field, SortOrder.ASC)


def desc(field: str) -> SortKey:
    """Create descending sort key."""
    return SortKey(field, SortOrder.DESC)


def create_sort_config(*keys: SortKey) -> SortConfig:
    """Create sort config from multiple keys."""
    return SortConfig(keys=list(keys))
