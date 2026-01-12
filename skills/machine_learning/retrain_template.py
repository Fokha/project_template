# ═══════════════════════════════════════════════════════════════
# SCHEDULED RETRAINING TEMPLATE
# Automated model retraining with performance monitoring
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Configure retraining schedule
# 3. Set up as cron job or LaunchAgent
#
# Why Scheduled Retraining?
# - Models degrade over time (concept drift)
# - Market conditions change
# - New data improves predictions
# - Automated maintenance reduces manual work
#
# ═══════════════════════════════════════════════════════════════

import os
import json
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, f1_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════


@dataclass
class RetrainConfig:
    """Configuration for scheduled retraining."""
    model_name: str
    schedule: str = "weekly"              # daily, weekly, monthly
    min_new_samples: int = 100            # Minimum new samples to trigger
    performance_threshold: float = 0.65   # Retrain if accuracy drops below
    max_days_since_retrain: int = 14      # Force retrain after N days
    validation_split: float = 0.2         # Holdout for validation
    n_cv_folds: int = 5                   # Cross-validation folds
    notify_on_retrain: bool = True        # Send notifications


@dataclass
class RetrainResult:
    """Result of a retraining run."""
    model_name: str
    timestamp: datetime
    triggered_by: str               # scheduled, performance_drop, manual, new_data
    old_accuracy: float
    new_accuracy: float
    improvement: float
    samples_used: int
    training_time: float
    success: bool
    error_message: str = ""
    metadata: Dict = field(default_factory=dict)


@dataclass
class ModelHealth:
    """Health status of a model."""
    model_name: str
    last_retrain: datetime
    days_since_retrain: int
    current_accuracy: float
    samples_since_retrain: int
    needs_retrain: bool
    reason: str


# ═══════════════════════════════════════════════════════════════
# PERFORMANCE TRACKER
# ═══════════════════════════════════════════════════════════════


class PerformanceTracker:
    """
    Track model performance over time.

    Monitors prediction accuracy to detect degradation.
    """

    def __init__(self, storage_path: str = "performance_logs"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.predictions: List[Dict] = []

    def log_prediction(
        self,
        model_name: str,
        prediction: int,
        actual: int = None,
        confidence: float = None,
        features: Dict = None
    ):
        """Log a prediction for later evaluation."""
        record = {
            "model_name": model_name,
            "timestamp": datetime.utcnow().isoformat(),
            "prediction": prediction,
            "actual": actual,
            "confidence": confidence,
            "features_hash": self._hash_features(features) if features else None,
        }
        self.predictions.append(record)

        # Persist periodically
        if len(self.predictions) % 100 == 0:
            self._save_predictions(model_name)

    def update_actual(self, model_name: str, timestamp: str, actual: int):
        """Update actual outcome for a prediction."""
        for pred in self.predictions:
            if (pred["model_name"] == model_name and
                pred["timestamp"] == timestamp and
                pred["actual"] is None):
                pred["actual"] = actual
                break

    def get_recent_accuracy(
        self,
        model_name: str,
        days: int = 7
    ) -> Tuple[float, int]:
        """
        Calculate recent accuracy.

        Returns:
            Tuple of (accuracy, sample_count)
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()

        recent = [
            p for p in self.predictions
            if (p["model_name"] == model_name and
                p["timestamp"] >= cutoff_str and
                p["actual"] is not None)
        ]

        if not recent:
            return 0.0, 0

        correct = sum(1 for p in recent if p["prediction"] == p["actual"])
        return correct / len(recent), len(recent)

    def get_accuracy_trend(
        self,
        model_name: str,
        window_days: int = 7,
        periods: int = 4
    ) -> List[float]:
        """Get accuracy over multiple time periods."""
        trend = []
        for i in range(periods):
            end = datetime.utcnow() - timedelta(days=i * window_days)
            start = end - timedelta(days=window_days)

            relevant = [
                p for p in self.predictions
                if (p["model_name"] == model_name and
                    start.isoformat() <= p["timestamp"] < end.isoformat() and
                    p["actual"] is not None)
            ]

            if relevant:
                acc = sum(1 for p in relevant if p["prediction"] == p["actual"]) / len(relevant)
                trend.append(acc)
            else:
                trend.append(None)

        return trend

    def _hash_features(self, features: Dict) -> str:
        """Create hash of features for deduplication."""
        return hashlib.md5(json.dumps(features, sort_keys=True).encode()).hexdigest()[:8]

    def _save_predictions(self, model_name: str):
        """Save predictions to disk."""
        file_path = self.storage_path / f"{model_name}_predictions.jsonl"
        with open(file_path, 'a') as f:
            for pred in self.predictions[-100:]:
                if pred["model_name"] == model_name:
                    f.write(json.dumps(pred) + "\n")


# ═══════════════════════════════════════════════════════════════
# SCHEDULED RETRAINER
# ═══════════════════════════════════════════════════════════════


class ScheduledRetrainer:
    """
    Automated model retraining system.

    Features:
    - Performance-triggered retraining
    - Time-based scheduled retraining
    - New data triggered retraining
    - Validation before deployment
    - Rollback on failure
    """

    def __init__(
        self,
        config: RetrainConfig,
        model_factory: Callable,
        data_loader: Callable,
        model_saver: Callable = None,
        model_loader: Callable = None,
        notifier: Callable = None
    ):
        """
        Initialize retrainer.

        Args:
            config: RetrainConfig
            model_factory: Function to create new model instance
            data_loader: Function to load training data
            model_saver: Function to save trained model
            model_loader: Function to load existing model
            notifier: Function to send notifications
        """
        self.config = config
        self.model_factory = model_factory
        self.data_loader = data_loader
        self.model_saver = model_saver
        self.model_loader = model_loader
        self.notifier = notifier

        self.tracker = PerformanceTracker()
        self.history: List[RetrainResult] = []
        self.current_model = None
        self.last_retrain: datetime = None

        # Load metadata
        self._load_metadata()

    def check_health(self) -> ModelHealth:
        """Check if model needs retraining."""
        # Calculate days since last retrain
        days_since = 0
        if self.last_retrain:
            days_since = (datetime.utcnow() - self.last_retrain).days

        # Get recent accuracy
        accuracy, samples = self.tracker.get_recent_accuracy(
            self.config.model_name, days=7
        )

        # Determine if retraining needed
        needs_retrain = False
        reason = ""

        if self.last_retrain is None:
            needs_retrain = True
            reason = "Never trained"
        elif days_since >= self.config.max_days_since_retrain:
            needs_retrain = True
            reason = f"Max days exceeded ({days_since} days)"
        elif accuracy < self.config.performance_threshold and samples >= 20:
            needs_retrain = True
            reason = f"Accuracy dropped ({accuracy:.2%} < {self.config.performance_threshold:.2%})"
        elif samples >= self.config.min_new_samples:
            # Check for accuracy trend decline
            trend = self.tracker.get_accuracy_trend(self.config.model_name)
            if len(trend) >= 2 and trend[0] is not None and trend[1] is not None:
                if trend[0] < trend[1] * 0.95:  # 5% decline
                    needs_retrain = True
                    reason = f"Accuracy declining ({trend[1]:.2%} → {trend[0]:.2%})"

        return ModelHealth(
            model_name=self.config.model_name,
            last_retrain=self.last_retrain,
            days_since_retrain=days_since,
            current_accuracy=accuracy,
            samples_since_retrain=samples,
            needs_retrain=needs_retrain,
            reason=reason,
        )

    def retrain(self, force: bool = False) -> RetrainResult:
        """
        Execute retraining if needed.

        Args:
            force: Force retraining regardless of health check

        Returns:
            RetrainResult
        """
        start_time = datetime.utcnow()

        # Check if retraining needed
        health = self.check_health()
        if not force and not health.needs_retrain:
            logger.info(f"Retraining not needed for {self.config.model_name}")
            return RetrainResult(
                model_name=self.config.model_name,
                timestamp=start_time,
                triggered_by="skipped",
                old_accuracy=health.current_accuracy,
                new_accuracy=health.current_accuracy,
                improvement=0.0,
                samples_used=0,
                training_time=0.0,
                success=False,
                error_message="Retraining not needed",
            )

        triggered_by = "manual" if force else health.reason
        logger.info(f"Starting retraining for {self.config.model_name}: {triggered_by}")

        try:
            # Load data
            X, y = self.data_loader()
            logger.info(f"Loaded {len(X)} samples")

            # Get baseline accuracy
            old_accuracy = health.current_accuracy

            # Split data
            split_idx = int(len(X) * (1 - self.config.validation_split))
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]

            # Cross-validation
            cv = TimeSeriesSplit(n_splits=self.config.n_cv_folds)
            cv_scores = []

            for fold, (train_idx, test_idx) in enumerate(cv.split(X_train)):
                model = self.model_factory()
                model.fit(X_train[train_idx], y_train[train_idx])
                pred = model.predict(X_train[test_idx])
                score = accuracy_score(y_train[test_idx], pred)
                cv_scores.append(score)
                logger.info(f"Fold {fold + 1}: {score:.4f}")

            cv_mean = np.mean(cv_scores)
            logger.info(f"CV Mean: {cv_mean:.4f}")

            # Train final model
            final_model = self.model_factory()
            final_model.fit(X_train, y_train)

            # Validate
            val_pred = final_model.predict(X_val)
            new_accuracy = accuracy_score(y_val, val_pred)
            logger.info(f"Validation accuracy: {new_accuracy:.4f}")

            # Check if improvement
            improvement = new_accuracy - old_accuracy if old_accuracy > 0 else 0

            # Decide whether to deploy
            should_deploy = (
                new_accuracy >= self.config.performance_threshold or
                (old_accuracy > 0 and new_accuracy >= old_accuracy * 0.95)  # Allow small decline
            )

            if should_deploy:
                # Save old model as backup
                if self.current_model and self.model_saver:
                    self.model_saver(
                        self.current_model,
                        f"{self.config.model_name}_backup"
                    )

                # Deploy new model
                self.current_model = final_model
                if self.model_saver:
                    self.model_saver(final_model, self.config.model_name)

                self.last_retrain = datetime.utcnow()
                self._save_metadata()

                logger.info(f"Deployed new model with accuracy {new_accuracy:.4f}")
            else:
                logger.warning(
                    f"Model not deployed: {new_accuracy:.4f} below threshold"
                )

            training_time = (datetime.utcnow() - start_time).total_seconds()

            result = RetrainResult(
                model_name=self.config.model_name,
                timestamp=start_time,
                triggered_by=triggered_by,
                old_accuracy=old_accuracy,
                new_accuracy=new_accuracy,
                improvement=improvement,
                samples_used=len(X),
                training_time=training_time,
                success=should_deploy,
                metadata={
                    "cv_scores": cv_scores,
                    "cv_mean": cv_mean,
                    "deployed": should_deploy,
                },
            )

        except Exception as e:
            logger.error(f"Retraining failed: {e}")
            training_time = (datetime.utcnow() - start_time).total_seconds()

            result = RetrainResult(
                model_name=self.config.model_name,
                timestamp=start_time,
                triggered_by=triggered_by,
                old_accuracy=health.current_accuracy,
                new_accuracy=0.0,
                improvement=0.0,
                samples_used=0,
                training_time=training_time,
                success=False,
                error_message=str(e),
            )

        # Save result
        self.history.append(result)

        # Send notification
        if self.config.notify_on_retrain and self.notifier:
            self._send_notification(result)

        return result

    def _send_notification(self, result: RetrainResult):
        """Send notification about retraining result."""
        if result.success:
            message = (
                f"Model Retrained: {result.model_name}\n"
                f"Accuracy: {result.old_accuracy:.2%} → {result.new_accuracy:.2%}\n"
                f"Improvement: {result.improvement:+.2%}\n"
                f"Samples: {result.samples_used}\n"
                f"Time: {result.training_time:.1f}s"
            )
        else:
            message = (
                f"Retraining Failed: {result.model_name}\n"
                f"Error: {result.error_message}"
            )

        try:
            self.notifier(message)
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

    def _load_metadata(self):
        """Load metadata from disk."""
        metadata_path = Path(f"retrain_metadata_{self.config.model_name}.json")
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                data = json.load(f)
                if data.get("last_retrain"):
                    self.last_retrain = datetime.fromisoformat(data["last_retrain"])

    def _save_metadata(self):
        """Save metadata to disk."""
        metadata_path = Path(f"retrain_metadata_{self.config.model_name}.json")
        with open(metadata_path, 'w') as f:
            json.dump({
                "model_name": self.config.model_name,
                "last_retrain": self.last_retrain.isoformat() if self.last_retrain else None,
            }, f)


# ═══════════════════════════════════════════════════════════════
# CRON JOB RUNNER
# ═══════════════════════════════════════════════════════════════


class CronRetrainRunner:
    """
    Run scheduled retraining as a cron job.

    Example crontab entry:
    0 2 * * 0 python retrain_template.py --run  # Every Sunday at 2 AM
    """

    def __init__(self, retrainers: List[ScheduledRetrainer]):
        self.retrainers = retrainers

    def run_all(self, force: bool = False) -> List[RetrainResult]:
        """Run retraining for all models."""
        results = []

        for retrainer in self.retrainers:
            logger.info(f"Checking {retrainer.config.model_name}...")
            health = retrainer.check_health()

            if force or health.needs_retrain:
                logger.info(f"Retraining: {health.reason}")
                result = retrainer.retrain(force=force)
                results.append(result)
            else:
                logger.info(f"Skipping: No retraining needed")

        return results

    def generate_report(self, results: List[RetrainResult]) -> str:
        """Generate summary report."""
        lines = [
            "=" * 60,
            "SCHEDULED RETRAINING REPORT",
            f"Time: {datetime.utcnow().isoformat()}",
            "=" * 60,
            "",
        ]

        for result in results:
            status = "" if result.success else ""
            lines.append(f"{status} {result.model_name}")
            lines.append(f"   Triggered by: {result.triggered_by}")
            lines.append(f"   Accuracy: {result.old_accuracy:.2%} → {result.new_accuracy:.2%}")
            if result.error_message:
                lines.append(f"   Error: {result.error_message}")
            lines.append("")

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification

    # Sample data loader
    def load_data():
        X, y = make_classification(
            n_samples=1000,
            n_features=20,
            n_informative=10,
            random_state=42
        )
        return X, y

    # Sample model factory
    def create_model():
        return RandomForestClassifier(n_estimators=100, random_state=42)

    # Sample notifier
    def send_notification(message: str):
        print(f"\n[NOTIFICATION]\n{message}\n")

    # Sample model saver
    def save_model(model, name: str):
        logger.info(f"Saving model: {name}")
        # In production: joblib.dump(model, f"models/{name}.pkl")

    # Configure retraining
    config = RetrainConfig(
        model_name="signal_classifier",
        schedule="weekly",
        min_new_samples=50,
        performance_threshold=0.70,
        max_days_since_retrain=7,
    )

    # Create retrainer
    retrainer = ScheduledRetrainer(
        config=config,
        model_factory=create_model,
        data_loader=load_data,
        model_saver=save_model,
        notifier=send_notification,
    )

    # Check health
    print("=" * 60)
    print("MODEL HEALTH CHECK")
    print("=" * 60)

    health = retrainer.check_health()
    print(f"\nModel: {health.model_name}")
    print(f"Last Retrain: {health.last_retrain or 'Never'}")
    print(f"Days Since: {health.days_since_retrain}")
    print(f"Current Accuracy: {health.current_accuracy:.2%}")
    print(f"Samples Since Retrain: {health.samples_since_retrain}")
    print(f"Needs Retrain: {health.needs_retrain}")
    print(f"Reason: {health.reason}")

    # Force retrain for demo
    print("\n" + "=" * 60)
    print("EXECUTING RETRAINING")
    print("=" * 60)

    result = retrainer.retrain(force=True)

    print(f"\nResult:")
    print(f"  Success: {result.success}")
    print(f"  Old Accuracy: {result.old_accuracy:.2%}")
    print(f"  New Accuracy: {result.new_accuracy:.2%}")
    print(f"  Improvement: {result.improvement:+.2%}")
    print(f"  Samples Used: {result.samples_used}")
    print(f"  Training Time: {result.training_time:.2f}s")

    if result.metadata.get("cv_scores"):
        print(f"  CV Scores: {[f'{s:.4f}' for s in result.metadata['cv_scores']]}")

    # Cron runner example
    print("\n" + "=" * 60)
    print("CRON RUNNER EXAMPLE")
    print("=" * 60)

    runner = CronRetrainRunner([retrainer])
    results = runner.run_all(force=True)
    report = runner.generate_report(results)
    print(report)
