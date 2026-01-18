# fokha_data/tests/test_example.py
# =============================================================================
# TEMPLATE: Example Tests
# =============================================================================
# Example tests demonstrating how to test fokha_data components.
# Copy and adapt these patterns for your project.
# =============================================================================

import unittest
from datetime import datetime

# Import from fokha_data
import sys
sys.path.insert(0, '..')

from models import DataRecord, DataMeta, DataSource, Validity, Intensity
from factory import DataFactory
from processors import Validator, ValidationRule, Formatter
from storage import MemoryStorage, QueryOptions
from pipeline import Pipeline, Stage


class TestDataModels(unittest.TestCase):
    """Test data models."""

    def test_create_data_record(self):
        """Test creating a DataRecord."""
        meta = DataMeta(
            source=DataSource.LIVE,
            validity=Validity.VALID,
            intensity=Intensity.HIGH,
        )
        record = DataRecord(
            meta=meta,
            payload={"test": "data"},
        )

        self.assertIsNotNone(record.id)
        self.assertTrue(record.is_valid)
        self.assertTrue(record.is_live)
        self.assertEqual(record.source, DataSource.LIVE)

    def test_data_meta_properties(self):
        """Test DataMeta convenience properties."""
        live_meta = DataMeta(source=DataSource.LIVE, validity=Validity.VALID)
        mock_meta = DataMeta(source=DataSource.MOCK, validity=Validity.INVALID)

        self.assertTrue(live_meta.is_production_ready)
        self.assertFalse(mock_meta.is_production_ready)
        self.assertTrue(mock_meta.is_test_data)


class TestDataFactory(unittest.TestCase):
    """Test data factory."""

    def setUp(self):
        self.factory = DataFactory()

    def test_generate_one(self):
        """Test generating a single record."""
        record = self.factory.generate_one(
            source=DataSource.MOCK,
            validity=Validity.VALID,
        )

        self.assertIsNotNone(record)
        self.assertEqual(record.source, DataSource.MOCK)
        self.assertEqual(record.validity, Validity.VALID)

    def test_generate_batch(self):
        """Test generating multiple records."""
        records = self.factory.generate(count=10)

        self.assertEqual(len(records), 10)
        for record in records:
            self.assertIsNotNone(record.id)

    def test_generate_matrix(self):
        """Test generating all combinations."""
        records = self.factory.generate_matrix(
            sources=[DataSource.LIVE, DataSource.MOCK],
            validities=[Validity.VALID, Validity.INVALID],
            intensities=[Intensity.HIGH, Intensity.LOW],
            count_per_combination=1,
        )

        # 2 sources * 2 validities * 2 intensities = 8 combinations
        self.assertEqual(len(records), 8)


class TestValidator(unittest.TestCase):
    """Test validator."""

    def setUp(self):
        self.validator = Validator()
        self.validator.add_rules([
            ValidationRule("name", "required"),
            ValidationRule("age", "range", {"min": 0, "max": 150}),
            ValidationRule("email", "pattern", {"regex": r".+@.+"}),
        ])

    def test_valid_data(self):
        """Test validation of valid data."""
        data = {
            "name": "John",
            "age": 30,
            "email": "john@example.com",
        }
        result = self.validator.validate(data)

        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

    def test_invalid_data(self):
        """Test validation of invalid data."""
        data = {
            "name": None,  # Required
            "age": 200,    # Out of range
            "email": "invalid",  # Bad format
        }
        result = self.validator.validate(data)

        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)


class TestStorage(unittest.TestCase):
    """Test storage implementations."""

    def setUp(self):
        self.storage = MemoryStorage()
        self.storage.connect()

    def tearDown(self):
        self.storage.disconnect()

    def test_save_and_get(self):
        """Test saving and retrieving records."""
        record = {"id": "test-1", "name": "Test"}
        record_id = self.storage.save(record)

        retrieved = self.storage.get(record_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["name"], "Test")

    def test_find_with_filter(self):
        """Test querying with filters."""
        self.storage.save({"id": "1", "status": "active"})
        self.storage.save({"id": "2", "status": "inactive"})
        self.storage.save({"id": "3", "status": "active"})

        results = self.storage.find(QueryOptions().eq("status", "active"))
        self.assertEqual(len(results), 2)

    def test_delete(self):
        """Test deleting records."""
        self.storage.save({"id": "to-delete", "name": "Test"})
        self.assertTrue(self.storage.exists("to-delete"))

        self.storage.delete("to-delete")
        self.assertFalse(self.storage.exists("to-delete"))


class TestPipeline(unittest.TestCase):
    """Test pipeline orchestration."""

    def test_simple_pipeline(self):
        """Test a simple pipeline."""
        pipeline = (Pipeline("test")
            .add_stage(Stage("double", lambda x: x * 2))
            .add_stage(Stage("add_ten", lambda x: x + 10)))

        result = pipeline.execute(5)

        self.assertTrue(result.success)
        self.assertEqual(result.data, 20)  # (5 * 2) + 10

    def test_pipeline_failure(self):
        """Test pipeline failure handling."""
        def failing_stage(x):
            raise ValueError("Intentional failure")

        pipeline = (Pipeline("failing")
            .add_stage(Stage("ok", lambda x: x))
            .add_stage(Stage("fail", failing_stage))
            .add_stage(Stage("never_runs", lambda x: x)))

        result = pipeline.execute("test")

        self.assertFalse(result.success)
        self.assertIn("fail", result.failed_stages)

    def test_conditional_stage(self):
        """Test stage with condition."""
        pipeline = Pipeline("conditional")
        pipeline.add_stage(Stage(
            "only_positive",
            lambda x: x * 2,
            condition=lambda x: x > 0,
        ))

        # Should execute
        result = pipeline.execute(5)
        self.assertEqual(result.data, 10)

        # Should skip
        pipeline.reset()
        result = pipeline.execute(-5)
        self.assertEqual(result.data, -5)  # Unchanged


if __name__ == "__main__":
    unittest.main()
