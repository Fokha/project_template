# fokha_data/unifiers/deduplicator.py
# =============================================================================
# TEMPLATE: Data Deduplicator
# =============================================================================
# Removes duplicate records from data collections.
# =============================================================================

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable, Set
from enum import Enum
import hashlib
import json


class DedupeStrategy(Enum):
    """Strategy for identifying duplicates."""
    EXACT = "exact"           # Exact match on all fields
    KEY = "key"               # Match on specific key fields
    HASH = "hash"             # Hash-based comparison
    CUSTOM = "custom"         # Custom comparison function


class KeepStrategy(Enum):
    """Which duplicate to keep."""
    FIRST = "first"
    LAST = "last"
    NEWEST = "newest"         # By timestamp field
    OLDEST = "oldest"


@dataclass
class DedupeConfig:
    """Configuration for deduplication."""
    strategy: DedupeStrategy = DedupeStrategy.KEY
    key_fields: List[str] = field(default_factory=lambda: ["id"])
    keep: KeepStrategy = KeepStrategy.FIRST
    timestamp_field: str = "created_at"
    custom_comparator: Optional[Callable[[Any, Any], bool]] = None


class Deduplicator:
    """
    Removes duplicate records.

    Usage:
        deduper = Deduplicator()

        # Dedupe by ID
        unique = deduper.dedupe(records)

        # Dedupe by multiple fields
        unique = deduper.dedupe(
            records,
            DedupeConfig(key_fields=["email", "phone"])
        )

        # Keep newest
        unique = deduper.dedupe(
            records,
            DedupeConfig(
                keep=KeepStrategy.NEWEST,
                timestamp_field="updated_at"
            )
        )
    """

    def __init__(self, default_config: Optional[DedupeConfig] = None):
        self.default_config = default_config or DedupeConfig()

    def dedupe(
        self,
        records: List[Any],
        config: Optional[DedupeConfig] = None,
    ) -> List[Any]:
        """
        Remove duplicates from records.

        Args:
            records: List of records
            config: Deduplication configuration

        Returns:
            List with duplicates removed
        """
        config = config or self.default_config

        if config.strategy == DedupeStrategy.EXACT:
            return self._dedupe_exact(records, config)
        elif config.strategy == DedupeStrategy.KEY:
            return self._dedupe_by_key(records, config)
        elif config.strategy == DedupeStrategy.HASH:
            return self._dedupe_by_hash(records, config)
        elif config.strategy == DedupeStrategy.CUSTOM:
            return self._dedupe_custom(records, config)

        return records

    def find_duplicates(
        self,
        records: List[Any],
        config: Optional[DedupeConfig] = None,
    ) -> Dict[str, List[Any]]:
        """
        Find and group duplicates.

        Returns:
            Dictionary mapping keys to lists of duplicate records
        """
        config = config or self.default_config
        groups: Dict[str, List[Any]] = {}

        for record in records:
            key = self._get_key(record, config)
            if key not in groups:
                groups[key] = []
            groups[key].append(record)

        # Filter to only groups with duplicates
        return {k: v for k, v in groups.items() if len(v) > 1}

    def _dedupe_exact(self, records: List[Any], config: DedupeConfig) -> List[Any]:
        """Dedupe by exact match."""
        seen: Set[str] = set()
        result = []

        for record in records:
            # Create hash of entire record
            record_hash = self._hash_record(record)

            if record_hash not in seen:
                seen.add(record_hash)
                result.append(record)
            elif config.keep == KeepStrategy.LAST:
                # Find and replace
                for i, r in enumerate(result):
                    if self._hash_record(r) == record_hash:
                        result[i] = record
                        break

        return result

    def _dedupe_by_key(self, records: List[Any], config: DedupeConfig) -> List[Any]:
        """Dedupe by key fields."""
        seen: Dict[str, Any] = {}

        for record in records:
            key = self._get_key(record, config)

            if key not in seen:
                seen[key] = record
            else:
                # Decide which to keep
                if config.keep == KeepStrategy.LAST:
                    seen[key] = record
                elif config.keep in (KeepStrategy.NEWEST, KeepStrategy.OLDEST):
                    existing = seen[key]
                    existing_ts = self._get_timestamp(existing, config.timestamp_field)
                    new_ts = self._get_timestamp(record, config.timestamp_field)

                    if existing_ts and new_ts:
                        if config.keep == KeepStrategy.NEWEST and new_ts > existing_ts:
                            seen[key] = record
                        elif config.keep == KeepStrategy.OLDEST and new_ts < existing_ts:
                            seen[key] = record

        return list(seen.values())

    def _dedupe_by_hash(self, records: List[Any], config: DedupeConfig) -> List[Any]:
        """Dedupe by content hash."""
        seen: Dict[str, Any] = {}

        for record in records:
            record_hash = self._hash_record(record)

            if record_hash not in seen:
                seen[record_hash] = record
            elif config.keep == KeepStrategy.LAST:
                seen[record_hash] = record

        return list(seen.values())

    def _dedupe_custom(self, records: List[Any], config: DedupeConfig) -> List[Any]:
        """Dedupe with custom comparator."""
        if not config.custom_comparator:
            return records

        result = []
        for record in records:
            is_duplicate = False
            for existing in result:
                if config.custom_comparator(record, existing):
                    is_duplicate = True
                    if config.keep == KeepStrategy.LAST:
                        result.remove(existing)
                        result.append(record)
                    break

            if not is_duplicate:
                result.append(record)

        return result

    def _get_key(self, record: Any, config: DedupeConfig) -> str:
        """Get deduplication key for a record."""
        values = []
        for field in config.key_fields:
            value = self._get_field_value(record, field)
            values.append(str(value))
        return "|".join(values)

    def _get_field_value(self, record: Any, field: str) -> Any:
        """Get field value from record."""
        if hasattr(record, field):
            return getattr(record, field)
        if isinstance(record, dict):
            keys = field.split(".")
            current = record
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return None
            return current
        return None

    def _get_timestamp(self, record: Any, field: str) -> Optional[str]:
        """Get timestamp from record."""
        return self._get_field_value(record, field)

    def _hash_record(self, record: Any) -> str:
        """Create hash of record content."""
        if hasattr(record, 'to_dict'):
            data = record.to_dict()
        elif isinstance(record, dict):
            data = record
        else:
            data = str(record)

        content = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(content.encode()).hexdigest()
