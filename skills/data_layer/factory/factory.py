# fokha_data/factory/factory.py
# =============================================================================
# TEMPLATE: Data Factory
# =============================================================================
# The DataFactory is the main entry point for generating data.
# It coordinates generators and templates to produce DataRecords
# with the specified classification.
#
# Features:
#   - Generate single or multiple records
#   - Support for LIVE, MOCK, HYBRID sources
#   - Support for VALID, INVALID, EDGE_CASE validity
#   - Support for HIGH, NEUTRAL, LOW intensity
#   - Template-based generation
#   - Reproducible generation with seeds
# =============================================================================

from typing import List, Optional, Dict, Any, Type, TypeVar, Callable
from pathlib import Path
import json
import os

from ..models.enums import DataSource, Validity, Intensity, Origin, GenerationMode
from ..models.base import DataMeta, DataRecord, GenerationConfig

from .generators.static_generator import StaticGenerator
from .generators.dynamic_generator import DynamicGenerator

T = TypeVar('T')


class DataFactory:
    """
    Main factory for generating data records.

    The factory uses templates and generators to create data records
    with specific classification (source, validity, intensity).

    Attributes:
        templates_dir: Path to templates directory
        generators: Dictionary of available generators

    Usage:
        factory = DataFactory()

        # Generate a single mock record
        record = factory.generate_one(
            source=DataSource.MOCK,
            validity=Validity.VALID,
            intensity=Intensity.HIGH,
        )

        # Generate multiple records
        records = factory.generate(
            source=DataSource.MOCK,
            validity=Validity.VALID,
            count=10,
        )

        # Generate from template
        record = factory.from_template("market/ohlcv", overrides={"symbol": "AAPL"})
    """

    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the factory.

        Args:
            templates_dir: Path to templates directory. If None, uses default.
        """
        if templates_dir is None:
            # Default to templates/ in same directory as factory
            templates_dir = os.path.join(os.path.dirname(__file__), "templates")

        self.templates_dir = Path(templates_dir)
        self.generators = {
            GenerationMode.STATIC: StaticGenerator(),
            GenerationMode.DYNAMIC: DynamicGenerator(),
            GenerationMode.SEEDED: DynamicGenerator(),  # Will use seed
            GenerationMode.SEQUENTIAL: StaticGenerator(),  # Will increment
        }
        self._template_cache: Dict[str, Dict[str, Any]] = {}
        self._sequence_counters: Dict[str, int] = {}

    # =========================================================================
    # MAIN GENERATION METHODS
    # =========================================================================

    def generate_one(
        self,
        source: DataSource = DataSource.MOCK,
        validity: Validity = Validity.VALID,
        intensity: Intensity = Intensity.NEUTRAL,
        origin: Origin = Origin.INTERNAL,
        mode: GenerationMode = GenerationMode.STATIC,
        seed: Optional[int] = None,
        template_name: Optional[str] = None,
        payload_type: Optional[Type[T]] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> DataRecord[T]:
        """
        Generate a single data record.

        Args:
            source: Data source classification
            validity: Data validity classification
            intensity: Data intensity classification
            origin: Data origin classification
            mode: Generation mode (static/dynamic)
            seed: Random seed for reproducibility
            template_name: Name of template to use
            payload_type: Type of payload (for type hints)
            overrides: Field overrides for the payload

        Returns:
            A DataRecord with the specified classification
        """
        # Create metadata
        meta = DataMeta(
            source=source,
            validity=validity,
            intensity=intensity,
            origin=origin,
        )

        # Create generation config
        gen_config = GenerationConfig(
            mode=mode,
            seed=seed,
            count=1,
            template_name=template_name,
            overrides=overrides,
        )

        # Get generator
        generator = self.generators.get(mode, self.generators[GenerationMode.STATIC])

        # Load template if specified
        template_data = None
        if template_name:
            template_data = self._load_template(template_name, source, validity, intensity)

        # Generate payload
        if template_data:
            payload = generator.generate(
                template=template_data,
                overrides=overrides or {},
                seed=seed,
            )
        else:
            # Generate empty/default payload
            payload = generator.generate_default(overrides=overrides or {})

        # Create and return record
        return DataRecord(
            meta=meta,
            payload=payload,
            generation=gen_config,
        )

    def generate(
        self,
        count: int = 1,
        source: DataSource = DataSource.MOCK,
        validity: Validity = Validity.VALID,
        intensity: Intensity = Intensity.NEUTRAL,
        origin: Origin = Origin.INTERNAL,
        mode: GenerationMode = GenerationMode.STATIC,
        seed: Optional[int] = None,
        template_name: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
        unique: bool = False,
    ) -> List[DataRecord]:
        """
        Generate multiple data records.

        Args:
            count: Number of records to generate
            source: Data source classification
            validity: Data validity classification
            intensity: Data intensity classification
            origin: Data origin classification
            mode: Generation mode
            seed: Random seed (will increment for each record if seeded)
            template_name: Name of template to use
            overrides: Field overrides
            unique: If True, ensure each record has unique values

        Returns:
            List of DataRecords
        """
        records = []

        for i in range(count):
            record_seed = (seed + i) if seed is not None else None

            # For sequential mode, pass index as override
            record_overrides = overrides.copy() if overrides else {}
            if mode == GenerationMode.SEQUENTIAL:
                record_overrides["_sequence_index"] = i

            record = self.generate_one(
                source=source,
                validity=validity,
                intensity=intensity,
                origin=origin,
                mode=mode,
                seed=record_seed,
                template_name=template_name,
                overrides=record_overrides,
            )
            records.append(record)

        return records

    # =========================================================================
    # TEMPLATE METHODS
    # =========================================================================

    def from_template(
        self,
        template_name: str,
        source: DataSource = DataSource.MOCK,
        validity: Validity = Validity.VALID,
        intensity: Intensity = Intensity.NEUTRAL,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> DataRecord:
        """
        Generate a record from a named template.

        Template names follow the pattern:
            "{domain}/{type}" or "{source}/{validity}/{intensity}"

        Examples:
            - "market/ohlcv"
            - "mock/valid/high"
            - "user/profile"

        Args:
            template_name: Name/path of template
            source: Override source classification
            validity: Override validity classification
            intensity: Override intensity classification
            overrides: Field overrides

        Returns:
            DataRecord generated from template
        """
        return self.generate_one(
            source=source,
            validity=validity,
            intensity=intensity,
            template_name=template_name,
            overrides=overrides,
        )

    def _load_template(
        self,
        template_name: str,
        source: DataSource,
        validity: Validity,
        intensity: Intensity,
    ) -> Optional[Dict[str, Any]]:
        """
        Load a template from the templates directory.

        Looks for templates in order:
        1. {templates_dir}/{template_name}.json
        2. {templates_dir}/{source}/{validity}/{intensity}.json
        3. {templates_dir}/{source}/{validity}/default.json
        4. {templates_dir}/{source}/default.json

        Returns:
            Template data as dictionary, or None if not found
        """
        cache_key = f"{template_name}:{source.value}:{validity.value}:{intensity.value}"

        if cache_key in self._template_cache:
            return self._template_cache[cache_key]

        # Try different paths
        paths_to_try = [
            self.templates_dir / f"{template_name}.json",
            self.templates_dir / source.value / validity.value / f"{intensity.value}.json",
            self.templates_dir / source.value / validity.value / "default.json",
            self.templates_dir / source.value / "default.json",
            self.templates_dir / "default.json",
        ]

        for path in paths_to_try:
            if path.exists():
                with open(path, 'r') as f:
                    template_data = json.load(f)
                    self._template_cache[cache_key] = template_data
                    return template_data

        return None

    def register_template(self, name: str, template: Dict[str, Any]) -> None:
        """
        Register a template programmatically.

        Args:
            name: Template name/key
            template: Template data
        """
        self._template_cache[name] = template

    def list_templates(self) -> List[str]:
        """List all available template names."""
        templates = list(self._template_cache.keys())

        # Also scan templates directory
        if self.templates_dir.exists():
            for path in self.templates_dir.rglob("*.json"):
                rel_path = path.relative_to(self.templates_dir)
                name = str(rel_path).replace(".json", "").replace(os.sep, "/")
                if name not in templates:
                    templates.append(name)

        return sorted(templates)

    # =========================================================================
    # BATCH GENERATION
    # =========================================================================

    def generate_matrix(
        self,
        sources: Optional[List[DataSource]] = None,
        validities: Optional[List[Validity]] = None,
        intensities: Optional[List[Intensity]] = None,
        count_per_combination: int = 1,
        template_name: Optional[str] = None,
    ) -> List[DataRecord]:
        """
        Generate records for all combinations of classifications.

        Useful for comprehensive testing across all data types.

        Args:
            sources: List of sources (default: all)
            validities: List of validities (default: all)
            intensities: List of intensities (default: all)
            count_per_combination: Records per combination
            template_name: Template to use

        Returns:
            List of records covering all combinations
        """
        if sources is None:
            sources = [DataSource.LIVE, DataSource.MOCK]
        if validities is None:
            validities = [Validity.VALID, Validity.INVALID, Validity.EDGE_CASE]
        if intensities is None:
            intensities = [Intensity.HIGH, Intensity.NEUTRAL, Intensity.LOW]

        records = []
        for source in sources:
            for validity in validities:
                for intensity in intensities:
                    batch = self.generate(
                        count=count_per_combination,
                        source=source,
                        validity=validity,
                        intensity=intensity,
                        template_name=template_name,
                    )
                    records.extend(batch)

        return records

    def generate_test_suite(
        self,
        template_name: str,
        include_edge_cases: bool = True,
    ) -> Dict[str, List[DataRecord]]:
        """
        Generate a complete test suite with categorized records.

        Returns a dictionary with records organized by use case:
        - "happy_path": Valid, live data
        - "mock_valid": Valid mock data
        - "mock_invalid": Invalid mock data (for error testing)
        - "edge_cases": Edge case data
        - "stress_test": High intensity data

        Args:
            template_name: Template to use
            include_edge_cases: Whether to include edge cases

        Returns:
            Dictionary of categorized record lists
        """
        suite = {
            "happy_path": self.generate(
                count=5,
                source=DataSource.LIVE,
                validity=Validity.VALID,
                intensity=Intensity.NEUTRAL,
                template_name=template_name,
            ),
            "mock_valid": self.generate(
                count=10,
                source=DataSource.MOCK,
                validity=Validity.VALID,
                intensity=Intensity.NEUTRAL,
                template_name=template_name,
            ),
            "mock_invalid": self.generate(
                count=5,
                source=DataSource.MOCK,
                validity=Validity.INVALID,
                intensity=Intensity.NEUTRAL,
                template_name=template_name,
            ),
            "stress_test": self.generate(
                count=3,
                source=DataSource.MOCK,
                validity=Validity.VALID,
                intensity=Intensity.EXTREME,
                template_name=template_name,
            ),
        }

        if include_edge_cases:
            suite["edge_cases"] = self.generate(
                count=5,
                source=DataSource.MOCK,
                validity=Validity.EDGE_CASE,
                intensity=Intensity.HIGH,
                template_name=template_name,
            )

        return suite
