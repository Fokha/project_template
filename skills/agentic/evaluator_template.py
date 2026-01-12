"""
Evaluator-Optimizer Pattern Template
====================================
Evaluate outputs and optimize parameters based on results.

Use when:
- Parameters need tuning
- A/B testing needed
- Continuous improvement wanted

Placeholders:
- {{METRIC_NAME}}: Primary metric to optimize
- {{OPTIMIZATION_GOAL}}: maximize or minimize
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import logging
from datetime import datetime
import statistics
import random

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Result of an evaluation."""
    score: float
    metrics: Dict[str, float]
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationResult:
    """Result of optimization."""
    best_params: Dict[str, Any]
    best_score: float
    iterations: int
    history: List[Dict[str, Any]]


class Evaluator:
    """
    Evaluate outputs against criteria.

    Example:
        evaluator = Evaluator()
        evaluator.add_metric("accuracy", lambda x: x["correct"] / x["total"])
        evaluator.add_metric("confidence", lambda x: x["confidence"])
        result = evaluator.evaluate(output)
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.metrics: Dict[str, Callable[[Any], float]] = {}
        self.weights = weights or {}

    def add_metric(
        self,
        name: str,
        calculator: Callable[[Any], float],
        weight: float = 1.0
    ) -> "Evaluator":
        """Add a metric to evaluate."""
        self.metrics[name] = calculator
        self.weights[name] = weight
        return self

    def evaluate(self, output: Any) -> EvaluationResult:
        """Evaluate output against all metrics."""
        metrics = {}
        weighted_sum = 0
        total_weight = 0

        for name, calculator in self.metrics.items():
            try:
                score = calculator(output)
                metrics[name] = score
                weight = self.weights.get(name, 1.0)
                weighted_sum += score * weight
                total_weight += weight
            except Exception as e:
                logger.warning(f"Metric {name} failed: {e}")
                metrics[name] = 0

        overall_score = weighted_sum / total_weight if total_weight > 0 else 0

        return EvaluationResult(
            score=overall_score,
            metrics=metrics
        )


class ParameterOptimizer:
    """
    Optimize parameters based on evaluation results.

    Example:
        optimizer = ParameterOptimizer(
            param_space={
                "threshold": (0.5, 0.9, 0.05),  # (min, max, step)
                "window": (5, 20, 1)
            }
        )
        result = optimizer.optimize(
            objective_fn=lambda params: evaluator.evaluate(run_with(params)).score
        )
    """

    def __init__(
        self,
        param_space: Dict[str, Tuple[float, float, float]],
        max_iterations: int = 100,
        patience: int = 10
    ):
        self.param_space = param_space
        self.max_iterations = max_iterations
        self.patience = patience

    def optimize(
        self,
        objective_fn: Callable[[Dict[str, Any]], float],
        maximize: bool = True
    ) -> OptimizationResult:
        """Run optimization."""
        history = []
        best_params = None
        best_score = float("-inf") if maximize else float("inf")
        no_improvement = 0

        for iteration in range(self.max_iterations):
            # Generate candidate parameters
            params = self._generate_params()

            # Evaluate
            try:
                score = objective_fn(params)
            except Exception as e:
                logger.warning(f"Evaluation failed: {e}")
                continue

            history.append({
                "iteration": iteration,
                "params": params,
                "score": score
            })

            # Check if better
            is_better = (score > best_score) if maximize else (score < best_score)
            if is_better:
                best_score = score
                best_params = params.copy()
                no_improvement = 0
            else:
                no_improvement += 1

            # Early stopping
            if no_improvement >= self.patience:
                logger.info(f"Early stopping at iteration {iteration}")
                break

        return OptimizationResult(
            best_params=best_params or {},
            best_score=best_score,
            iterations=len(history),
            history=history
        )

    def _generate_params(self) -> Dict[str, Any]:
        """Generate random parameters from space."""
        params = {}
        for name, (min_val, max_val, step) in self.param_space.items():
            steps = int((max_val - min_val) / step) + 1
            value = min_val + random.randint(0, steps - 1) * step
            params[name] = round(value, 4)
        return params


class GridSearchOptimizer(ParameterOptimizer):
    """Exhaustive grid search optimizer."""

    def optimize(
        self,
        objective_fn: Callable[[Dict[str, Any]], float],
        maximize: bool = True
    ) -> OptimizationResult:
        """Run grid search."""
        history = []
        best_params = None
        best_score = float("-inf") if maximize else float("inf")

        # Generate all combinations
        combinations = self._generate_grid()

        for i, params in enumerate(combinations):
            try:
                score = objective_fn(params)
            except Exception as e:
                logger.warning(f"Evaluation failed: {e}")
                continue

            history.append({
                "iteration": i,
                "params": params,
                "score": score
            })

            is_better = (score > best_score) if maximize else (score < best_score)
            if is_better:
                best_score = score
                best_params = params.copy()

        return OptimizationResult(
            best_params=best_params or {},
            best_score=best_score,
            iterations=len(history),
            history=history
        )

    def _generate_grid(self) -> List[Dict[str, Any]]:
        """Generate all parameter combinations."""
        from itertools import product

        param_lists = {}
        for name, (min_val, max_val, step) in self.param_space.items():
            values = []
            val = min_val
            while val <= max_val:
                values.append(round(val, 4))
                val += step
            param_lists[name] = values

        keys = list(param_lists.keys())
        combinations = []
        for values in product(*param_lists.values()):
            combinations.append(dict(zip(keys, values)))

        return combinations


class TradingEvaluator(Evaluator):
    """Pre-built evaluator for trading signals."""

    def __init__(self):
        super().__init__()

        # Win rate
        self.add_metric("win_rate", self._calc_win_rate, weight=2.0)

        # Profit factor
        self.add_metric("profit_factor", self._calc_profit_factor, weight=2.0)

        # Sharpe ratio
        self.add_metric("sharpe", self._calc_sharpe, weight=1.5)

        # Max drawdown (lower is better, so we invert)
        self.add_metric("drawdown_score", self._calc_drawdown_score, weight=1.0)

        # Signal frequency (moderate is best)
        self.add_metric("frequency_score", self._calc_frequency_score, weight=0.5)

    def _calc_win_rate(self, trades: List[Dict]) -> float:
        if not trades:
            return 0
        wins = sum(1 for t in trades if t.get("profit", 0) > 0)
        return wins / len(trades)

    def _calc_profit_factor(self, trades: List[Dict]) -> float:
        gross_profit = sum(t["profit"] for t in trades if t.get("profit", 0) > 0)
        gross_loss = abs(sum(t["profit"] for t in trades if t.get("profit", 0) < 0))
        return gross_profit / gross_loss if gross_loss > 0 else 0

    def _calc_sharpe(self, trades: List[Dict]) -> float:
        if len(trades) < 2:
            return 0
        returns = [t.get("profit", 0) for t in trades]
        mean_return = statistics.mean(returns)
        std_return = statistics.stdev(returns)
        return mean_return / std_return if std_return > 0 else 0

    def _calc_drawdown_score(self, trades: List[Dict]) -> float:
        # Lower drawdown = higher score
        max_dd = abs(min([t.get("drawdown", 0) for t in trades] or [0]))
        return max(0, 1 - max_dd / 100)  # Assume max DD as percentage

    def _calc_frequency_score(self, trades: List[Dict]) -> float:
        # Optimal frequency: not too many, not too few
        count = len(trades)
        if count < 10:
            return count / 10
        elif count > 100:
            return max(0, 1 - (count - 100) / 100)
        return 1.0


class TradingOptimizer:
    """Optimize trading strategy parameters."""

    def __init__(self, evaluator: TradingEvaluator, backtest_fn: Callable):
        self.evaluator = evaluator
        self.backtest_fn = backtest_fn

    def optimize_strategy(
        self,
        param_space: Dict[str, Tuple[float, float, float]]
    ) -> OptimizationResult:
        """Optimize strategy parameters."""
        optimizer = GridSearchOptimizer(param_space)

        def objective(params):
            trades = self.backtest_fn(params)
            result = self.evaluator.evaluate(trades)
            return result.score

        return optimizer.optimize(objective, maximize=True)


# Example usage
if __name__ == "__main__":
    # Create evaluator
    evaluator = TradingEvaluator()

    # Sample trades
    trades = [
        {"profit": 100, "drawdown": -5},
        {"profit": -50, "drawdown": -10},
        {"profit": 150, "drawdown": -3},
        {"profit": -30, "drawdown": -8},
        {"profit": 80, "drawdown": -4},
    ]

    result = evaluator.evaluate(trades)
    print(f"Overall score: {result.score:.2f}")
    print("Metrics:")
    for name, score in result.metrics.items():
        print(f"  {name}: {score:.2f}")

    # Test optimizer
    def mock_backtest(params):
        # Simulate: higher threshold = fewer but better trades
        count = int(100 * (1 - params["threshold"]))
        win_rate = 0.5 + params["threshold"] * 0.3
        trades = []
        for _ in range(count):
            win = random.random() < win_rate
            trades.append({
                "profit": random.uniform(50, 150) if win else random.uniform(-100, -30),
                "drawdown": random.uniform(-15, -2)
            })
        return trades

    optimizer = TradingOptimizer(evaluator, mock_backtest)
    result = optimizer.optimize_strategy({
        "threshold": (0.5, 0.9, 0.1)
    })

    print(f"\nBest params: {result.best_params}")
    print(f"Best score: {result.best_score:.2f}")
