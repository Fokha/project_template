# ═══════════════════════════════════════════════════════════════
# ANOMALY DETECTION TEMPLATE
# Isolation Forest for detecting unusual market behavior
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Install: pip install scikit-learn
# 3. Detect unusual price movements, volume spikes, etc.
#
# Why Anomaly Detection?
# - Identify unusual market conditions
# - Detect potential manipulation or flash crashes
# - Filter out abnormal data before ML training
# - Alert on unusual trading patterns
#
# ═══════════════════════════════════════════════════════════════

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════


@dataclass
class AnomalyResult:
    """Result of anomaly detection."""
    timestamp: datetime
    is_anomaly: bool
    anomaly_score: float      # -1 to 1 (negative = anomaly)
    features: Dict[str, float]
    reason: str = ""


@dataclass
class AnomalyStats:
    """Statistics about detected anomalies."""
    total_points: int
    anomaly_count: int
    anomaly_rate: float
    avg_anomaly_score: float
    feature_importance: Dict[str, float]


# ═══════════════════════════════════════════════════════════════
# MARKET ANOMALY DETECTOR
# ═══════════════════════════════════════════════════════════════


class MarketAnomalyDetector:
    """
    Detect anomalies in market data using Isolation Forest.

    Features detected:
    - Unusual price movements (beyond normal volatility)
    - Volume spikes
    - Abnormal spread widening
    - Unusual time-of-day patterns
    """

    def __init__(
        self,
        contamination: float = 0.05,
        n_estimators: int = 100,
        random_state: int = 42
    ):
        """
        Initialize detector.

        Args:
            contamination: Expected proportion of anomalies (0.01-0.1)
            n_estimators: Number of trees in forest
            random_state: Random seed for reproducibility
        """
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state

        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1,
        )

        self.scaler = StandardScaler()
        self.is_fitted = False
        self.feature_names: List[str] = []

    def fit(self, df: pd.DataFrame):
        """
        Fit detector on historical data.

        Args:
            df: DataFrame with OHLCV data
        """
        logger.info("Fitting anomaly detector...")

        # Extract features
        features = self._extract_features(df)
        self.feature_names = list(features.columns)

        # Scale features
        X_scaled = self.scaler.fit_transform(features)

        # Fit Isolation Forest
        self.model.fit(X_scaled)
        self.is_fitted = True

        logger.info(f"Fitted on {len(features)} samples with {len(self.feature_names)} features")

    def detect(self, df: pd.DataFrame) -> List[AnomalyResult]:
        """
        Detect anomalies in new data.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            List of AnomalyResult for each data point
        """
        if not self.is_fitted:
            raise ValueError("Detector not fitted. Call fit() first.")

        # Extract features
        features = self._extract_features(df)
        X_scaled = self.scaler.transform(features)

        # Predict
        predictions = self.model.predict(X_scaled)  # -1 for anomaly, 1 for normal
        scores = self.model.decision_function(X_scaled)  # Anomaly score

        # Build results
        results = []
        for i in range(len(features)):
            is_anomaly = predictions[i] == -1

            # Identify which features contributed most to anomaly
            reason = ""
            if is_anomaly:
                reason = self._identify_anomaly_reason(features.iloc[i], X_scaled[i])

            results.append(AnomalyResult(
                timestamp=df.index[i] if isinstance(df.index, pd.DatetimeIndex) else datetime.now(),
                is_anomaly=is_anomaly,
                anomaly_score=float(scores[i]),
                features=features.iloc[i].to_dict(),
                reason=reason,
            ))

        return results

    def detect_realtime(self, row: Dict) -> AnomalyResult:
        """
        Detect anomaly in a single real-time data point.

        Args:
            row: Dictionary with OHLCV data

        Returns:
            AnomalyResult
        """
        df = pd.DataFrame([row])
        results = self.detect(df)
        return results[0] if results else None

    def _extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract anomaly detection features from OHLCV data."""
        features = pd.DataFrame(index=df.index)

        # Price-based features
        features['return'] = df['close'].pct_change()
        features['abs_return'] = features['return'].abs()
        features['log_return'] = np.log(df['close'] / df['close'].shift(1))

        # Volatility features
        features['rolling_std'] = df['close'].rolling(20).std()
        features['return_zscore'] = (
            (features['return'] - features['return'].rolling(20).mean()) /
            features['return'].rolling(20).std()
        )

        # Range features
        features['high_low_range'] = (df['high'] - df['low']) / df['close']
        features['body_range'] = abs(df['close'] - df['open']) / df['close']
        features['upper_shadow'] = (df['high'] - df[['open', 'close']].max(axis=1)) / df['close']
        features['lower_shadow'] = (df[['open', 'close']].min(axis=1) - df['low']) / df['close']

        # Volume features (if available)
        if 'volume' in df.columns:
            features['volume_change'] = df['volume'].pct_change()
            features['volume_zscore'] = (
                (df['volume'] - df['volume'].rolling(20).mean()) /
                df['volume'].rolling(20).std()
            )
            features['volume_price_corr'] = (
                features['abs_return'] * features['volume_change'].abs()
            )

        # Gap features
        features['gap'] = (df['open'] - df['close'].shift(1)) / df['close'].shift(1)
        features['gap_abs'] = features['gap'].abs()

        # Trend deviation
        ma20 = df['close'].rolling(20).mean()
        features['ma_deviation'] = (df['close'] - ma20) / ma20

        # Clean NaN/Inf
        features = features.replace([np.inf, -np.inf], np.nan)
        features = features.fillna(0)

        return features

    def _identify_anomaly_reason(
        self,
        raw_features: pd.Series,
        scaled_features: np.ndarray
    ) -> str:
        """Identify the most likely reason for an anomaly."""
        reasons = []

        # Check each feature for extreme values
        for i, name in enumerate(self.feature_names):
            if abs(scaled_features[i]) > 2.5:  # More than 2.5 std from mean
                if scaled_features[i] > 0:
                    reasons.append(f"High {name}")
                else:
                    reasons.append(f"Low {name}")

        return "; ".join(reasons[:3]) if reasons else "Multiple factors"

    def get_stats(self, results: List[AnomalyResult]) -> AnomalyStats:
        """Calculate statistics from detection results."""
        total = len(results)
        anomalies = sum(1 for r in results if r.is_anomaly)

        # Feature importance (based on variance contribution)
        feature_importance = {}
        if results:
            features_df = pd.DataFrame([r.features for r in results])
            for col in features_df.columns:
                feature_importance[col] = float(features_df[col].var())

            # Normalize
            total_var = sum(feature_importance.values())
            if total_var > 0:
                feature_importance = {
                    k: v / total_var
                    for k, v in feature_importance.items()
                }

        return AnomalyStats(
            total_points=total,
            anomaly_count=anomalies,
            anomaly_rate=anomalies / total if total > 0 else 0,
            avg_anomaly_score=np.mean([r.anomaly_score for r in results]),
            feature_importance=feature_importance,
        )


# ═══════════════════════════════════════════════════════════════
# STREAMING ANOMALY DETECTOR
# ═══════════════════════════════════════════════════════════════


class StreamingAnomalyDetector:
    """
    Real-time anomaly detection for streaming data.

    Uses a sliding window approach for online detection.
    """

    def __init__(
        self,
        window_size: int = 100,
        contamination: float = 0.05,
        update_frequency: int = 50
    ):
        """
        Initialize streaming detector.

        Args:
            window_size: Number of recent points to keep
            contamination: Expected anomaly rate
            update_frequency: How often to refit model
        """
        self.window_size = window_size
        self.contamination = contamination
        self.update_frequency = update_frequency

        self.detector = MarketAnomalyDetector(contamination=contamination)
        self.buffer: List[Dict] = []
        self.point_count = 0

    def update(self, data_point: Dict) -> Optional[AnomalyResult]:
        """
        Process a new data point.

        Args:
            data_point: Dict with OHLCV data

        Returns:
            AnomalyResult if detection performed, None if still warming up
        """
        self.buffer.append(data_point)
        self.point_count += 1

        # Keep only recent points
        if len(self.buffer) > self.window_size:
            self.buffer.pop(0)

        # Need minimum data to detect
        if len(self.buffer) < 30:
            return None

        # Refit periodically
        if self.point_count % self.update_frequency == 0:
            df = pd.DataFrame(self.buffer)
            self.detector.fit(df)
            logger.info(f"Refitted detector at point {self.point_count}")

        # Detect on current point
        if self.detector.is_fitted:
            return self.detector.detect_realtime(data_point)

        return None

    def get_recent_anomalies(self) -> List[AnomalyResult]:
        """Get anomalies from current buffer."""
        if not self.detector.is_fitted or len(self.buffer) < 30:
            return []

        df = pd.DataFrame(self.buffer)
        results = self.detector.detect(df)
        return [r for r in results if r.is_anomaly]


# ═══════════════════════════════════════════════════════════════
# ANOMALY-AWARE TRADING FILTER
# ═══════════════════════════════════════════════════════════════


class AnomalyTradingFilter:
    """
    Filter trading signals based on anomaly detection.

    Use to:
    - Block trades during unusual market conditions
    - Reduce position size during volatility spikes
    - Alert on potential flash crashes
    """

    def __init__(
        self,
        detector: MarketAnomalyDetector,
        block_on_anomaly: bool = True,
        reduce_size_threshold: float = -0.3
    ):
        """
        Initialize trading filter.

        Args:
            detector: Fitted MarketAnomalyDetector
            block_on_anomaly: Block all trades during anomalies
            reduce_size_threshold: Score below which to reduce size
        """
        self.detector = detector
        self.block_on_anomaly = block_on_anomaly
        self.reduce_size_threshold = reduce_size_threshold

    def should_trade(self, df: pd.DataFrame) -> Tuple[bool, float, str]:
        """
        Check if trading is safe.

        Args:
            df: Recent OHLCV data

        Returns:
            Tuple of (can_trade, position_multiplier, reason)
        """
        results = self.detector.detect(df)

        if not results:
            return True, 1.0, "No data"

        # Check most recent point
        latest = results[-1]

        if latest.is_anomaly:
            if self.block_on_anomaly:
                return False, 0.0, f"Anomaly detected: {latest.reason}"
            else:
                return True, 0.5, f"Reduced size due to anomaly: {latest.reason}"

        # Check anomaly score
        if latest.anomaly_score < self.reduce_size_threshold:
            multiplier = 0.5 + (latest.anomaly_score - self.reduce_size_threshold)
            multiplier = max(0.3, min(1.0, multiplier))
            return True, multiplier, f"Elevated risk (score: {latest.anomaly_score:.2f})"

        return True, 1.0, "Normal conditions"

    def get_market_condition(self, df: pd.DataFrame) -> str:
        """Get human-readable market condition."""
        can_trade, multiplier, reason = self.should_trade(df)

        if not can_trade:
            return f"DANGEROUS: {reason}"
        elif multiplier < 0.7:
            return f"CAUTION: {reason}"
        else:
            return "NORMAL"


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    # Create sample data with some anomalies
    np.random.seed(42)

    n_points = 500
    dates = pd.date_range(start='2024-01-01', periods=n_points, freq='H')

    # Normal price data
    price = 100 + np.random.randn(n_points).cumsum() * 0.5

    # Inject anomalies
    anomaly_indices = [100, 200, 350, 450]
    for idx in anomaly_indices:
        price[idx] += np.random.choice([-1, 1]) * 10  # Large spike

    df = pd.DataFrame({
        'open': price + np.random.randn(n_points) * 0.2,
        'high': price + abs(np.random.randn(n_points)) * 0.5,
        'low': price - abs(np.random.randn(n_points)) * 0.5,
        'close': price,
        'volume': np.random.randint(1000, 10000, n_points) * (1 + np.random.randn(n_points) * 0.3),
    }, index=dates)

    # Fix volume at anomaly points (spike)
    for idx in anomaly_indices:
        df.iloc[idx, df.columns.get_loc('volume')] *= 5

    # Split data
    train_df = df.iloc[:400]
    test_df = df.iloc[400:]

    # Initialize and fit detector
    print("=" * 60)
    print("ANOMALY DETECTION")
    print("=" * 60)

    detector = MarketAnomalyDetector(contamination=0.05)
    detector.fit(train_df)

    # Detect anomalies in test data
    results = detector.detect(test_df)

    # Print results
    print(f"\nTotal test points: {len(results)}")
    anomalies = [r for r in results if r.is_anomaly]
    print(f"Anomalies detected: {len(anomalies)}")

    print("\nDetected Anomalies:")
    for r in anomalies:
        print(f"  {r.timestamp}: Score={r.anomaly_score:.3f} | {r.reason}")

    # Get statistics
    stats = detector.get_stats(results)
    print(f"\nStatistics:")
    print(f"  Anomaly rate: {stats.anomaly_rate:.2%}")
    print(f"  Avg anomaly score: {stats.avg_anomaly_score:.3f}")

    print(f"\nTop 3 Important Features:")
    sorted_features = sorted(
        stats.feature_importance.items(),
        key=lambda x: x[1],
        reverse=True
    )[:3]
    for name, importance in sorted_features:
        print(f"  {name}: {importance:.3f}")

    # Trading filter example
    print(f"\n{'='*60}")
    print("TRADING FILTER")
    print(f"{'='*60}")

    trading_filter = AnomalyTradingFilter(detector)
    can_trade, multiplier, reason = trading_filter.should_trade(test_df)

    print(f"\nCurrent market condition: {trading_filter.get_market_condition(test_df)}")
    print(f"Can trade: {can_trade}")
    print(f"Position multiplier: {multiplier:.2f}")
    print(f"Reason: {reason}")
