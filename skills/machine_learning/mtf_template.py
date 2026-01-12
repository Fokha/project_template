# ═══════════════════════════════════════════════════════════════
# MULTI-TIMEFRAME (MTF) ANALYSIS TEMPLATE
# Combine signals from multiple timeframes for robust predictions
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Configure timeframes and weights
# 3. Get confluence signals
#
# Why Multi-Timeframe?
# - Higher timeframes show the trend
# - Lower timeframes show entry timing
# - Confluence increases win rate
#
# ═══════════════════════════════════════════════════════════════

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════


class Timeframe(Enum):
    """Standard trading timeframes."""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"
    MN = "1M"


class SignalDirection(Enum):
    """Signal directions."""
    BUY = 1
    SELL = -1
    NEUTRAL = 0


@dataclass
class TimeframeSignal:
    """Signal from a single timeframe."""
    timeframe: Timeframe
    direction: SignalDirection
    confidence: float
    trend: str                # UP, DOWN, RANGING
    key_levels: Dict = None   # Support/resistance


@dataclass
class MTFSignal:
    """Combined multi-timeframe signal."""
    direction: SignalDirection
    confidence: float
    confluence_score: float    # 0-1, higher = more agreement
    signals: List[TimeframeSignal] = field(default_factory=list)
    aligned_timeframes: int = 0
    total_timeframes: int = 0
    recommendation: str = ""


# ═══════════════════════════════════════════════════════════════
# MTF CONFIGURATION
# ═══════════════════════════════════════════════════════════════


@dataclass
class MTFConfig:
    """Multi-timeframe configuration."""
    # Timeframes to analyze (low to high)
    timeframes: List[Timeframe] = None

    # Weight per timeframe (higher TF = more weight)
    weights: Dict[Timeframe, float] = None

    # Minimum confluence for signal
    min_confluence: float = 0.6

    # Minimum aligned timeframes
    min_aligned: int = 3

    def __post_init__(self):
        if self.timeframes is None:
            # Default: 8 timeframes
            self.timeframes = [
                Timeframe.M5, Timeframe.M15, Timeframe.M30,
                Timeframe.H1, Timeframe.H4, Timeframe.D1,
                Timeframe.W1, Timeframe.MN
            ]

        if self.weights is None:
            # Higher timeframes get more weight
            self.weights = {
                Timeframe.M5: 0.05,
                Timeframe.M15: 0.07,
                Timeframe.M30: 0.08,
                Timeframe.H1: 0.15,
                Timeframe.H4: 0.20,
                Timeframe.D1: 0.20,
                Timeframe.W1: 0.15,
                Timeframe.MN: 0.10,
            }


# ═══════════════════════════════════════════════════════════════
# MTF ANALYZER
# ═══════════════════════════════════════════════════════════════


class MTFAnalyzer:
    """
    Multi-timeframe signal analyzer.

    Combines signals from multiple timeframes using weighted voting.
    """

    def __init__(self, config: MTFConfig = None):
        self.config = config or MTFConfig()
        self.tf_models: Dict[Timeframe, Any] = {}

    def set_model(self, timeframe: Timeframe, model):
        """Set ML model for a specific timeframe."""
        self.tf_models[timeframe] = model

    def analyze(
        self,
        data: Dict[Timeframe, pd.DataFrame]
    ) -> MTFSignal:
        """
        Analyze multiple timeframes and generate combined signal.

        Args:
            data: Dict mapping timeframe to OHLCV DataFrame

        Returns:
            MTFSignal with combined analysis
        """
        signals = []

        for tf in self.config.timeframes:
            if tf not in data:
                logger.warning(f"Missing data for {tf.value}")
                continue

            tf_signal = self._analyze_timeframe(tf, data[tf])
            signals.append(tf_signal)

        return self._combine_signals(signals)

    def _analyze_timeframe(
        self,
        timeframe: Timeframe,
        df: pd.DataFrame
    ) -> TimeframeSignal:
        """Analyze a single timeframe."""
        # Get trend
        trend = self._detect_trend(df)

        # Get signal direction
        direction, confidence = self._get_signal(timeframe, df)

        # Get key levels
        key_levels = self._find_key_levels(df)

        return TimeframeSignal(
            timeframe=timeframe,
            direction=direction,
            confidence=confidence,
            trend=trend,
            key_levels=key_levels,
        )

    def _detect_trend(self, df: pd.DataFrame) -> str:
        """Detect trend direction."""
        if len(df) < 50:
            return "UNKNOWN"

        close = df['close'].values

        # Use EMA crossover for trend
        ema20 = pd.Series(close).ewm(span=20).mean().values
        ema50 = pd.Series(close).ewm(span=50).mean().values

        current_price = close[-1]
        ema20_current = ema20[-1]
        ema50_current = ema50[-1]

        # Check trend strength
        if ema20_current > ema50_current and current_price > ema20_current:
            return "UP"
        elif ema20_current < ema50_current and current_price < ema20_current:
            return "DOWN"
        else:
            return "RANGING"

    def _get_signal(
        self,
        timeframe: Timeframe,
        df: pd.DataFrame
    ) -> Tuple[SignalDirection, float]:
        """Get signal from model or rules."""
        # Use ML model if available
        if timeframe in self.tf_models:
            return self._get_ml_signal(timeframe, df)

        # Otherwise use rule-based signal
        return self._get_rule_signal(df)

    def _get_ml_signal(
        self,
        timeframe: Timeframe,
        df: pd.DataFrame
    ) -> Tuple[SignalDirection, float]:
        """Get signal from ML model."""
        model = self.tf_models[timeframe]

        # Prepare features (simplified - customize for your features)
        features = self._extract_features(df)
        X = features.values.reshape(1, -1)

        # Predict
        pred = model.predict(X)[0]
        proba = model.predict_proba(X)[0]
        confidence = max(proba)

        if pred == 1:
            return SignalDirection.BUY, confidence
        elif pred == 0:
            return SignalDirection.SELL, confidence
        else:
            return SignalDirection.NEUTRAL, confidence

    def _get_rule_signal(
        self,
        df: pd.DataFrame
    ) -> Tuple[SignalDirection, float]:
        """Get rule-based signal."""
        if len(df) < 20:
            return SignalDirection.NEUTRAL, 0.5

        close = df['close'].values

        # Simple RSI + EMA rule
        rsi = self._calculate_rsi(close, 14)
        ema9 = pd.Series(close).ewm(span=9).mean().values[-1]
        ema21 = pd.Series(close).ewm(span=21).mean().values[-1]

        # Buy signal
        if rsi < 40 and ema9 > ema21:
            confidence = min(0.9, 0.5 + (50 - rsi) / 100)
            return SignalDirection.BUY, confidence

        # Sell signal
        if rsi > 60 and ema9 < ema21:
            confidence = min(0.9, 0.5 + (rsi - 50) / 100)
            return SignalDirection.SELL, confidence

        return SignalDirection.NEUTRAL, 0.5

    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate RSI."""
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def _find_key_levels(self, df: pd.DataFrame) -> Dict:
        """Find support and resistance levels."""
        if len(df) < 20:
            return {}

        high = df['high'].values
        low = df['low'].values
        close = df['close'].values[-1]

        # Simple pivot points
        pivot = (high[-1] + low[-1] + close) / 3
        r1 = 2 * pivot - low[-1]
        s1 = 2 * pivot - high[-1]
        r2 = pivot + (high[-1] - low[-1])
        s2 = pivot - (high[-1] - low[-1])

        return {
            "pivot": pivot,
            "resistance_1": r1,
            "resistance_2": r2,
            "support_1": s1,
            "support_2": s2,
        }

    def _extract_features(self, df: pd.DataFrame) -> pd.Series:
        """Extract features for ML model."""
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values

        features = {
            'rsi': self._calculate_rsi(close),
            'ema_ratio': close[-1] / pd.Series(close).ewm(span=20).mean().values[-1],
            'volatility': np.std(close[-20:]) / np.mean(close[-20:]),
            'momentum': (close[-1] - close[-5]) / close[-5] * 100,
        }

        return pd.Series(features)

    def _combine_signals(self, signals: List[TimeframeSignal]) -> MTFSignal:
        """Combine signals using weighted voting."""
        if not signals:
            return MTFSignal(
                direction=SignalDirection.NEUTRAL,
                confidence=0.0,
                confluence_score=0.0,
                recommendation="Insufficient data",
            )

        # Weighted vote
        buy_score = 0.0
        sell_score = 0.0
        total_weight = 0.0

        for signal in signals:
            weight = self.config.weights.get(signal.timeframe, 0.1)
            total_weight += weight

            if signal.direction == SignalDirection.BUY:
                buy_score += weight * signal.confidence
            elif signal.direction == SignalDirection.SELL:
                sell_score += weight * signal.confidence

        # Normalize
        if total_weight > 0:
            buy_score /= total_weight
            sell_score /= total_weight

        # Determine direction
        if buy_score > sell_score and buy_score > 0.5:
            direction = SignalDirection.BUY
            confidence = buy_score
        elif sell_score > buy_score and sell_score > 0.5:
            direction = SignalDirection.SELL
            confidence = sell_score
        else:
            direction = SignalDirection.NEUTRAL
            confidence = max(buy_score, sell_score)

        # Count aligned timeframes
        aligned = sum(1 for s in signals if s.direction == direction)

        # Confluence score
        confluence = aligned / len(signals) if signals else 0

        # Recommendation
        if confluence >= self.config.min_confluence and aligned >= self.config.min_aligned:
            if direction == SignalDirection.BUY:
                recommendation = f"STRONG BUY - {aligned}/{len(signals)} TFs aligned"
            elif direction == SignalDirection.SELL:
                recommendation = f"STRONG SELL - {aligned}/{len(signals)} TFs aligned"
            else:
                recommendation = "WAIT - No clear direction"
        else:
            recommendation = f"WEAK SIGNAL - Only {aligned}/{len(signals)} TFs aligned"

        return MTFSignal(
            direction=direction,
            confidence=confidence,
            confluence_score=confluence,
            signals=signals,
            aligned_timeframes=aligned,
            total_timeframes=len(signals),
            recommendation=recommendation,
        )


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    # Create sample data for multiple timeframes
    np.random.seed(42)

    def create_sample_df(periods: int) -> pd.DataFrame:
        price = 100 + np.random.randn(periods).cumsum()
        return pd.DataFrame({
            'open': price + np.random.randn(periods) * 0.5,
            'high': price + abs(np.random.randn(periods)) * 1.0,
            'low': price - abs(np.random.randn(periods)) * 1.0,
            'close': price,
            'volume': np.random.randint(1000, 10000, periods),
        })

    # Sample data per timeframe
    data = {
        Timeframe.M15: create_sample_df(100),
        Timeframe.H1: create_sample_df(100),
        Timeframe.H4: create_sample_df(100),
        Timeframe.D1: create_sample_df(100),
    }

    # Configure MTF analyzer
    config = MTFConfig(
        timeframes=[Timeframe.M15, Timeframe.H1, Timeframe.H4, Timeframe.D1],
        weights={
            Timeframe.M15: 0.15,
            Timeframe.H1: 0.25,
            Timeframe.H4: 0.30,
            Timeframe.D1: 0.30,
        },
        min_confluence=0.5,
        min_aligned=2,
    )

    analyzer = MTFAnalyzer(config)

    # Analyze
    result = analyzer.analyze(data)

    # Print results
    print(f"\n{'='*60}")
    print("MULTI-TIMEFRAME ANALYSIS")
    print(f"{'='*60}")
    print(f"\nDirection: {result.direction.name}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Confluence: {result.confluence_score:.2%}")
    print(f"Aligned: {result.aligned_timeframes}/{result.total_timeframes} timeframes")
    print(f"\nRecommendation: {result.recommendation}")

    print(f"\nPer-Timeframe Signals:")
    for signal in result.signals:
        print(f"  {signal.timeframe.value}: {signal.direction.name} "
              f"({signal.confidence:.2%}) - Trend: {signal.trend}")
