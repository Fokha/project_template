# fokha_data/models/base.py
# =============================================================================
# TEMPLATE: Base Data Models
# =============================================================================
# Core data structures used across the entire fokha_data layer.
# These are the building blocks for all domain-specific models.
#
# Classes:
#   - QualityScore: Granular quality metrics (validity, completeness, etc.)
#   - DataMeta: Metadata/classification for any data record
#   - GenerationConfig: Configuration for data generation (factory)
#   - DataRecord: Base class for all data records
# =============================================================================

from dataclasses import dataclass, field, asdict
from typing import Optional, Any, Dict, List, TypeVar, Generic
from datetime import datetime
import uuid
import json

from .enums import (
    DataSource,
    Validity,
    Intensity,
    Origin,
    GenerationMode,
    SchemaType,
)


# =============================================================================
# QUALITY SCORE
# =============================================================================

@dataclass
class QualityScore:
    """
    Granular quality metrics for data.
    Each metric is a float from 0.0 to 1.0.

    Attributes:
        validity: Does the data meet validation rules?
        completeness: Are all required fields present?
        accuracy: Are the values correct/accurate?
        freshness: How recent is the data?
        consistency: Is the data internally consistent?

    Usage:
        score = QualityScore(validity=0.95, completeness=1.0, accuracy=0.9)
        print(score.overall)  # "HIGH"
        print(score.average)  # 0.9625
    """
    validity: float = 1.0
    completeness: float = 1.0
    accuracy: float = 1.0
    freshness: float = 1.0
    consistency: float = 1.0

    def __post_init__(self):
        # Clamp all values to [0.0, 1.0]
        self.validity = max(0.0, min(1.0, self.validity))
        self.completeness = max(0.0, min(1.0, self.completeness))
        self.accuracy = max(0.0, min(1.0, self.accuracy))
        self.freshness = max(0.0, min(1.0, self.freshness))
        self.consistency = max(0.0, min(1.0, self.consistency))

    @property
    def average(self) -> float:
        """Calculate average quality score."""
        return (
            self.validity +
            self.completeness +
            self.accuracy +
            self.freshness +
            self.consistency
        ) / 5

    @property
    def overall(self) -> str:
        """Get overall quality level as string."""
        avg = self.average
        if avg >= 0.9:
            return "EXCELLENT"
        elif avg >= 0.75:
            return "HIGH"
        elif avg >= 0.5:
            return "MEDIUM"
        elif avg >= 0.25:
            return "LOW"
        else:
            return "POOR"

    @property
    def intensity(self) -> Intensity:
        """Convert to Intensity enum."""
        avg = self.average
        if avg >= 0.75:
            return Intensity.HIGH
        elif avg >= 0.4:
            return Intensity.NEUTRAL
        else:
            return Intensity.LOW

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "average": self.average,
            "overall": self.overall,
        }


# =============================================================================
# DATA METADATA
# =============================================================================

@dataclass
class DataMeta:
    """
    Metadata and classification for any data record.

    This is the core classification structure that categorizes data along
    multiple dimensions: source, validity, intensity, origin.

    Attributes:
        source: LIVE, MOCK, or HYBRID
        validity: VALID, INVALID, EDGE_CASE, PARTIAL
        intensity: HIGH, NEUTRAL, LOW, EXTREME
        origin: INTERNAL, EXTERNAL, USER, COMPUTED
        schema_type: PRIMITIVE, OBJECT, ARRAY, NESTED, BINARY
        version: Schema version string
        tags: Optional key-value tags for additional classification
        quality: Optional detailed quality scores

    Usage:
        meta = DataMeta(
            source=DataSource.LIVE,
            validity=Validity.VALID,
            intensity=Intensity.HIGH,
            origin=Origin.EXTERNAL,
        )
    """
    source: DataSource = DataSource.LIVE
    validity: Validity = Validity.VALID
    intensity: Intensity = Intensity.NEUTRAL
    origin: Origin = Origin.EXTERNAL
    schema_type: SchemaType = SchemaType.OBJECT
    version: str = "1.0.0"
    tags: Optional[Dict[str, str]] = None
    quality: Optional[QualityScore] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = {}

    @property
    def is_production_ready(self) -> bool:
        """Check if data is suitable for production use."""
        return (
            self.source == DataSource.LIVE and
            self.validity in (Validity.VALID, Validity.PARTIAL)
        )

    @property
    def is_test_data(self) -> bool:
        """Check if this is test/mock data."""
        return self.source in (DataSource.MOCK, DataSource.HYBRID)

    def with_tag(self, key: str, value: str) -> "DataMeta":
        """Return a new DataMeta with an additional tag."""
        new_tags = {**(self.tags or {}), key: value}
        return DataMeta(
            source=self.source,
            validity=self.validity,
            intensity=self.intensity,
            origin=self.origin,
            schema_type=self.schema_type,
            version=self.version,
            tags=new_tags,
            quality=self.quality,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source.value,
            "validity": self.validity.value,
            "intensity": self.intensity.value,
            "origin": self.origin.value,
            "schema_type": self.schema_type.value,
            "version": self.version,
            "tags": self.tags,
            "quality": self.quality.to_dict() if self.quality else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataMeta":
        return cls(
            source=DataSource(data.get("source", "live")),
            validity=Validity(data.get("validity", "valid")),
            intensity=Intensity(data.get("intensity", "neutral")),
            origin=Origin(data.get("origin", "external")),
            schema_type=SchemaType(data.get("schema_type", "object")),
            version=data.get("version", "1.0.0"),
            tags=data.get("tags"),
            quality=QualityScore(**data["quality"]) if data.get("quality") else None,
        )


# =============================================================================
# GENERATION CONFIG
# =============================================================================

@dataclass
class GenerationConfig:
    """
    Configuration for data generation (used by factory).

    Controls how the data factory generates data records.

    Attributes:
        mode: STATIC, DYNAMIC, SEEDED, SEQUENTIAL
        seed: Random seed for reproducibility (when mode is SEEDED)
        count: Number of records to generate
        template_name: Name of template to use (optional)
        overrides: Field overrides for generation

    Usage:
        config = GenerationConfig(
            mode=GenerationMode.SEEDED,
            seed=42,
            count=100,
        )
    """
    mode: GenerationMode = GenerationMode.STATIC
    seed: Optional[int] = None
    count: int = 1
    template_name: Optional[str] = None
    overrides: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.overrides is None:
            self.overrides = {}

    @property
    def is_reproducible(self) -> bool:
        """Check if generation will produce same results."""
        return self.mode.is_reproducible

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode.value,
            "seed": self.seed,
            "count": self.count,
            "template_name": self.template_name,
            "overrides": self.overrides,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenerationConfig":
        return cls(
            mode=GenerationMode(data.get("mode", "static")),
            seed=data.get("seed"),
            count=data.get("count", 1),
            template_name=data.get("template_name"),
            overrides=data.get("overrides"),
        )


# =============================================================================
# DATA RECORD (Generic Base)
# =============================================================================

T = TypeVar('T')


@dataclass
class DataRecord(Generic[T]):
    """
    Base class for all data records.

    Wraps any payload with metadata, timestamps, and unique ID.

    Attributes:
        id: Unique identifier (auto-generated UUID if not provided)
        meta: DataMeta classification
        payload: The actual data (generic type T)
        created_at: Creation timestamp
        updated_at: Last update timestamp
        generation: Optional generation config (for factory-created data)

    Usage:
        record = DataRecord(
            meta=DataMeta(source=DataSource.LIVE, validity=Validity.VALID),
            payload={"symbol": "AAPL", "price": 150.0},
        )
        print(record.id)  # "a1b2c3d4-..."
        print(record.is_valid)  # True
    """
    meta: DataMeta
    payload: T
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: Optional[str] = None
    generation: Optional[GenerationConfig] = None

    # Convenience properties
    @property
    def is_valid(self) -> bool:
        """Check if record has valid data."""
        return self.meta.validity in (Validity.VALID, Validity.PARTIAL)

    @property
    def is_live(self) -> bool:
        """Check if record is from live source."""
        return self.meta.source == DataSource.LIVE

    @property
    def is_mock(self) -> bool:
        """Check if record is mock/test data."""
        return self.meta.source == DataSource.MOCK

    @property
    def source(self) -> DataSource:
        """Shortcut to meta.source."""
        return self.meta.source

    @property
    def validity(self) -> Validity:
        """Shortcut to meta.validity."""
        return self.meta.validity

    @property
    def intensity(self) -> Intensity:
        """Shortcut to meta.intensity."""
        return self.meta.intensity

    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow().isoformat()

    def with_payload(self, new_payload: T) -> "DataRecord[T]":
        """Return a new record with updated payload."""
        return DataRecord(
            id=self.id,
            meta=self.meta,
            payload=new_payload,
            created_at=self.created_at,
            updated_at=datetime.utcnow().isoformat(),
            generation=self.generation,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "meta": self.meta.to_dict(),
            "payload": self.payload if not hasattr(self.payload, 'to_dict') else self.payload.to_dict(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "generation": self.generation.to_dict() if self.generation else None,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], payload_parser=None) -> "DataRecord":
        """
        Deserialize from dictionary.

        Args:
            data: Dictionary representation
            payload_parser: Optional function to parse payload
        """
        payload = data.get("payload")
        if payload_parser and payload:
            payload = payload_parser(payload)

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            meta=DataMeta.from_dict(data.get("meta", {})),
            payload=payload,
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at"),
            generation=GenerationConfig.from_dict(data["generation"]) if data.get("generation") else None,
        )


# =============================================================================
# FACTORY METHODS
# =============================================================================

def create_live_record(payload: T, intensity: Intensity = Intensity.NEUTRAL) -> DataRecord[T]:
    """Quick factory for creating live/production records."""
    return DataRecord(
        meta=DataMeta(
            source=DataSource.LIVE,
            validity=Validity.VALID,
            intensity=intensity,
            origin=Origin.EXTERNAL,
        ),
        payload=payload,
    )


def create_mock_record(
    payload: T,
    validity: Validity = Validity.VALID,
    intensity: Intensity = Intensity.NEUTRAL,
) -> DataRecord[T]:
    """Quick factory for creating mock/test records."""
    return DataRecord(
        meta=DataMeta(
            source=DataSource.MOCK,
            validity=validity,
            intensity=intensity,
            origin=Origin.INTERNAL,
        ),
        payload=payload,
        generation=GenerationConfig(mode=GenerationMode.STATIC),
    )
