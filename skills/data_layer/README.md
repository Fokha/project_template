# fokha_data - Unified Data Layer Template

A comprehensive, reusable data layer template for building consistent, testable, and maintainable data pipelines.

## Overview

`fokha_data` provides a complete foundation for data handling across all Fokha projects:

- **Classification System**: Categorize data by source (live/mock), validity (valid/invalid), and intensity (high/neutral/low)
- **Factory Pattern**: Generate test data with static or dynamic generators
- **Processing Pipeline**: Validate, format, sort, and transform data
- **Storage Abstraction**: Unified interface for memory, file, and database storage
- **Pipeline Orchestration**: Compose stages into complete data workflows

## Installation

Copy this template to your project:

```bash
cp -r fokha_data/ /your/project/
```

## Quick Start

```python
from fokha_data import (
    DataRecord, DataMeta, DataSource, Validity,
    DataFactory, Validator, Pipeline, Stage,
    MemoryStorage
)

# 1. Create a data record with classification
record = DataRecord(
    meta=DataMeta(
        source=DataSource.LIVE,
        validity=Validity.VALID,
        intensity=Intensity.HIGH,
    ),
    payload={"symbol": "AAPL", "price": 150.0}
)

# 2. Generate test data
factory = DataFactory()
test_records = factory.generate(
    count=10,
    source=DataSource.MOCK,
    validity=Validity.VALID,
)

# 3. Build a processing pipeline
validator = Validator()
validator.add_rule(ValidationRule("symbol", "required"))

storage = MemoryStorage()
storage.connect()

pipeline = (Pipeline("data_processing")
    .add_stage(Stage("validate", validator.validate))
    .add_stage(Stage("store", storage.save)))

result = pipeline.execute(record)

if result.success:
    print(f"Processed in {result.total_duration_ms}ms")
```

## Architecture

```
fokha_data/
├── models/           # Data models and classification
│   ├── enums.py      # DataSource, Validity, Intensity, etc.
│   └── base.py       # DataMeta, DataRecord, QualityScore
│
├── factory/          # Test data generation
│   ├── factory.py    # DataFactory main class
│   ├── generators/   # Static and Dynamic generators
│   └── templates/    # JSON templates by classification
│
├── processors/       # Data transformation
│   ├── validator.py  # Rule-based validation
│   ├── formatter.py  # Format normalization
│   ├── sorter.py     # Sorting and grouping
│   └── transformer.py # Business logic transforms
│
├── unifiers/         # Data consolidation
│   ├── merger.py     # Combine multiple sources
│   ├── normalizer.py # Standardize formats
│   └── deduplicator.py # Remove duplicates
│
├── storage/          # Persistence layer
│   ├── interfaces/   # BaseStorage contract
│   ├── implementations/  # Memory, File, SQLite
│   └── repositories/ # Higher-level data access
│
├── pipeline/         # Orchestration
│   ├── orchestrator.py # Pipeline coordinator
│   ├── stages/       # Individual pipeline steps
│   ├── requester.py  # Data fetching
│   └── gatherer.py   # Multi-source collection
│
└── contracts/        # JSON Schema definitions
    ├── data_record.schema.json
    ├── validation_result.schema.json
    └── pipeline_result.schema.json
```

## Data Classification

Every piece of data is classified along multiple dimensions:

| Dimension | Values | Purpose |
|-----------|--------|---------|
| **Source** | `LIVE`, `MOCK`, `HYBRID` | Distinguish production vs test data |
| **Validity** | `VALID`, `INVALID`, `EDGE_CASE`, `PARTIAL` | Data quality status |
| **Intensity** | `HIGH`, `NEUTRAL`, `LOW`, `EXTREME` | Severity/magnitude level |
| **Origin** | `INTERNAL`, `EXTERNAL`, `USER`, `COMPUTED` | Where data came from |

### Usage

```python
from fokha_data import DataMeta, DataSource, Validity, Intensity

# Production data
live_meta = DataMeta(
    source=DataSource.LIVE,
    validity=Validity.VALID,
    intensity=Intensity.HIGH,
)

# Test data
mock_meta = DataMeta(
    source=DataSource.MOCK,
    validity=Validity.INVALID,  # For error testing
    intensity=Intensity.NEUTRAL,
)
```

## Factory - Test Data Generation

Generate consistent test data with the factory pattern:

```python
from fokha_data import DataFactory, DataSource, Validity

factory = DataFactory()

# Generate single record
record = factory.generate_one(
    source=DataSource.MOCK,
    validity=Validity.VALID,
)

# Generate batch
records = factory.generate(
    count=100,
    source=DataSource.MOCK,
    validity=Validity.VALID,
    intensity=Intensity.HIGH,
)

# Generate test suite
suite = factory.generate_test_suite("my_template")
# Returns: happy_path, mock_valid, mock_invalid, edge_cases, stress_test

# Generate all combinations (for comprehensive testing)
matrix = factory.generate_matrix(
    sources=[DataSource.LIVE, DataSource.MOCK],
    validities=[Validity.VALID, Validity.INVALID],
    count_per_combination=5,
)
```

### Templates

Define templates in `factory/templates/`:

```json
// templates/mock/valid/high.json
{
  "_meta": {
    "description": "High intensity valid mock data"
  },
  "id": "{uuid}",
  "timestamp": "{now}",
  "data": {
    "value": {"_type": "float", "_min": 900, "_max": 1000},
    "confidence": 0.95
  }
}
```

## Processors

### Validator

```python
from fokha_data import Validator, ValidationRule, required, range_check

validator = Validator()
validator.add_rules([
    required("name"),
    range_check("age", min_val=0, max_val=150),
    ValidationRule("email", "pattern", {"regex": r".*@.*"}),
])

result = validator.validate(data)
if not result.is_valid:
    for error in result.errors:
        print(f"{error.field}: {error.message}")
```

### Formatter

```python
from fokha_data import Formatter, trim, round_to, default_value

formatter = Formatter()
formatter.add_format(trim("name"))
formatter.add_format(round_to("price", decimals=2))
formatter.add_format(default_value("status", "pending"))

formatted = formatter.format(data)
```

### Transformer

```python
from fokha_data import Transformer

transformer = (Transformer()
    .rename("old_field", "new_field")
    .compute("full_name", lambda x: f"{x['first']} {x['last']}")
    .remove("internal_id", "debug_info"))

transformed = transformer.apply(data)
```

## Storage

All storage backends implement the same interface:

```python
from fokha_data import MemoryStorage, SQLiteStorage, QueryOptions

# In-memory (testing)
storage = MemoryStorage()

# SQLite (production)
storage = SQLiteStorage("data.db")

# Common interface
storage.connect()
storage.save(record)
storage.get(record_id)
storage.find(QueryOptions().eq("status", "active"))
storage.delete(record_id)
storage.disconnect()
```

## Pipeline

Compose processing stages into pipelines:

```python
from fokha_data import Pipeline, Stage

pipeline = (Pipeline("etl_pipeline")
    .add_stage(Stage("extract", fetch_data))
    .add_stage(Stage("validate", validator.validate))
    .add_stage(Stage("transform", transformer.transform))
    .add_stage(Stage("load", storage.save)))

result = pipeline.execute(input_data)

print(f"Success: {result.success}")
print(f"Duration: {result.total_duration_ms}ms")
print(f"Stages: {result.stage_results}")
```

## Applying to Existing Projects

### Migration Strategy

1. **Copy template** to your project
2. **Adapt models** to your domain (add domain-specific models)
3. **Create templates** for your test data
4. **Replace existing** data handling with fokha_data components
5. **Standardize** across all projects

### Integration with AI_STUDIO

```python
# In python_ml/models/, extend fokha_data models
from fokha_data import DataRecord, DataMeta

class MarketDataRecord(DataRecord):
    """Market data with trading-specific fields."""
    pass

# Use factory for test data
factory = DataFactory(templates_dir="path/to/trading_templates")
test_signals = factory.generate(source=DataSource.MOCK, count=1000)
```

### Integration with FOKHA_APPS

```python
# In packages/fokha_core/, use fokha_data for shared models
from fokha_data import DataMeta, Validity

# Validate incoming data
validator = Validator()
validator.add_rules(api_validation_rules)
```

## License

Fokha Technologies - Internal Use

---

**Version**: 1.0.0
**Created**: January 2026
