# ═══════════════════════════════════════════════════════════════
# MODEL PERSISTENCE TEMPLATE
# Save, load, and version ML models
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Use ModelRegistry to save/load models
# 3. Track model versions and metadata
#
# ═══════════════════════════════════════════════════════════════

import joblib
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════


@dataclass
class ModelMetadata:
    """Metadata for a saved model."""
    model_name: str
    version: str
    created_at: str
    model_type: str
    accuracy: float
    feature_columns: List[str]
    hyperparameters: Dict[str, Any]
    training_samples: int
    file_hash: str
    description: str = ""
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class ModelArtifact:
    """Complete model artifact with all components."""
    model: Any                          # The trained model
    scaler: Any = None                  # Feature scaler
    feature_columns: List[str] = None   # Feature names
    metadata: ModelMetadata = None      # Model metadata
    config: Dict = None                 # Training config


# ═══════════════════════════════════════════════════════════════
# MODEL REGISTRY
# ═══════════════════════════════════════════════════════════════


class ModelRegistry:
    """
    Registry for saving, loading, and versioning ML models.

    Features:
    - Automatic versioning
    - Metadata tracking
    - Model comparison
    - Rollback support
    """

    def __init__(self, registry_path: str = "models"):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.registry_path / "registry_index.json"
        self._load_index()

    def _load_index(self):
        """Load or create registry index."""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {"models": {}, "latest": {}}

    def _save_index(self):
        """Save registry index."""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)

    def save(
        self,
        artifact: ModelArtifact,
        model_name: str,
        description: str = "",
        tags: List[str] = None
    ) -> str:
        """
        Save a model artifact with automatic versioning.

        Args:
            artifact: ModelArtifact containing model and components
            model_name: Name for the model
            description: Optional description
            tags: Optional tags for organization

        Returns:
            Version string (e.g., "v1", "v2")
        """
        # Determine version
        if model_name in self.index["models"]:
            versions = self.index["models"][model_name]
            latest_version = max(int(v[1:]) for v in versions.keys())
            version = f"v{latest_version + 1}"
        else:
            self.index["models"][model_name] = {}
            version = "v1"

        # Create model directory
        model_dir = self.registry_path / model_name / version
        model_dir.mkdir(parents=True, exist_ok=True)

        # Save model file
        model_file = model_dir / "model.pkl"
        joblib.dump(artifact.model, model_file)

        # Save scaler if present
        if artifact.scaler is not None:
            scaler_file = model_dir / "scaler.pkl"
            joblib.dump(artifact.scaler, scaler_file)

        # Calculate file hash
        file_hash = self._calculate_hash(model_file)

        # Create metadata
        metadata = ModelMetadata(
            model_name=model_name,
            version=version,
            created_at=datetime.utcnow().isoformat(),
            model_type=type(artifact.model).__name__,
            accuracy=artifact.metadata.accuracy if artifact.metadata else 0.0,
            feature_columns=artifact.feature_columns or [],
            hyperparameters=artifact.config or {},
            training_samples=artifact.metadata.training_samples if artifact.metadata else 0,
            file_hash=file_hash,
            description=description,
            tags=tags or [],
        )

        # Save metadata
        metadata_file = model_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(asdict(metadata), f, indent=2)

        # Update index
        self.index["models"][model_name][version] = {
            "path": str(model_dir),
            "created_at": metadata.created_at,
            "accuracy": metadata.accuracy,
        }
        self.index["latest"][model_name] = version
        self._save_index()

        logger.info(f"Saved model: {model_name} {version}")
        return version

    def load(
        self,
        model_name: str,
        version: str = None
    ) -> ModelArtifact:
        """
        Load a model artifact.

        Args:
            model_name: Name of the model
            version: Specific version or None for latest

        Returns:
            ModelArtifact with all components
        """
        if model_name not in self.index["models"]:
            raise ValueError(f"Model not found: {model_name}")

        # Get version
        if version is None:
            version = self.index["latest"].get(model_name)
            if version is None:
                raise ValueError(f"No versions found for: {model_name}")

        if version not in self.index["models"][model_name]:
            raise ValueError(f"Version not found: {model_name} {version}")

        # Load files
        model_dir = Path(self.index["models"][model_name][version]["path"])

        model = joblib.load(model_dir / "model.pkl")

        scaler = None
        scaler_file = model_dir / "scaler.pkl"
        if scaler_file.exists():
            scaler = joblib.load(scaler_file)

        with open(model_dir / "metadata.json", 'r') as f:
            metadata_dict = json.load(f)
            metadata = ModelMetadata(**metadata_dict)

        logger.info(f"Loaded model: {model_name} {version}")

        return ModelArtifact(
            model=model,
            scaler=scaler,
            feature_columns=metadata.feature_columns,
            metadata=metadata,
            config=metadata.hyperparameters,
        )

    def load_latest(self, model_name: str) -> ModelArtifact:
        """Load the latest version of a model."""
        return self.load(model_name, version=None)

    def list_models(self) -> List[str]:
        """List all registered model names."""
        return list(self.index["models"].keys())

    def list_versions(self, model_name: str) -> List[Dict]:
        """List all versions of a model."""
        if model_name not in self.index["models"]:
            return []

        versions = []
        for version, info in self.index["models"][model_name].items():
            versions.append({
                "version": version,
                "created_at": info["created_at"],
                "accuracy": info.get("accuracy", 0),
                "is_latest": version == self.index["latest"].get(model_name),
            })

        return sorted(versions, key=lambda x: x["version"], reverse=True)

    def get_metadata(self, model_name: str, version: str = None) -> ModelMetadata:
        """Get metadata for a specific model version."""
        if version is None:
            version = self.index["latest"].get(model_name)

        model_dir = Path(self.index["models"][model_name][version]["path"])
        with open(model_dir / "metadata.json", 'r') as f:
            return ModelMetadata(**json.load(f))

    def compare_versions(
        self,
        model_name: str,
        version1: str,
        version2: str
    ) -> Dict:
        """Compare two model versions."""
        meta1 = self.get_metadata(model_name, version1)
        meta2 = self.get_metadata(model_name, version2)

        return {
            "version1": version1,
            "version2": version2,
            "accuracy_diff": meta2.accuracy - meta1.accuracy,
            "created_diff_days": (
                datetime.fromisoformat(meta2.created_at) -
                datetime.fromisoformat(meta1.created_at)
            ).days,
            "hyperparameter_changes": self._diff_dicts(
                meta1.hyperparameters,
                meta2.hyperparameters
            ),
        }

    def rollback(self, model_name: str, version: str):
        """Set a specific version as the latest."""
        if model_name not in self.index["models"]:
            raise ValueError(f"Model not found: {model_name}")
        if version not in self.index["models"][model_name]:
            raise ValueError(f"Version not found: {version}")

        self.index["latest"][model_name] = version
        self._save_index()
        logger.info(f"Rolled back {model_name} to {version}")

    def delete_version(self, model_name: str, version: str):
        """Delete a specific model version."""
        if model_name not in self.index["models"]:
            raise ValueError(f"Model not found: {model_name}")
        if version not in self.index["models"][model_name]:
            raise ValueError(f"Version not found: {version}")

        # Don't delete latest
        if self.index["latest"].get(model_name) == version:
            raise ValueError("Cannot delete latest version. Rollback first.")

        # Delete files
        model_dir = Path(self.index["models"][model_name][version]["path"])
        shutil.rmtree(model_dir)

        # Update index
        del self.index["models"][model_name][version]
        self._save_index()

        logger.info(f"Deleted: {model_name} {version}")

    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _diff_dicts(self, d1: Dict, d2: Dict) -> Dict:
        """Find differences between two dictionaries."""
        changes = {}
        all_keys = set(d1.keys()) | set(d2.keys())

        for key in all_keys:
            v1 = d1.get(key)
            v2 = d2.get(key)
            if v1 != v2:
                changes[key] = {"old": v1, "new": v2}

        return changes


# ═══════════════════════════════════════════════════════════════
# QUICK SAVE/LOAD FUNCTIONS
# ═══════════════════════════════════════════════════════════════


def quick_save(
    model: Any,
    path: str,
    scaler: Any = None,
    feature_columns: List[str] = None,
    metadata: Dict = None
):
    """
    Quick save without registry.

    Saves model, scaler, and metadata as a single pickle file.
    """
    artifact = {
        "model": model,
        "scaler": scaler,
        "feature_columns": feature_columns,
        "metadata": metadata or {},
        "saved_at": datetime.utcnow().isoformat(),
    }

    joblib.dump(artifact, path)
    logger.info(f"Saved model to: {path}")


def quick_load(path: str) -> Tuple[Any, Any, List[str]]:
    """
    Quick load without registry.

    Returns:
        Tuple of (model, scaler, feature_columns)
    """
    artifact = joblib.load(path)

    return (
        artifact["model"],
        artifact.get("scaler"),
        artifact.get("feature_columns", [])
    )


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    import numpy as np

    # Create sample model
    X = np.random.randn(100, 5)
    y = np.random.randint(0, 2, 100)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_scaled, y)

    # Create artifact
    artifact = ModelArtifact(
        model=model,
        scaler=scaler,
        feature_columns=["f1", "f2", "f3", "f4", "f5"],
        metadata=ModelMetadata(
            model_name="signal_classifier",
            version="v1",
            created_at=datetime.utcnow().isoformat(),
            model_type="RandomForestClassifier",
            accuracy=0.85,
            feature_columns=["f1", "f2", "f3", "f4", "f5"],
            hyperparameters={"n_estimators": 100},
            training_samples=100,
            file_hash="",
        ),
        config={"n_estimators": 100},
    )

    # Initialize registry
    registry = ModelRegistry("test_models")

    # Save model (creates v1)
    v1 = registry.save(artifact, "signal_classifier", description="Initial model")
    print(f"Saved: {v1}")

    # Save again (creates v2)
    artifact.metadata.accuracy = 0.87
    v2 = registry.save(artifact, "signal_classifier", description="Improved model")
    print(f"Saved: {v2}")

    # List versions
    print(f"\nVersions:")
    for v in registry.list_versions("signal_classifier"):
        print(f"  {v['version']}: accuracy={v['accuracy']:.2f}, latest={v['is_latest']}")

    # Load latest
    loaded = registry.load_latest("signal_classifier")
    print(f"\nLoaded: {loaded.metadata.model_name} {loaded.metadata.version}")
    print(f"Accuracy: {loaded.metadata.accuracy}")

    # Compare versions
    comparison = registry.compare_versions("signal_classifier", "v1", "v2")
    print(f"\nComparison v1 vs v2:")
    print(f"  Accuracy improvement: {comparison['accuracy_diff']:.2f}")
