"""
Meta-Learning Pattern Template
==============================
Learn how to learn - adapt strategies based on performance.

Use when:
- System needs to improve over time
- Different strategies work in different conditions
- Automatic adaptation desired
- Performance-based strategy selection

Placeholders:
- {{ADAPTATION_RATE}}: How fast to adapt (0-1)
- {{MIN_SAMPLES}}: Minimum samples before learning
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from collections import defaultdict
import logging
from datetime import datetime, timedelta
import json
import math

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for a strategy."""
    success_rate: float = 0.0
    average_score: float = 0.0
    total_executions: int = 0
    recent_trend: float = 0.0  # positive = improving
    volatility: float = 0.0


@dataclass
class StrategyProfile:
    """Profile of a strategy's behavior."""
    name: str
    conditions: Dict[str, Any]  # When strategy works well
    metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    weight: float = 1.0
    last_used: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class LearningOutcome:
    """Outcome of a learning episode."""
    strategy: str
    context: Dict[str, Any]
    success: bool
    score: float
    timestamp: datetime = field(default_factory=datetime.now)


class Strategy(ABC):
    """Abstract strategy that can be meta-learned."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Tuple[Any, float]:
        """Execute strategy, return result and confidence."""
        pass

    @abstractmethod
    def get_applicable_conditions(self) -> Dict[str, Any]:
        """Return conditions where this strategy applies."""
        pass


class StrategySelector:
    """Select best strategy based on context and history."""

    def __init__(self, exploration_rate: float = 0.1):
        self.profiles: Dict[str, StrategyProfile] = {}
        self.exploration_rate = exploration_rate

    def register_strategy(self, strategy: Strategy):
        """Register a strategy."""
        self.profiles[strategy.name] = StrategyProfile(
            name=strategy.name,
            conditions=strategy.get_applicable_conditions()
        )

    def select(
        self,
        strategies: List[Strategy],
        context: Dict[str, Any]
    ) -> Strategy:
        """Select best strategy for context."""
        import random

        # Exploration: occasionally try random strategy
        if random.random() < self.exploration_rate:
            return random.choice(strategies)

        # Exploitation: select based on expected performance
        best_strategy = None
        best_score = float('-inf')

        for strategy in strategies:
            profile = self.profiles.get(strategy.name)
            if profile is None:
                continue

            # Calculate expected score
            score = self._calculate_expected_score(profile, context)

            if score > best_score:
                best_score = score
                best_strategy = strategy

        return best_strategy or strategies[0]

    def _calculate_expected_score(
        self,
        profile: StrategyProfile,
        context: Dict[str, Any]
    ) -> float:
        """Calculate expected score for strategy in context."""
        # Base score from historical performance
        base_score = profile.metrics.average_score * profile.weight

        # Context matching bonus
        match_bonus = self._context_match_score(profile.conditions, context)

        # Recency bonus (prefer recently successful)
        recency_bonus = 0
        if profile.last_used:
            hours_ago = (datetime.now() - profile.last_used).total_seconds() / 3600
            if hours_ago < 24 and profile.metrics.recent_trend > 0:
                recency_bonus = 0.1 * profile.metrics.recent_trend

        # Confidence penalty for high volatility
        volatility_penalty = profile.metrics.volatility * 0.1

        return base_score + match_bonus + recency_bonus - volatility_penalty

    def _context_match_score(
        self,
        conditions: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """Score how well context matches strategy conditions."""
        if not conditions:
            return 0

        matches = 0
        total = len(conditions)

        for key, expected in conditions.items():
            actual = context.get(key)
            if actual is None:
                continue

            if isinstance(expected, (list, tuple)):
                if actual in expected:
                    matches += 1
            elif isinstance(expected, dict):
                # Range check
                min_val = expected.get("min", float('-inf'))
                max_val = expected.get("max", float('inf'))
                if min_val <= actual <= max_val:
                    matches += 1
            elif actual == expected:
                matches += 1

        return matches / total if total > 0 else 0

    def update_profile(self, strategy_name: str, outcome: LearningOutcome):
        """Update strategy profile based on outcome."""
        profile = self.profiles.get(strategy_name)
        if profile is None:
            return

        metrics = profile.metrics
        n = metrics.total_executions

        # Update running averages
        old_avg = metrics.average_score
        metrics.total_executions += 1
        metrics.average_score = old_avg + (outcome.score - old_avg) / metrics.total_executions

        # Update success rate
        old_rate = metrics.success_rate
        success_val = 1.0 if outcome.success else 0.0
        metrics.success_rate = old_rate + (success_val - old_rate) / metrics.total_executions

        # Update volatility (running variance)
        if n > 0:
            metrics.volatility = metrics.volatility + (outcome.score - old_avg) * (outcome.score - metrics.average_score)

        # Update recent trend (exponential moving average of differences)
        trend_alpha = 0.3
        if n > 0:
            recent_diff = outcome.score - old_avg
            metrics.recent_trend = trend_alpha * recent_diff + (1 - trend_alpha) * metrics.recent_trend

        profile.last_used = outcome.timestamp


class MetaLearner:
    """
    Learn and adapt strategy selection over time.

    Example:
        meta = MetaLearner()
        meta.register_strategy(TrendStrategy())
        meta.register_strategy(MeanReversionStrategy())

        strategy = meta.select(context)
        result, score = strategy.execute(context)
        meta.record_outcome(strategy.name, context, score > 0, score)
    """

    def __init__(
        self,
        adaptation_rate: float = 0.1,
        min_samples: int = 10,
        decay_rate: float = 0.99
    ):
        self.selector = StrategySelector()
        self.strategies: Dict[str, Strategy] = {}
        self.outcomes: List[LearningOutcome] = []
        self.adaptation_rate = adaptation_rate
        self.min_samples = min_samples
        self.decay_rate = decay_rate

        # Context patterns that predict success
        self.learned_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def register_strategy(self, strategy: Strategy):
        """Register a learnable strategy."""
        self.strategies[strategy.name] = strategy
        self.selector.register_strategy(strategy)

    def select(self, context: Dict[str, Any]) -> Strategy:
        """Select best strategy for context."""
        return self.selector.select(
            list(self.strategies.values()),
            context
        )

    def record_outcome(
        self,
        strategy_name: str,
        context: Dict[str, Any],
        success: bool,
        score: float
    ):
        """Record outcome and learn from it."""
        outcome = LearningOutcome(
            strategy=strategy_name,
            context=context.copy(),
            success=success,
            score=score
        )
        self.outcomes.append(outcome)

        # Update strategy profile
        self.selector.update_profile(strategy_name, outcome)

        # Learn patterns
        if len(self.outcomes) >= self.min_samples:
            self._learn_patterns()

        # Apply weight decay to all strategies
        self._apply_decay()

    def _learn_patterns(self):
        """Learn success patterns from outcomes."""
        recent = self.outcomes[-100:]  # Last 100 outcomes

        for strategy_name in self.strategies:
            strategy_outcomes = [o for o in recent if o.strategy == strategy_name]
            if len(strategy_outcomes) < 5:
                continue

            # Find common patterns in successful outcomes
            successes = [o for o in strategy_outcomes if o.success]
            if len(successes) < 3:
                continue

            # Extract common context values
            patterns = self._extract_patterns(successes)
            self.learned_patterns[strategy_name] = patterns

            # Update strategy conditions based on patterns
            profile = self.selector.profiles.get(strategy_name)
            if profile and patterns:
                # Merge learned patterns with original conditions
                for pattern in patterns[:3]:  # Top 3 patterns
                    for key, value in pattern.items():
                        if key not in profile.conditions:
                            profile.conditions[key] = value

    def _extract_patterns(self, outcomes: List[LearningOutcome]) -> List[Dict[str, Any]]:
        """Extract common patterns from successful outcomes."""
        if not outcomes:
            return []

        # Count value frequencies for each context key
        key_values: Dict[str, Dict[Any, int]] = defaultdict(lambda: defaultdict(int))

        for outcome in outcomes:
            for key, value in outcome.context.items():
                # Skip complex values
                if isinstance(value, (list, dict)):
                    continue
                key_values[key][value] += 1

        # Find values that appear in >50% of successes
        patterns = []
        threshold = len(outcomes) * 0.5

        pattern = {}
        for key, values in key_values.items():
            for value, count in values.items():
                if count >= threshold:
                    pattern[key] = value

        if pattern:
            patterns.append(pattern)

        return patterns

    def _apply_decay(self):
        """Apply decay to strategy weights."""
        for profile in self.selector.profiles.values():
            profile.weight *= self.decay_rate

    def get_strategy_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all strategies."""
        stats = {}
        for name, strategy in self.strategies.items():
            profile = self.selector.profiles.get(name)
            if profile:
                stats[name] = {
                    "success_rate": profile.metrics.success_rate,
                    "average_score": profile.metrics.average_score,
                    "executions": profile.metrics.total_executions,
                    "trend": profile.metrics.recent_trend,
                    "weight": profile.weight,
                    "learned_patterns": len(self.learned_patterns.get(name, []))
                }
        return stats

    def save_state(self, path: str):
        """Save learned state."""
        state = {
            "profiles": {
                name: {
                    "metrics": {
                        "success_rate": p.metrics.success_rate,
                        "average_score": p.metrics.average_score,
                        "total_executions": p.metrics.total_executions,
                        "recent_trend": p.metrics.recent_trend,
                        "volatility": p.metrics.volatility
                    },
                    "weight": p.weight,
                    "conditions": p.conditions
                }
                for name, p in self.selector.profiles.items()
            },
            "learned_patterns": dict(self.learned_patterns)
        }
        with open(path, "w") as f:
            json.dump(state, f, indent=2, default=str)

    def load_state(self, path: str):
        """Load learned state."""
        try:
            with open(path, "r") as f:
                state = json.load(f)

            for name, data in state.get("profiles", {}).items():
                if name in self.selector.profiles:
                    profile = self.selector.profiles[name]
                    profile.weight = data.get("weight", 1.0)
                    profile.conditions = data.get("conditions", {})

                    metrics_data = data.get("metrics", {})
                    profile.metrics.success_rate = metrics_data.get("success_rate", 0)
                    profile.metrics.average_score = metrics_data.get("average_score", 0)
                    profile.metrics.total_executions = metrics_data.get("total_executions", 0)
                    profile.metrics.recent_trend = metrics_data.get("recent_trend", 0)
                    profile.metrics.volatility = metrics_data.get("volatility", 0)

            self.learned_patterns = defaultdict(list, state.get("learned_patterns", {}))

        except FileNotFoundError:
            logger.warning(f"State file not found: {path}")


# Trading-specific meta-learner
class TradingMetaLearner(MetaLearner):
    """Meta-learner specialized for trading strategies."""

    def __init__(self):
        super().__init__(
            adaptation_rate=0.15,
            min_samples=20,
            decay_rate=0.995
        )
        self.regime_history: List[str] = []

    def get_regime_adjusted_strategy(
        self,
        context: Dict[str, Any],
        regime: str
    ) -> Strategy:
        """Select strategy adjusted for market regime."""
        # Add regime to context
        context["regime"] = regime
        self.regime_history.append(regime)

        # If regime changed, reset exploration temporarily
        if len(self.regime_history) > 1 and self.regime_history[-1] != self.regime_history[-2]:
            original_exploration = self.selector.exploration_rate
            self.selector.exploration_rate = 0.3  # Increase exploration
            strategy = self.select(context)
            self.selector.exploration_rate = original_exploration
            return strategy

        return self.select(context)


# Example strategies
class TrendFollowingStrategy(Strategy):
    def __init__(self):
        super().__init__("trend_following")

    def execute(self, context: Dict[str, Any]) -> Tuple[Any, float]:
        trend = context.get("trend", 0)
        confidence = min(abs(trend) / 100, 1.0)
        direction = "BUY" if trend > 0 else "SELL" if trend < 0 else "NEUTRAL"
        return {"direction": direction, "strategy": self.name}, confidence

    def get_applicable_conditions(self) -> Dict[str, Any]:
        return {
            "regime": ["trending", "strong_trend"],
            "volatility": {"min": 0.5, "max": 2.0}
        }


class MeanReversionStrategy(Strategy):
    def __init__(self):
        super().__init__("mean_reversion")

    def execute(self, context: Dict[str, Any]) -> Tuple[Any, float]:
        deviation = context.get("deviation", 0)
        confidence = min(abs(deviation) / 2, 1.0)
        direction = "SELL" if deviation > 0 else "BUY" if deviation < 0 else "NEUTRAL"
        return {"direction": direction, "strategy": self.name}, confidence

    def get_applicable_conditions(self) -> Dict[str, Any]:
        return {
            "regime": ["ranging", "mean_reverting"],
            "volatility": {"min": 0.2, "max": 1.0}
        }


# Example usage
if __name__ == "__main__":
    import random

    # Create meta-learner
    meta = TradingMetaLearner()
    meta.register_strategy(TrendFollowingStrategy())
    meta.register_strategy(MeanReversionStrategy())

    # Simulate trading
    for i in range(100):
        # Random context
        regime = random.choice(["trending", "ranging", "volatile"])
        context = {
            "regime": regime,
            "trend": random.uniform(-50, 50),
            "deviation": random.uniform(-2, 2),
            "volatility": random.uniform(0.3, 1.5)
        }

        # Select strategy
        strategy = meta.get_regime_adjusted_strategy(context, regime)
        result, confidence = strategy.execute(context)

        # Simulate outcome
        if regime == "trending" and strategy.name == "trend_following":
            success = random.random() < 0.7
            score = random.uniform(0.5, 1.0) if success else random.uniform(-0.5, 0)
        elif regime == "ranging" and strategy.name == "mean_reversion":
            success = random.random() < 0.65
            score = random.uniform(0.3, 0.8) if success else random.uniform(-0.4, 0)
        else:
            success = random.random() < 0.4
            score = random.uniform(-0.3, 0.4)

        # Record outcome
        meta.record_outcome(strategy.name, context, success, score)

    # Print stats
    print("Strategy Statistics:")
    print("-" * 50)
    for name, stats in meta.get_strategy_stats().items():
        print(f"{name}:")
        print(f"  Success Rate: {stats['success_rate']:.1%}")
        print(f"  Avg Score: {stats['average_score']:.3f}")
        print(f"  Executions: {stats['executions']}")
        print(f"  Trend: {stats['trend']:.3f}")
