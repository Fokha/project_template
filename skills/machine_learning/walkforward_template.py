# ═══════════════════════════════════════════════════════════════
# WALK-FORWARD VALIDATION TEMPLATE
# Time-series cross-validation for trading ML models
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Configure train/test windows
# 3. Run validation
#
# CRITICAL: Never train on future data in trading!
#
# ═══════════════════════════════════════════════════════════════

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from pathlib import Path

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════


@dataclass
class WalkForwardConfig:
    """Walk-forward validation configuration."""
    train_window_days: int = 90      # Training window size
    test_window_days: int = 30       # Testing window size
    step_days: int = 30              # Step size between windows
    min_train_samples: int = 500     # Minimum samples for training
    date_column: str = "date"        # Date column name
    target_column: str = "target"    # Target column name


@dataclass
class WindowResult:
    """Results for a single walk-forward window."""
    window_id: int
    train_start: datetime
    train_end: datetime
    test_start: datetime
    test_end: datetime
    train_samples: int
    test_samples: int
    accuracy: float
    precision: float
    recall: float
    f1: float
    predictions: np.ndarray
    actuals: np.ndarray


@dataclass
class WalkForwardResult:
    """Complete walk-forward validation results."""
    config: WalkForwardConfig
    windows: List[WindowResult]
    avg_accuracy: float
    std_accuracy: float
    avg_precision: float
    avg_recall: float
    avg_f1: float
    total_predictions: int
    degradation_detected: bool
    validation_date: datetime


# ═══════════════════════════════════════════════════════════════
# WALK-FORWARD VALIDATOR
# ═══════════════════════════════════════════════════════════════


class WalkForwardValidator:
    """
    Walk-Forward Validation for Time-Series ML.

    Key Principle: Never train on future data!

    Timeline:
    ─────────────────────────────────────────────────────────────
    |  TRAIN 1  |  TEST 1  |
              |  TRAIN 2  |  TEST 2  |
                        |  TRAIN 3  |  TEST 3  |
    ─────────────────────────────────────────────────────────────
    Past ──────────────────────────────────────────────► Future
    """

    def __init__(self, config: WalkForwardConfig):
        self.config = config
        self.results: List[WindowResult] = []

    def validate(
        self,
        df: pd.DataFrame,
        model_factory: Callable,
        feature_columns: List[str],
        scaler: Optional[StandardScaler] = None
    ) -> WalkForwardResult:
        """
        Run walk-forward validation.

        Args:
            df: DataFrame with date and target columns
            model_factory: Function that returns a new model instance
            feature_columns: List of feature column names
            scaler: Optional scaler (will be fit per window)

        Returns:
            WalkForwardResult with all window results
        """
        logger.info("Starting walk-forward validation")

        # Ensure date column is datetime
        df = df.copy()
        df[self.config.date_column] = pd.to_datetime(df[self.config.date_column])
        df = df.sort_values(self.config.date_column)

        # Get date range
        min_date = df[self.config.date_column].min()
        max_date = df[self.config.date_column].max()

        logger.info(f"Data range: {min_date} to {max_date}")

        # Generate windows
        windows = self._generate_windows(min_date, max_date)
        logger.info(f"Generated {len(windows)} validation windows")

        self.results = []

        for i, (train_start, train_end, test_start, test_end) in enumerate(windows):
            logger.info(f"\n{'='*50}")
            logger.info(f"Window {i + 1}/{len(windows)}")
            logger.info(f"Train: {train_start.date()} → {train_end.date()}")
            logger.info(f"Test:  {test_start.date()} → {test_end.date()}")

            # Split data
            train_mask = (
                (df[self.config.date_column] >= train_start) &
                (df[self.config.date_column] < train_end)
            )
            test_mask = (
                (df[self.config.date_column] >= test_start) &
                (df[self.config.date_column] < test_end)
            )

            train_df = df[train_mask]
            test_df = df[test_mask]

            if len(train_df) < self.config.min_train_samples:
                logger.warning(f"Skipping: only {len(train_df)} train samples")
                continue

            if len(test_df) == 0:
                logger.warning("Skipping: no test samples")
                continue

            # Extract features and targets
            X_train = train_df[feature_columns].values
            y_train = train_df[self.config.target_column].values
            X_test = test_df[feature_columns].values
            y_test = test_df[self.config.target_column].values

            # Scale features (fit on train only!)
            window_scaler = StandardScaler() if scaler is None else StandardScaler()
            X_train = window_scaler.fit_transform(X_train)
            X_test = window_scaler.transform(X_test)

            # Train model
            model = model_factory()
            model.fit(X_train, y_train)

            # Predict
            y_pred = model.predict(X_test)

            # Calculate metrics
            result = WindowResult(
                window_id=i + 1,
                train_start=train_start,
                train_end=train_end,
                test_start=test_start,
                test_end=test_end,
                train_samples=len(train_df),
                test_samples=len(test_df),
                accuracy=accuracy_score(y_test, y_pred),
                precision=precision_score(y_test, y_pred, average='weighted', zero_division=0),
                recall=recall_score(y_test, y_pred, average='weighted', zero_division=0),
                f1=f1_score(y_test, y_pred, average='weighted', zero_division=0),
                predictions=y_pred,
                actuals=y_test,
            )

            self.results.append(result)
            logger.info(f"Accuracy: {result.accuracy:.4f}")

        # Calculate overall metrics
        return self._compile_results()

    def _generate_windows(
        self,
        min_date: datetime,
        max_date: datetime
    ) -> List[Tuple[datetime, datetime, datetime, datetime]]:
        """Generate walk-forward windows."""
        windows = []

        train_days = timedelta(days=self.config.train_window_days)
        test_days = timedelta(days=self.config.test_window_days)
        step_days = timedelta(days=self.config.step_days)

        current_start = min_date

        while True:
            train_start = current_start
            train_end = train_start + train_days
            test_start = train_end
            test_end = test_start + test_days

            # Stop if we've gone past the data
            if test_end > max_date:
                break

            windows.append((train_start, train_end, test_start, test_end))
            current_start += step_days

        return windows

    def _compile_results(self) -> WalkForwardResult:
        """Compile results across all windows."""
        if not self.results:
            raise ValueError("No validation results available")

        accuracies = [r.accuracy for r in self.results]
        precisions = [r.precision for r in self.results]
        recalls = [r.recall for r in self.results]
        f1s = [r.f1 for r in self.results]

        # Detect degradation (last 3 windows vs first 3)
        degradation_detected = False
        if len(accuracies) >= 6:
            first_3_avg = np.mean(accuracies[:3])
            last_3_avg = np.mean(accuracies[-3:])
            degradation_detected = last_3_avg < first_3_avg * 0.9  # 10% drop

        total_predictions = sum(r.test_samples for r in self.results)

        return WalkForwardResult(
            config=self.config,
            windows=self.results,
            avg_accuracy=np.mean(accuracies),
            std_accuracy=np.std(accuracies),
            avg_precision=np.mean(precisions),
            avg_recall=np.mean(recalls),
            avg_f1=np.mean(f1s),
            total_predictions=total_predictions,
            degradation_detected=degradation_detected,
            validation_date=datetime.now(),
        )

    def get_stability_score(self) -> float:
        """
        Calculate model stability score.

        Returns:
            Score 0-1 (higher = more stable)
        """
        if not self.results:
            return 0.0

        accuracies = [r.accuracy for r in self.results]

        # Stability = 1 - normalized std
        std = np.std(accuracies)
        mean = np.mean(accuracies)

        if mean == 0:
            return 0.0

        cv = std / mean  # Coefficient of variation
        stability = max(0, 1 - cv)

        return stability

    def should_retrain(self, threshold: float = 0.1) -> bool:
        """
        Determine if model needs retraining based on performance drift.

        Args:
            threshold: Maximum acceptable performance drop

        Returns:
            True if retraining recommended
        """
        if len(self.results) < 2:
            return False

        # Compare recent performance to historical
        recent_acc = self.results[-1].accuracy
        historical_avg = np.mean([r.accuracy for r in self.results[:-1]])

        drop = historical_avg - recent_acc
        return drop > threshold


# ═══════════════════════════════════════════════════════════════
# EXPANDING WINDOW VALIDATOR
# ═══════════════════════════════════════════════════════════════


class ExpandingWindowValidator:
    """
    Expanding Window Validation (Growing Training Set).

    Unlike fixed walk-forward, the training window grows over time.

    Timeline:
    ─────────────────────────────────────────────────────────────
    |  TRAIN 1  |  TEST 1  |
    |    TRAIN 2     |  TEST 2  |
    |       TRAIN 3       |  TEST 3  |
    ─────────────────────────────────────────────────────────────
    """

    def __init__(
        self,
        min_train_days: int = 60,
        test_days: int = 30,
        step_days: int = 30
    ):
        self.min_train_days = min_train_days
        self.test_days = test_days
        self.step_days = step_days

    def validate(
        self,
        df: pd.DataFrame,
        model_factory: Callable,
        feature_columns: List[str],
        date_column: str = "date",
        target_column: str = "target"
    ) -> Dict[str, Any]:
        """Run expanding window validation."""
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df = df.sort_values(date_column)

        min_date = df[date_column].min()
        max_date = df[date_column].max()

        results = []
        current_test_start = min_date + timedelta(days=self.min_train_days)

        while True:
            train_end = current_test_start
            test_end = train_end + timedelta(days=self.test_days)

            if test_end > max_date:
                break

            # Train on ALL data up to train_end
            train_mask = df[date_column] < train_end
            test_mask = (df[date_column] >= train_end) & (df[date_column] < test_end)

            train_df = df[train_mask]
            test_df = df[test_mask]

            if len(train_df) < 100 or len(test_df) == 0:
                current_test_start += timedelta(days=self.step_days)
                continue

            # Train and evaluate
            X_train = train_df[feature_columns].values
            y_train = train_df[target_column].values
            X_test = test_df[feature_columns].values
            y_test = test_df[target_column].values

            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)

            model = model_factory()
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            results.append({
                'train_samples': len(train_df),
                'test_samples': len(test_df),
                'accuracy': accuracy_score(y_test, y_pred),
                'test_start': train_end,
                'test_end': test_end,
            })

            current_test_start += timedelta(days=self.step_days)

        return {
            'windows': results,
            'avg_accuracy': np.mean([r['accuracy'] for r in results]),
            'accuracy_trend': self._calculate_trend([r['accuracy'] for r in results]),
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction."""
        if len(values) < 3:
            return "insufficient_data"

        first_half = np.mean(values[:len(values)//2])
        second_half = np.mean(values[len(values)//2:])

        if second_half > first_half * 1.05:
            return "improving"
        elif second_half < first_half * 0.95:
            return "degrading"
        else:
            return "stable"


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    from sklearn.ensemble import RandomForestClassifier

    # Create sample time-series data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=1000, freq='D')

    df = pd.DataFrame({
        'date': dates,
        'feature_1': np.random.randn(1000).cumsum(),
        'feature_2': np.random.randn(1000).cumsum(),
        'feature_3': np.random.randn(1000),
        'target': np.random.randint(0, 2, 1000),
    })

    # Configure walk-forward
    config = WalkForwardConfig(
        train_window_days=90,
        test_window_days=30,
        step_days=30,
        min_train_samples=50,
    )

    # Model factory
    def create_model():
        return RandomForestClassifier(n_estimators=50, random_state=42)

    # Run validation
    validator = WalkForwardValidator(config)
    result = validator.validate(
        df=df,
        model_factory=create_model,
        feature_columns=['feature_1', 'feature_2', 'feature_3'],
    )

    # Print results
    print(f"\n{'='*60}")
    print("WALK-FORWARD VALIDATION RESULTS")
    print(f"{'='*60}")
    print(f"Windows:           {len(result.windows)}")
    print(f"Total Predictions: {result.total_predictions}")
    print(f"\nAverage Accuracy:  {result.avg_accuracy:.4f} ± {result.std_accuracy:.4f}")
    print(f"Average Precision: {result.avg_precision:.4f}")
    print(f"Average Recall:    {result.avg_recall:.4f}")
    print(f"Average F1:        {result.avg_f1:.4f}")
    print(f"\nStability Score:   {validator.get_stability_score():.4f}")
    print(f"Degradation:       {'Yes' if result.degradation_detected else 'No'}")
    print(f"Needs Retrain:     {'Yes' if validator.should_retrain() else 'No'}")

    print(f"\n{'='*60}")
    print("WINDOW DETAILS")
    print(f"{'='*60}")
    for w in result.windows:
        print(f"Window {w.window_id}: {w.test_start.date()} → {w.test_end.date()} | "
              f"Acc: {w.accuracy:.4f} | Train: {w.train_samples} | Test: {w.test_samples}")
