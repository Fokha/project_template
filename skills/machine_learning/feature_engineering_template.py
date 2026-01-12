# ═══════════════════════════════════════════════════════════════
# FEATURE ENGINEERING TEMPLATE
# Transform raw data into ML-ready features
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Customize feature calculations for your domain
# 3. Run: python feature_engineering_template.py
#
# ═══════════════════════════════════════════════════════════════

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════


@dataclass
class FeatureConfig:
    """Feature engineering configuration."""
    lookback_periods: List[int] = None
    include_technical: bool = True
    include_time: bool = True
    include_lag: bool = True
    lag_periods: List[int] = None
    drop_na: bool = True

    def __post_init__(self):
        if self.lookback_periods is None:
            self.lookback_periods = [5, 10, 20, 50]
        if self.lag_periods is None:
            self.lag_periods = [1, 2, 3, 5]


# ═══════════════════════════════════════════════════════════════
# BASE FEATURE ENGINEER
# ═══════════════════════════════════════════════════════════════


class BaseFeatureEngineer(ABC):
    """Abstract base class for feature engineering."""

    def __init__(self, config: FeatureConfig = None):
        self.config = config or FeatureConfig()
        self.feature_names: List[str] = []

    @abstractmethod
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features from raw data."""
        pass

    def get_feature_names(self) -> List[str]:
        """Get list of created feature names."""
        return self.feature_names


# ═══════════════════════════════════════════════════════════════
# TRADING FEATURE ENGINEER
# ═══════════════════════════════════════════════════════════════


class TradingFeatureEngineer(BaseFeatureEngineer):
    """
    Feature engineering for trading/financial data.

    Creates 100+ features including:
    - Technical indicators (MA, RSI, MACD, BB, etc.)
    - Price patterns (returns, momentum, volatility)
    - Time-based features (hour, day, session)
    - Lag features
    """

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create all features from OHLCV data.

        Expected columns: open, high, low, close, volume (optional)
        """
        df = df.copy()
        self.feature_names = []

        logger.info(f"Starting feature engineering on {len(df)} rows")

        # Technical indicators
        if self.config.include_technical:
            df = self._add_moving_averages(df)
            df = self._add_momentum_indicators(df)
            df = self._add_volatility_indicators(df)
            df = self._add_volume_indicators(df)
            df = self._add_price_patterns(df)

        # Time features
        if self.config.include_time and 'date' in df.columns:
            df = self._add_time_features(df)

        # Lag features
        if self.config.include_lag:
            df = self._add_lag_features(df)

        # Drop NaN if configured
        if self.config.drop_na:
            original_len = len(df)
            df = df.dropna()
            logger.info(f"Dropped {original_len - len(df)} rows with NaN")

        logger.info(f"Created {len(self.feature_names)} features")
        return df

    def _add_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add moving average features."""
        for period in self.config.lookback_periods:
            # Simple Moving Average
            col_name = f'sma_{period}'
            df[col_name] = df['close'].rolling(period).mean()
            self.feature_names.append(col_name)

            # Exponential Moving Average
            col_name = f'ema_{period}'
            df[col_name] = df['close'].ewm(span=period).mean()
            self.feature_names.append(col_name)

            # Price relative to MA
            col_name = f'close_sma_{period}_ratio'
            df[col_name] = df['close'] / df[f'sma_{period}']
            self.feature_names.append(col_name)

        # MA Crossover signals
        if len(self.config.lookback_periods) >= 2:
            fast = self.config.lookback_periods[0]
            slow = self.config.lookback_periods[1]
            df['ma_crossover'] = (df[f'sma_{fast}'] > df[f'sma_{slow}']).astype(int)
            self.feature_names.append('ma_crossover')

        return df

    def _add_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add momentum-based features."""
        # RSI
        for period in [7, 14, 21]:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
            rs = gain / loss
            col_name = f'rsi_{period}'
            df[col_name] = 100 - (100 / (1 + rs))
            self.feature_names.append(col_name)

        # MACD
        ema12 = df['close'].ewm(span=12).mean()
        ema26 = df['close'].ewm(span=26).mean()
        df['macd'] = ema12 - ema26
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        self.feature_names.extend(['macd', 'macd_signal', 'macd_hist'])

        # Momentum
        for period in [5, 10, 20]:
            col_name = f'momentum_{period}'
            df[col_name] = df['close'] - df['close'].shift(period)
            self.feature_names.append(col_name)

        # Rate of Change
        for period in [5, 10, 20]:
            col_name = f'roc_{period}'
            df[col_name] = df['close'].pct_change(period) * 100
            self.feature_names.append(col_name)

        # Stochastic
        for period in [14]:
            low_min = df['low'].rolling(period).min()
            high_max = df['high'].rolling(period).max()
            df[f'stoch_k_{period}'] = 100 * (df['close'] - low_min) / (high_max - low_min)
            df[f'stoch_d_{period}'] = df[f'stoch_k_{period}'].rolling(3).mean()
            self.feature_names.extend([f'stoch_k_{period}', f'stoch_d_{period}'])

        return df

    def _add_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volatility-based features."""
        # ATR
        for period in [7, 14, 21]:
            high_low = df['high'] - df['low']
            high_close = abs(df['high'] - df['close'].shift())
            low_close = abs(df['low'] - df['close'].shift())
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            col_name = f'atr_{period}'
            df[col_name] = tr.rolling(period).mean()
            self.feature_names.append(col_name)

        # Bollinger Bands
        for period in [20]:
            sma = df['close'].rolling(period).mean()
            std = df['close'].rolling(period).std()
            df[f'bb_upper_{period}'] = sma + (std * 2)
            df[f'bb_lower_{period}'] = sma - (std * 2)
            df[f'bb_width_{period}'] = (df[f'bb_upper_{period}'] - df[f'bb_lower_{period}']) / sma
            df[f'bb_position_{period}'] = (df['close'] - df[f'bb_lower_{period}']) / (
                df[f'bb_upper_{period}'] - df[f'bb_lower_{period}']
            )
            self.feature_names.extend([
                f'bb_upper_{period}', f'bb_lower_{period}',
                f'bb_width_{period}', f'bb_position_{period}'
            ])

        # Standard deviation
        for period in self.config.lookback_periods:
            col_name = f'std_{period}'
            df[col_name] = df['close'].rolling(period).std()
            self.feature_names.append(col_name)

        # Historical volatility
        df['returns'] = df['close'].pct_change()
        for period in [10, 20]:
            col_name = f'volatility_{period}'
            df[col_name] = df['returns'].rolling(period).std() * np.sqrt(252)
            self.feature_names.append(col_name)

        return df

    def _add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based features."""
        if 'volume' not in df.columns:
            return df

        # Volume MA
        for period in [5, 10, 20]:
            col_name = f'volume_sma_{period}'
            df[col_name] = df['volume'].rolling(period).mean()
            self.feature_names.append(col_name)

        # Volume ratio
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
        self.feature_names.append('volume_ratio')

        # OBV (On-Balance Volume)
        df['obv'] = (np.sign(df['close'].diff()) * df['volume']).cumsum()
        self.feature_names.append('obv')

        # VWAP
        df['vwap'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()
        self.feature_names.append('vwap')

        return df

    def _add_price_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add price pattern features."""
        # Candle patterns
        df['body'] = df['close'] - df['open']
        df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
        df['body_ratio'] = abs(df['body']) / (df['high'] - df['low'] + 0.0001)
        self.feature_names.extend(['body', 'upper_shadow', 'lower_shadow', 'body_ratio'])

        # Gap
        df['gap'] = df['open'] - df['close'].shift(1)
        df['gap_pct'] = df['gap'] / df['close'].shift(1) * 100
        self.feature_names.extend(['gap', 'gap_pct'])

        # High-Low range
        df['range'] = df['high'] - df['low']
        df['range_pct'] = df['range'] / df['close'] * 100
        self.feature_names.extend(['range', 'range_pct'])

        # Returns
        for period in [1, 2, 3, 5, 10]:
            col_name = f'return_{period}'
            df[col_name] = df['close'].pct_change(period)
            self.feature_names.append(col_name)

        return df

    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features."""
        df['date'] = pd.to_datetime(df['date'])

        # Basic time features
        df['hour'] = df['date'].dt.hour
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        self.feature_names.extend(['hour', 'day_of_week', 'day_of_month', 'month', 'quarter'])

        # Trading session (simplified)
        df['is_london'] = ((df['hour'] >= 8) & (df['hour'] < 17)).astype(int)
        df['is_newyork'] = ((df['hour'] >= 13) & (df['hour'] < 22)).astype(int)
        df['is_overlap'] = ((df['hour'] >= 13) & (df['hour'] < 17)).astype(int)
        self.feature_names.extend(['is_london', 'is_newyork', 'is_overlap'])

        # Cyclical encoding
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        self.feature_names.extend(['hour_sin', 'hour_cos', 'dow_sin', 'dow_cos'])

        return df

    def _add_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add lagged features."""
        lag_columns = ['close', 'returns', 'volume'] if 'volume' in df.columns else ['close', 'returns']

        for col in lag_columns:
            if col not in df.columns:
                continue
            for lag in self.config.lag_periods:
                col_name = f'{col}_lag_{lag}'
                df[col_name] = df[col].shift(lag)
                self.feature_names.append(col_name)

        return df


# ═══════════════════════════════════════════════════════════════
# FEATURE SELECTOR
# ═══════════════════════════════════════════════════════════════


class FeatureSelector:
    """Select most important features."""

    def __init__(self, n_features: int = 50):
        self.n_features = n_features
        self.selected_features: List[str] = []

    def select_by_importance(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        model=None
    ) -> List[str]:
        """Select features by model importance."""
        if model is None:
            from sklearn.ensemble import RandomForestClassifier
            model = RandomForestClassifier(n_estimators=100, random_state=42)

        model.fit(X, y)

        importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)

        self.selected_features = importance.head(self.n_features)['feature'].tolist()
        return self.selected_features

    def select_by_correlation(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        threshold: float = 0.05
    ) -> List[str]:
        """Select features correlated with target."""
        correlations = X.corrwith(y).abs().sort_values(ascending=False)
        self.selected_features = correlations[correlations > threshold].index.tolist()
        return self.selected_features[:self.n_features]


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    # Create sample OHLCV data
    np.random.seed(42)
    n_samples = 1000

    dates = pd.date_range('2023-01-01', periods=n_samples, freq='H')
    price = 100 + np.random.randn(n_samples).cumsum()

    df = pd.DataFrame({
        'date': dates,
        'open': price + np.random.randn(n_samples) * 0.5,
        'high': price + abs(np.random.randn(n_samples)) * 1.0,
        'low': price - abs(np.random.randn(n_samples)) * 1.0,
        'close': price,
        'volume': np.random.randint(1000, 10000, n_samples),
    })

    # Create target
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)

    # Feature engineering
    config = FeatureConfig(
        lookback_periods=[5, 10, 20, 50],
        include_technical=True,
        include_time=True,
        include_lag=True,
    )

    engineer = TradingFeatureEngineer(config)
    df_features = engineer.create_features(df)

    print(f"\n{'='*60}")
    print("FEATURE ENGINEERING RESULTS")
    print(f"{'='*60}")
    print(f"Original columns: {len(df.columns)}")
    print(f"Total features created: {len(engineer.feature_names)}")
    print(f"Final dataframe shape: {df_features.shape}")
    print(f"\nSample features:")
    for feat in engineer.feature_names[:10]:
        print(f"  - {feat}")
    print(f"  ... and {len(engineer.feature_names) - 10} more")
