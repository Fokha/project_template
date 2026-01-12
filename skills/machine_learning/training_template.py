# ═══════════════════════════════════════════════════════════════
# ML TRAINING PIPELINE TEMPLATE
# Complete training workflow with validation and persistence
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Customize feature engineering
# 3. Run training: python training_template.py
#
# ═══════════════════════════════════════════════════════════════

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import joblib
from pathlib import Path

from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler

# Optional: Install these for full functionality
try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

try:
    import lightgbm as lgb
    HAS_LGB = True
except ImportError:
    HAS_LGB = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════


@dataclass
class TrainingConfig:
    """Training configuration."""
    model_name: str
    target_column: str
    feature_columns: List[str]
    test_size: float = 0.2
    n_splits: int = 5
    random_state: int = 42
    model_dir: str = "models"


@dataclass
class TrainingResult:
    """Training results."""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1: float
    feature_importance: Dict[str, float]
    training_time: float
    model_path: str
    metadata: Dict[str, Any]


# ═══════════════════════════════════════════════════════════════
# FEATURE ENGINEERING
# ═══════════════════════════════════════════════════════════════


class FeatureEngineer:
    """
    Feature engineering for ML models.

    Customize this class for your specific domain.
    """

    def __init__(self, config: TrainingConfig):
        self.config = config
        self.scaler = StandardScaler()

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features from raw data.

        Override this method with your domain-specific features.
        """
        df = df.copy()

        # Example: Technical indicators for trading
        if 'close' in df.columns:
            # Moving averages
            df['sma_10'] = df['close'].rolling(10).mean()
            df['sma_20'] = df['close'].rolling(20).mean()
            df['ema_10'] = df['close'].ewm(span=10).mean()

            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))

            # MACD
            ema12 = df['close'].ewm(span=12).mean()
            ema26 = df['close'].ewm(span=26).mean()
            df['macd'] = ema12 - ema26
            df['macd_signal'] = df['macd'].ewm(span=9).mean()

            # Volatility
            df['volatility'] = df['close'].rolling(20).std()

            # Returns
            df['returns'] = df['close'].pct_change()
            df['returns_5'] = df['close'].pct_change(5)

        # Drop NaN values
        df = df.dropna()

        return df

    def prepare_data(
        self,
        df: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare data for training."""

        # Create features
        df = self.create_features(df)

        # Get feature columns
        feature_cols = [c for c in df.columns
                       if c not in [self.config.target_column, 'date', 'datetime']]

        X = df[feature_cols].values
        y = df[self.config.target_column].values

        # Scale features
        X = self.scaler.fit_transform(X)

        return X, y, feature_cols


# ═══════════════════════════════════════════════════════════════
# MODEL TRAINER
# ═══════════════════════════════════════════════════════════════


class ModelTrainer:
    """
    Train and evaluate ML models.
    """

    def __init__(self, config: TrainingConfig):
        self.config = config
        self.feature_engineer = FeatureEngineer(config)
        self.model = None
        self.feature_columns = []

    def train(self, df: pd.DataFrame) -> TrainingResult:
        """
        Train model on data.

        Args:
            df: DataFrame with features and target

        Returns:
            TrainingResult with metrics and model path
        """
        start_time = datetime.now()
        logger.info(f"Starting training for {self.config.model_name}")

        # Prepare data
        X, y, self.feature_columns = self.feature_engineer.prepare_data(df)

        # Time series split
        tscv = TimeSeriesSplit(n_splits=self.config.n_splits)

        # Track metrics across folds
        fold_metrics = []

        for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]

            # Train model
            model = self._create_model()
            model.fit(X_train, y_train)

            # Evaluate
            y_pred = model.predict(X_val)

            metrics = {
                'accuracy': accuracy_score(y_val, y_pred),
                'precision': precision_score(y_val, y_pred, average='weighted', zero_division=0),
                'recall': recall_score(y_val, y_pred, average='weighted', zero_division=0),
                'f1': f1_score(y_val, y_pred, average='weighted', zero_division=0),
            }
            fold_metrics.append(metrics)

            logger.info(f"Fold {fold + 1}: Accuracy = {metrics['accuracy']:.4f}")

        # Train final model on all data
        self.model = self._create_model()
        self.model.fit(X, y)

        # Calculate average metrics
        avg_metrics = {
            k: np.mean([m[k] for m in fold_metrics])
            for k in fold_metrics[0].keys()
        }

        # Get feature importance
        importance = self._get_feature_importance()

        # Save model
        model_path = self._save_model()

        training_time = (datetime.now() - start_time).total_seconds()

        result = TrainingResult(
            model_name=self.config.model_name,
            accuracy=avg_metrics['accuracy'],
            precision=avg_metrics['precision'],
            recall=avg_metrics['recall'],
            f1=avg_metrics['f1'],
            feature_importance=importance,
            training_time=training_time,
            model_path=model_path,
            metadata={
                'n_samples': len(df),
                'n_features': len(self.feature_columns),
                'n_folds': self.config.n_splits,
                'trained_at': datetime.now().isoformat(),
            }
        )

        logger.info(f"Training complete: Accuracy = {result.accuracy:.4f}")
        return result

    def _create_model(self):
        """Create the ML model."""
        if HAS_XGB:
            return xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=self.config.random_state,
                use_label_encoder=False,
                eval_metric='logloss'
            )
        else:
            # Fallback to sklearn
            from sklearn.ensemble import RandomForestClassifier
            return RandomForestClassifier(
                n_estimators=100,
                max_depth=6,
                random_state=self.config.random_state
            )

    def _get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from model."""
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            return dict(zip(self.feature_columns, importance))
        return {}

    def _save_model(self) -> str:
        """Save model to disk."""
        model_dir = Path(self.config.model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)

        model_path = model_dir / f"{self.config.model_name}.pkl"

        # Save model and scaler together
        joblib.dump({
            'model': self.model,
            'scaler': self.feature_engineer.scaler,
            'feature_columns': self.feature_columns,
            'config': self.config,
        }, model_path)

        logger.info(f"Model saved to {model_path}")
        return str(model_path)

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Make predictions on new data."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        X, _, _ = self.feature_engineer.prepare_data(df)
        return self.model.predict(X)

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        """Get prediction probabilities."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        X, _, _ = self.feature_engineer.prepare_data(df)
        return self.model.predict_proba(X)


# ═══════════════════════════════════════════════════════════════
# MODEL LOADER
# ═══════════════════════════════════════════════════════════════


def load_model(model_path: str) -> Tuple[Any, StandardScaler, List[str]]:
    """
    Load a saved model.

    Returns:
        Tuple of (model, scaler, feature_columns)
    """
    data = joblib.load(model_path)
    return data['model'], data['scaler'], data['feature_columns']


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    # Example: Train a signal classification model

    # Create sample data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=1000, freq='H')
    df = pd.DataFrame({
        'date': dates,
        'open': np.random.randn(1000).cumsum() + 100,
        'high': np.random.randn(1000).cumsum() + 101,
        'low': np.random.randn(1000).cumsum() + 99,
        'close': np.random.randn(1000).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 1000),
    })

    # Create target (example: price direction)
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
    df = df.dropna()

    # Configure training
    config = TrainingConfig(
        model_name="signal_classifier",
        target_column="target",
        feature_columns=[],  # Will be auto-detected
        test_size=0.2,
        n_splits=5,
    )

    # Train
    trainer = ModelTrainer(config)
    result = trainer.train(df)

    # Print results
    print(f"\n{'='*50}")
    print(f"Model: {result.model_name}")
    print(f"Accuracy: {result.accuracy:.4f}")
    print(f"Precision: {result.precision:.4f}")
    print(f"Recall: {result.recall:.4f}")
    print(f"F1 Score: {result.f1:.4f}")
    print(f"Training Time: {result.training_time:.2f}s")
    print(f"Model Path: {result.model_path}")
    print(f"\nTop Features:")
    for feat, imp in sorted(result.feature_importance.items(),
                           key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {feat}: {imp:.4f}")
