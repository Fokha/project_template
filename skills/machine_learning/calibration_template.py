# ═══════════════════════════════════════════════════════════════
# CONFIDENCE CALIBRATION TEMPLATE
# Calibrate model confidence scores for reliable predictions
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Train your model
# 3. Calibrate confidence scores
#
# Why Calibrate?
# Raw model probabilities are often overconfident.
# Calibration ensures 80% confidence = 80% correct rate.
#
# ═══════════════════════════════════════════════════════════════

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════


@dataclass
class CalibrationResult:
    """Results of calibration analysis."""
    fraction_of_positives: np.ndarray  # Actual positive rate per bin
    mean_predicted_value: np.ndarray    # Mean predicted probability per bin
    brier_score: float                  # Brier score (lower is better)
    expected_calibration_error: float   # ECE metric
    max_calibration_error: float        # MCE metric
    is_calibrated: bool                 # Whether model is well-calibrated


# ═══════════════════════════════════════════════════════════════
# CALIBRATOR
# ═══════════════════════════════════════════════════════════════


class ConfidenceCalibrator:
    """
    Calibrate ML model confidence scores.

    Methods:
    - Platt Scaling (sigmoid): Works well for SVMs
    - Isotonic Regression: Non-parametric, works for any model
    - Temperature Scaling: Simple scaling factor
    """

    def __init__(self, method: str = "isotonic"):
        """
        Initialize calibrator.

        Args:
            method: 'isotonic', 'sigmoid', or 'temperature'
        """
        self.method = method
        self.calibrated_model = None
        self.temperature = 1.0

    def fit(
        self,
        model,
        X_cal: np.ndarray,
        y_cal: np.ndarray,
        cv: int = 5
    ):
        """
        Fit calibration on held-out data.

        Args:
            model: Trained model with predict_proba
            X_cal: Calibration features
            y_cal: Calibration labels
            cv: Cross-validation folds
        """
        logger.info(f"Fitting calibration with method: {self.method}")

        if self.method == "temperature":
            self._fit_temperature(model, X_cal, y_cal)
        else:
            self.calibrated_model = CalibratedClassifierCV(
                model,
                method=self.method,
                cv=cv
            )
            self.calibrated_model.fit(X_cal, y_cal)

        logger.info("Calibration complete")

    def _fit_temperature(
        self,
        model,
        X_cal: np.ndarray,
        y_cal: np.ndarray
    ):
        """Fit temperature scaling."""
        from scipy.optimize import minimize

        # Get logits (log of probabilities)
        probs = model.predict_proba(X_cal)
        logits = np.log(probs + 1e-10)

        def nll_loss(T):
            scaled = logits / T
            exp_scaled = np.exp(scaled)
            softmax = exp_scaled / exp_scaled.sum(axis=1, keepdims=True)
            return -np.mean(np.log(softmax[range(len(y_cal)), y_cal] + 1e-10))

        result = minimize(nll_loss, 1.0, method='Nelder-Mead')
        self.temperature = result.x[0]
        self._base_model = model

        logger.info(f"Optimal temperature: {self.temperature:.4f}")

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get calibrated probabilities."""
        if self.method == "temperature":
            probs = self._base_model.predict_proba(X)
            logits = np.log(probs + 1e-10)
            scaled = logits / self.temperature
            exp_scaled = np.exp(scaled)
            return exp_scaled / exp_scaled.sum(axis=1, keepdims=True)
        else:
            return self.calibrated_model.predict_proba(X)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Get predictions using calibrated model."""
        proba = self.predict_proba(X)
        return np.argmax(proba, axis=1)

    def get_confidence(self, X: np.ndarray) -> np.ndarray:
        """Get confidence scores (max probability)."""
        proba = self.predict_proba(X)
        return np.max(proba, axis=1)


# ═══════════════════════════════════════════════════════════════
# CALIBRATION ANALYSIS
# ═══════════════════════════════════════════════════════════════


class CalibrationAnalyzer:
    """Analyze model calibration quality."""

    def __init__(self, n_bins: int = 10):
        self.n_bins = n_bins

    def analyze(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray
    ) -> CalibrationResult:
        """
        Analyze calibration of predicted probabilities.

        Args:
            y_true: True labels (0 or 1)
            y_prob: Predicted probabilities for positive class

        Returns:
            CalibrationResult with metrics
        """
        # Calibration curve
        fraction_of_positives, mean_predicted_value = calibration_curve(
            y_true, y_prob, n_bins=self.n_bins, strategy='uniform'
        )

        # Brier score
        brier_score = np.mean((y_prob - y_true) ** 2)

        # Expected Calibration Error (ECE)
        ece = self._calculate_ece(y_true, y_prob)

        # Maximum Calibration Error (MCE)
        mce = self._calculate_mce(y_true, y_prob)

        # Check if well-calibrated (ECE < 0.05 is generally good)
        is_calibrated = ece < 0.05

        return CalibrationResult(
            fraction_of_positives=fraction_of_positives,
            mean_predicted_value=mean_predicted_value,
            brier_score=brier_score,
            expected_calibration_error=ece,
            max_calibration_error=mce,
            is_calibrated=is_calibrated,
        )

    def _calculate_ece(self, y_true: np.ndarray, y_prob: np.ndarray) -> float:
        """Calculate Expected Calibration Error."""
        bin_boundaries = np.linspace(0, 1, self.n_bins + 1)
        ece = 0.0

        for i in range(self.n_bins):
            mask = (y_prob >= bin_boundaries[i]) & (y_prob < bin_boundaries[i + 1])
            if mask.sum() > 0:
                bin_accuracy = y_true[mask].mean()
                bin_confidence = y_prob[mask].mean()
                bin_weight = mask.sum() / len(y_true)
                ece += bin_weight * abs(bin_accuracy - bin_confidence)

        return ece

    def _calculate_mce(self, y_true: np.ndarray, y_prob: np.ndarray) -> float:
        """Calculate Maximum Calibration Error."""
        bin_boundaries = np.linspace(0, 1, self.n_bins + 1)
        max_error = 0.0

        for i in range(self.n_bins):
            mask = (y_prob >= bin_boundaries[i]) & (y_prob < bin_boundaries[i + 1])
            if mask.sum() > 0:
                bin_accuracy = y_true[mask].mean()
                bin_confidence = y_prob[mask].mean()
                max_error = max(max_error, abs(bin_accuracy - bin_confidence))

        return max_error

    def compare_before_after(
        self,
        y_true: np.ndarray,
        y_prob_uncal: np.ndarray,
        y_prob_cal: np.ndarray
    ) -> Dict[str, Any]:
        """Compare calibration before and after."""
        before = self.analyze(y_true, y_prob_uncal)
        after = self.analyze(y_true, y_prob_cal)

        return {
            "before": {
                "brier_score": before.brier_score,
                "ece": before.expected_calibration_error,
                "mce": before.max_calibration_error,
            },
            "after": {
                "brier_score": after.brier_score,
                "ece": after.expected_calibration_error,
                "mce": after.max_calibration_error,
            },
            "improvement": {
                "brier_score": before.brier_score - after.brier_score,
                "ece": before.expected_calibration_error - after.expected_calibration_error,
                "mce": before.max_calibration_error - after.max_calibration_error,
            },
        }


# ═══════════════════════════════════════════════════════════════
# CONFIDENCE THRESHOLDS
# ═══════════════════════════════════════════════════════════════


class ConfidenceThresholder:
    """
    Apply confidence thresholds for trading decisions.

    Only act on predictions above certain confidence levels.
    """

    def __init__(
        self,
        high_confidence: float = 0.8,
        medium_confidence: float = 0.65,
        low_confidence: float = 0.5
    ):
        self.high = high_confidence
        self.medium = medium_confidence
        self.low = low_confidence

    def get_signal_quality(self, confidence: float) -> str:
        """Get signal quality level."""
        if confidence >= self.high:
            return "HIGH"
        elif confidence >= self.medium:
            return "MEDIUM"
        elif confidence >= self.low:
            return "LOW"
        else:
            return "REJECT"

    def filter_predictions(
        self,
        predictions: np.ndarray,
        confidences: np.ndarray,
        min_confidence: float = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Filter predictions by confidence threshold.

        Returns:
            Tuple of (filtered_predictions, filtered_confidences, mask)
        """
        threshold = min_confidence or self.medium
        mask = confidences >= threshold

        return predictions[mask], confidences[mask], mask

    def get_position_size_multiplier(self, confidence: float) -> float:
        """
        Get position size multiplier based on confidence.

        Higher confidence = larger position.
        """
        quality = self.get_signal_quality(confidence)

        multipliers = {
            "HIGH": 1.0,
            "MEDIUM": 0.7,
            "LOW": 0.5,
            "REJECT": 0.0,
        }

        return multipliers[quality]


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification

    # Create sample data
    X, y = make_classification(
        n_samples=2000,
        n_features=20,
        n_informative=10,
        random_state=42
    )

    # Split data
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.4, random_state=42)
    X_cal, X_test, y_cal, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Get uncalibrated probabilities
    y_prob_uncal = model.predict_proba(X_test)[:, 1]

    # Calibrate
    calibrator = ConfidenceCalibrator(method="isotonic")
    calibrator.fit(model, X_cal, y_cal)

    # Get calibrated probabilities
    y_prob_cal = calibrator.predict_proba(X_test)[:, 1]

    # Analyze
    analyzer = CalibrationAnalyzer(n_bins=10)
    comparison = analyzer.compare_before_after(y_test, y_prob_uncal, y_prob_cal)

    # Print results
    print(f"\n{'='*60}")
    print("CALIBRATION RESULTS")
    print(f"{'='*60}")
    print(f"\nBefore Calibration:")
    print(f"  Brier Score: {comparison['before']['brier_score']:.4f}")
    print(f"  ECE: {comparison['before']['ece']:.4f}")
    print(f"  MCE: {comparison['before']['mce']:.4f}")

    print(f"\nAfter Calibration:")
    print(f"  Brier Score: {comparison['after']['brier_score']:.4f}")
    print(f"  ECE: {comparison['after']['ece']:.4f}")
    print(f"  MCE: {comparison['after']['mce']:.4f}")

    print(f"\nImprovement:")
    print(f"  Brier Score: {comparison['improvement']['brier_score']:.4f}")
    print(f"  ECE: {comparison['improvement']['ece']:.4f}")

    # Confidence thresholding
    print(f"\n{'='*60}")
    print("CONFIDENCE THRESHOLDING")
    print(f"{'='*60}")

    thresholder = ConfidenceThresholder()
    confidences = calibrator.get_confidence(X_test)

    for conf in [0.9, 0.75, 0.6, 0.45]:
        quality = thresholder.get_signal_quality(conf)
        multiplier = thresholder.get_position_size_multiplier(conf)
        print(f"  Confidence {conf:.2f}: {quality} (position size: {multiplier:.1f}x)")
