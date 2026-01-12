# ═══════════════════════════════════════════════════════════════
# ENSEMBLE MODEL TEMPLATE
# Combine XGBoost + LightGBM for robust predictions
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Customize weights and models
# 3. Run training
#
# ═══════════════════════════════════════════════════════════════

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import joblib
from pathlib import Path

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Optional imports
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
class EnsembleConfig:
    """Ensemble configuration."""
    model_name: str
    xgb_weight: float = 0.5
    lgb_weight: float = 0.5
    voting_method: str = "soft"  # soft, hard, weighted
    random_state: int = 42
    model_dir: str = "models"


@dataclass
class EnsembleResult:
    """Ensemble training results."""
    model_name: str
    ensemble_accuracy: float
    xgb_accuracy: float
    lgb_accuracy: float
    weights: Dict[str, float]
    model_path: str


# ═══════════════════════════════════════════════════════════════
# ENSEMBLE TRAINER
# ═══════════════════════════════════════════════════════════════


class EnsembleTrainer:
    """
    Train ensemble of XGBoost + LightGBM.

    Ensemble Strategy:
    - Soft voting: Average predicted probabilities
    - Hard voting: Majority vote on predictions
    - Weighted: Weighted average based on validation performance
    """

    def __init__(self, config: EnsembleConfig):
        self.config = config
        self.xgb_model = None
        self.lgb_model = None
        self.scaler = StandardScaler()
        self.feature_columns = []

        # Validate weights
        if abs(config.xgb_weight + config.lgb_weight - 1.0) > 0.01:
            raise ValueError("Weights must sum to 1.0")

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        feature_columns: List[str]
    ) -> EnsembleResult:
        """
        Train ensemble models.

        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            feature_columns: List of feature names

        Returns:
            EnsembleResult with metrics
        """
        self.feature_columns = feature_columns
        logger.info(f"Training ensemble: {self.config.model_name}")

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)

        # Train XGBoost
        xgb_accuracy = 0.0
        if HAS_XGB:
            logger.info("Training XGBoost...")
            self.xgb_model = self._create_xgb_model()
            self.xgb_model.fit(X_train_scaled, y_train)
            xgb_pred = self.xgb_model.predict(X_val_scaled)
            xgb_accuracy = accuracy_score(y_val, xgb_pred)
            logger.info(f"  XGBoost Accuracy: {xgb_accuracy:.4f}")

        # Train LightGBM
        lgb_accuracy = 0.0
        if HAS_LGB:
            logger.info("Training LightGBM...")
            self.lgb_model = self._create_lgb_model()
            self.lgb_model.fit(X_train_scaled, y_train)
            lgb_pred = self.lgb_model.predict(X_val_scaled)
            lgb_accuracy = accuracy_score(y_val, lgb_pred)
            logger.info(f"  LightGBM Accuracy: {lgb_accuracy:.4f}")

        # Ensemble prediction
        ensemble_pred = self.predict(X_val)
        ensemble_accuracy = accuracy_score(y_val, ensemble_pred)
        logger.info(f"  Ensemble Accuracy: {ensemble_accuracy:.4f}")

        # Auto-adjust weights based on validation performance
        if self.config.voting_method == "weighted":
            self._optimize_weights(X_val_scaled, y_val)

        # Save model
        model_path = self._save_model()

        return EnsembleResult(
            model_name=self.config.model_name,
            ensemble_accuracy=ensemble_accuracy,
            xgb_accuracy=xgb_accuracy,
            lgb_accuracy=lgb_accuracy,
            weights={
                'xgb': self.config.xgb_weight,
                'lgb': self.config.lgb_weight,
            },
            model_path=model_path,
        )

    def _create_xgb_model(self):
        """Create XGBoost model."""
        return xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=self.config.random_state,
            use_label_encoder=False,
            eval_metric='logloss'
        )

    def _create_lgb_model(self):
        """Create LightGBM model."""
        return lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=self.config.random_state,
            verbose=-1
        )

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make ensemble predictions.

        Args:
            X: Feature array (unscaled)

        Returns:
            Predicted labels
        """
        X_scaled = self.scaler.transform(X)

        if self.config.voting_method == "soft":
            return self._soft_voting(X_scaled)
        elif self.config.voting_method == "hard":
            return self._hard_voting(X_scaled)
        else:
            return self._weighted_voting(X_scaled)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get ensemble prediction probabilities."""
        X_scaled = self.scaler.transform(X)

        proba_sum = np.zeros((len(X), 2))
        total_weight = 0

        if self.xgb_model is not None:
            proba_sum += self.xgb_model.predict_proba(X_scaled) * self.config.xgb_weight
            total_weight += self.config.xgb_weight

        if self.lgb_model is not None:
            proba_sum += self.lgb_model.predict_proba(X_scaled) * self.config.lgb_weight
            total_weight += self.config.lgb_weight

        return proba_sum / total_weight if total_weight > 0 else proba_sum

    def _soft_voting(self, X_scaled: np.ndarray) -> np.ndarray:
        """Average probabilities and take argmax."""
        proba = self.predict_proba(self.scaler.inverse_transform(X_scaled))
        return (proba[:, 1] >= 0.5).astype(int)

    def _hard_voting(self, X_scaled: np.ndarray) -> np.ndarray:
        """Majority vote on predictions."""
        predictions = []

        if self.xgb_model is not None:
            predictions.append(self.xgb_model.predict(X_scaled))
        if self.lgb_model is not None:
            predictions.append(self.lgb_model.predict(X_scaled))

        if not predictions:
            return np.zeros(len(X_scaled), dtype=int)

        # Stack and take mode
        stacked = np.stack(predictions, axis=1)
        return np.apply_along_axis(
            lambda x: np.bincount(x.astype(int)).argmax(),
            axis=1,
            arr=stacked
        )

    def _weighted_voting(self, X_scaled: np.ndarray) -> np.ndarray:
        """Weighted average of probabilities."""
        return self._soft_voting(X_scaled)

    def _optimize_weights(
        self,
        X_val: np.ndarray,
        y_val: np.ndarray
    ) -> Tuple[float, float]:
        """Find optimal weights based on validation performance."""
        best_accuracy = 0
        best_weights = (0.5, 0.5)

        for xgb_w in np.arange(0.1, 1.0, 0.1):
            lgb_w = 1.0 - xgb_w

            # Temporarily set weights
            old_xgb = self.config.xgb_weight
            old_lgb = self.config.lgb_weight
            self.config.xgb_weight = xgb_w
            self.config.lgb_weight = lgb_w

            # Predict
            pred = self._soft_voting(X_val)
            accuracy = accuracy_score(y_val, pred)

            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_weights = (xgb_w, lgb_w)

            # Restore
            self.config.xgb_weight = old_xgb
            self.config.lgb_weight = old_lgb

        # Set optimal weights
        self.config.xgb_weight, self.config.lgb_weight = best_weights
        logger.info(f"Optimized weights: XGB={best_weights[0]:.2f}, LGB={best_weights[1]:.2f}")

        return best_weights

    def _save_model(self) -> str:
        """Save ensemble to disk."""
        model_dir = Path(self.config.model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)

        model_path = model_dir / f"{self.config.model_name}_ensemble.pkl"

        joblib.dump({
            'xgb_model': self.xgb_model,
            'lgb_model': self.lgb_model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'config': self.config,
        }, model_path)

        logger.info(f"Ensemble saved to {model_path}")
        return str(model_path)


# ═══════════════════════════════════════════════════════════════
# LOADER
# ═══════════════════════════════════════════════════════════════


def load_ensemble(model_path: str) -> EnsembleTrainer:
    """Load a saved ensemble model."""
    data = joblib.load(model_path)

    trainer = EnsembleTrainer(data['config'])
    trainer.xgb_model = data['xgb_model']
    trainer.lgb_model = data['lgb_model']
    trainer.scaler = data['scaler']
    trainer.feature_columns = data['feature_columns']

    return trainer


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    # Create sample data
    np.random.seed(42)
    n_samples = 1000
    n_features = 10

    X = np.random.randn(n_samples, n_features)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)

    # Split
    split_idx = int(n_samples * 0.8)
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]

    feature_columns = [f"feature_{i}" for i in range(n_features)]

    # Train ensemble
    config = EnsembleConfig(
        model_name="signal_ensemble",
        xgb_weight=0.5,
        lgb_weight=0.5,
        voting_method="weighted",
    )

    trainer = EnsembleTrainer(config)
    result = trainer.train(X_train, y_train, X_val, y_val, feature_columns)

    # Print results
    print(f"\n{'='*50}")
    print(f"Ensemble: {result.model_name}")
    print(f"XGBoost Accuracy: {result.xgb_accuracy:.4f}")
    print(f"LightGBM Accuracy: {result.lgb_accuracy:.4f}")
    print(f"Ensemble Accuracy: {result.ensemble_accuracy:.4f}")
    print(f"Weights: {result.weights}")
    print(f"Model Path: {result.model_path}")
