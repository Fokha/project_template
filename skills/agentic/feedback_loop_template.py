"""
Feedback Loop Pattern Template
==============================
Continuous improvement through outcome feedback.

Use when:
- System should improve over time
- Outcomes can be measured
- Historical data can inform decisions
- Automated retraining desired

Placeholders:
- {{FEEDBACK_WINDOW}}: Days of feedback to consider
- {{RETRAIN_THRESHOLD}}: Performance drop triggering retrain
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime, timedelta
import logging
import json
import statistics

logger = logging.getLogger(__name__)


@dataclass
class Feedback:
    """Feedback on a prediction/action."""
    prediction_id: str
    prediction: Dict[str, Any]
    actual_outcome: Dict[str, Any]
    score: float  # -1 to 1 typically
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_positive(self) -> bool:
        return self.score > 0


@dataclass
class PerformanceSnapshot:
    """Snapshot of system performance."""
    timestamp: datetime
    success_rate: float
    average_score: float
    sample_size: int
    volatility: float
    trend: float  # positive = improving


@dataclass
class RetrainingTrigger:
    """Trigger for model retraining."""
    triggered: bool
    reason: str
    severity: str  # low, medium, high, critical
    recommended_action: str
    metrics: Dict[str, float] = field(default_factory=dict)


class FeedbackCollector:
    """Collect and store feedback."""

    def __init__(self, max_history: int = 10000):
        self.feedback: deque = deque(maxlen=max_history)
        self.by_category: Dict[str, List[Feedback]] = {}

    def record(self, feedback: Feedback, category: Optional[str] = None):
        """Record feedback."""
        self.feedback.append(feedback)

        if category:
            if category not in self.by_category:
                self.by_category[category] = []
            self.by_category[category].append(feedback)

    def get_recent(self, days: int = 7) -> List[Feedback]:
        """Get feedback from recent days."""
        cutoff = datetime.now() - timedelta(days=days)
        return [f for f in self.feedback if f.timestamp >= cutoff]

    def get_by_category(self, category: str) -> List[Feedback]:
        """Get feedback by category."""
        return self.by_category.get(category, [])

    def get_feedback_for_prediction(self, prediction_id: str) -> Optional[Feedback]:
        """Get feedback for a specific prediction."""
        for f in self.feedback:
            if f.prediction_id == prediction_id:
                return f
        return None


class PerformanceAnalyzer:
    """Analyze performance from feedback."""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.history: List[PerformanceSnapshot] = []

    def analyze(self, feedback_list: List[Feedback]) -> PerformanceSnapshot:
        """Analyze feedback to generate performance snapshot."""
        if not feedback_list:
            return PerformanceSnapshot(
                timestamp=datetime.now(),
                success_rate=0,
                average_score=0,
                sample_size=0,
                volatility=0,
                trend=0
            )

        scores = [f.score for f in feedback_list]
        successes = [1 if f.is_positive else 0 for f in feedback_list]

        snapshot = PerformanceSnapshot(
            timestamp=datetime.now(),
            success_rate=sum(successes) / len(successes),
            average_score=statistics.mean(scores),
            sample_size=len(feedback_list),
            volatility=statistics.stdev(scores) if len(scores) > 1 else 0,
            trend=self._calculate_trend(scores)
        )

        self.history.append(snapshot)
        return snapshot

    def _calculate_trend(self, scores: List[float]) -> float:
        """Calculate score trend (positive = improving)."""
        if len(scores) < 10:
            return 0

        # Compare first half to second half
        mid = len(scores) // 2
        first_half = statistics.mean(scores[:mid])
        second_half = statistics.mean(scores[mid:])

        return second_half - first_half

    def get_trend_analysis(self, periods: int = 5) -> Dict[str, Any]:
        """Analyze trend over multiple periods."""
        if len(self.history) < periods:
            return {"status": "insufficient_data", "periods": len(self.history)}

        recent = self.history[-periods:]
        trends = [s.trend for s in recent]
        success_rates = [s.success_rate for s in recent]

        return {
            "status": "ok",
            "average_trend": statistics.mean(trends),
            "trend_direction": "improving" if statistics.mean(trends) > 0 else "declining",
            "success_rate_trend": success_rates[-1] - success_rates[0],
            "volatility_trend": recent[-1].volatility - recent[0].volatility,
            "periods_analyzed": periods
        }


class RetrainingDecider:
    """Decide when to trigger retraining."""

    def __init__(
        self,
        success_threshold: float = 0.5,
        decline_threshold: float = -0.1,
        min_samples: int = 50
    ):
        self.success_threshold = success_threshold
        self.decline_threshold = decline_threshold
        self.min_samples = min_samples
        self.last_retrain: Optional[datetime] = None
        self.cooldown_hours: int = 24

    def should_retrain(
        self,
        current: PerformanceSnapshot,
        baseline: Optional[PerformanceSnapshot] = None
    ) -> RetrainingTrigger:
        """Decide if retraining is needed."""
        # Check cooldown
        if self.last_retrain:
            hours_since = (datetime.now() - self.last_retrain).total_seconds() / 3600
            if hours_since < self.cooldown_hours:
                return RetrainingTrigger(
                    triggered=False,
                    reason="In cooldown period",
                    severity="low",
                    recommended_action="wait",
                    metrics={"hours_remaining": self.cooldown_hours - hours_since}
                )

        # Check minimum samples
        if current.sample_size < self.min_samples:
            return RetrainingTrigger(
                triggered=False,
                reason="Insufficient samples",
                severity="low",
                recommended_action="collect_more_data",
                metrics={"current_samples": current.sample_size, "required": self.min_samples}
            )

        # Check absolute success rate
        if current.success_rate < self.success_threshold:
            return RetrainingTrigger(
                triggered=True,
                reason="Success rate below threshold",
                severity="high",
                recommended_action="full_retrain",
                metrics={
                    "current_rate": current.success_rate,
                    "threshold": self.success_threshold
                }
            )

        # Check relative decline from baseline
        if baseline:
            decline = baseline.success_rate - current.success_rate
            if decline > abs(self.decline_threshold):
                return RetrainingTrigger(
                    triggered=True,
                    reason="Performance decline from baseline",
                    severity="medium",
                    recommended_action="incremental_retrain",
                    metrics={
                        "baseline_rate": baseline.success_rate,
                        "current_rate": current.success_rate,
                        "decline": decline
                    }
                )

        # Check trend
        if current.trend < self.decline_threshold:
            return RetrainingTrigger(
                triggered=True,
                reason="Negative performance trend",
                severity="medium",
                recommended_action="investigate_and_retrain",
                metrics={"trend": current.trend}
            )

        return RetrainingTrigger(
            triggered=False,
            reason="Performance acceptable",
            severity="low",
            recommended_action="continue_monitoring",
            metrics={
                "success_rate": current.success_rate,
                "trend": current.trend
            }
        )

    def mark_retrained(self):
        """Mark that retraining occurred."""
        self.last_retrain = datetime.now()


class FeedbackLoop:
    """
    Complete feedback loop system.

    Example:
        loop = FeedbackLoop(
            predictor=my_model.predict,
            retrainer=my_model.retrain
        )

        # Make prediction
        prediction = loop.predict({"symbol": "XAUUSD"})

        # Later, record outcome
        loop.record_outcome(
            prediction_id=prediction["id"],
            actual={"direction": "up", "profit": 50}
        )

        # Check if retraining needed
        trigger = loop.check_retraining()
        if trigger.triggered:
            loop.retrain()
    """

    def __init__(
        self,
        predictor: Callable[[Dict[str, Any]], Dict[str, Any]],
        retrainer: Optional[Callable[[List[Feedback]], None]] = None,
        feedback_window_days: int = 30
    ):
        self.predictor = predictor
        self.retrainer = retrainer
        self.feedback_window = feedback_window_days

        self.collector = FeedbackCollector()
        self.analyzer = PerformanceAnalyzer()
        self.decider = RetrainingDecider()

        self.predictions: Dict[str, Dict[str, Any]] = {}
        self.baseline: Optional[PerformanceSnapshot] = None

    def predict(
        self,
        input_data: Dict[str, Any],
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make a prediction and track it."""
        prediction = self.predictor(input_data)

        # Assign ID if not present
        if "id" not in prediction:
            prediction["id"] = f"pred_{datetime.now().timestamp()}"

        # Store for later feedback matching
        self.predictions[prediction["id"]] = {
            "input": input_data,
            "output": prediction,
            "category": category,
            "timestamp": datetime.now()
        }

        return prediction

    def record_outcome(
        self,
        prediction_id: str,
        actual: Dict[str, Any],
        score: Optional[float] = None
    ):
        """Record the actual outcome for a prediction."""
        if prediction_id not in self.predictions:
            logger.warning(f"Unknown prediction ID: {prediction_id}")
            return

        pred_data = self.predictions[prediction_id]

        # Calculate score if not provided
        if score is None:
            score = self._calculate_score(pred_data["output"], actual)

        feedback = Feedback(
            prediction_id=prediction_id,
            prediction=pred_data["output"],
            actual_outcome=actual,
            score=score,
            metadata={"input": pred_data["input"]}
        )

        self.collector.record(feedback, pred_data.get("category"))

        # Clean up old prediction
        del self.predictions[prediction_id]

    def _calculate_score(
        self,
        prediction: Dict[str, Any],
        actual: Dict[str, Any]
    ) -> float:
        """Calculate score based on prediction vs actual."""
        # Default implementation - override for specific use cases
        if "direction" in prediction and "direction" in actual:
            if prediction["direction"] == actual["direction"]:
                return 1.0
            return -1.0

        if "value" in prediction and "value" in actual:
            error = abs(prediction["value"] - actual["value"])
            max_error = max(abs(actual["value"]), 1)
            return 1 - min(error / max_error, 1)

        return 0

    def get_performance(self) -> PerformanceSnapshot:
        """Get current performance snapshot."""
        recent = self.collector.get_recent(self.feedback_window)
        return self.analyzer.analyze(recent)

    def check_retraining(self) -> RetrainingTrigger:
        """Check if retraining is needed."""
        current = self.get_performance()
        return self.decider.should_retrain(current, self.baseline)

    def retrain(self, force: bool = False) -> bool:
        """Trigger retraining if needed or forced."""
        if not self.retrainer:
            logger.warning("No retrainer configured")
            return False

        trigger = self.check_retraining()
        if not force and not trigger.triggered:
            return False

        logger.info(f"Starting retraining: {trigger.reason}")

        # Get feedback for retraining
        feedback = self.collector.get_recent(self.feedback_window)

        try:
            self.retrainer(feedback)
            self.decider.mark_retrained()

            # Update baseline
            self.baseline = self.get_performance()

            logger.info("Retraining completed successfully")
            return True

        except Exception as e:
            logger.error(f"Retraining failed: {e}")
            return False

    def get_insights(self) -> Dict[str, Any]:
        """Get insights from feedback analysis."""
        current = self.get_performance()
        trend = self.analyzer.get_trend_analysis()

        # Analyze by category
        category_performance = {}
        for category in self.collector.by_category:
            cat_feedback = self.collector.get_by_category(category)
            if cat_feedback:
                scores = [f.score for f in cat_feedback[-100:]]
                category_performance[category] = {
                    "success_rate": sum(1 for f in cat_feedback[-100:] if f.is_positive) / len(cat_feedback[-100:]),
                    "average_score": statistics.mean(scores),
                    "sample_size": len(cat_feedback)
                }

        return {
            "current_performance": {
                "success_rate": current.success_rate,
                "average_score": current.average_score,
                "volatility": current.volatility,
                "trend": current.trend
            },
            "trend_analysis": trend,
            "category_breakdown": category_performance,
            "total_feedback": len(self.collector.feedback),
            "baseline": {
                "success_rate": self.baseline.success_rate if self.baseline else None,
                "set_at": self.baseline.timestamp.isoformat() if self.baseline else None
            }
        }


class TradingFeedbackLoop(FeedbackLoop):
    """Feedback loop specialized for trading signals."""

    def __init__(
        self,
        signal_predictor: Callable[[Dict[str, Any]], Dict[str, Any]],
        retrainer: Optional[Callable[[List[Feedback]], None]] = None
    ):
        super().__init__(signal_predictor, retrainer, feedback_window_days=30)
        self.profit_threshold = 0

    def _calculate_score(
        self,
        prediction: Dict[str, Any],
        actual: Dict[str, Any]
    ) -> float:
        """Calculate score based on trading outcome."""
        # Direction accuracy
        pred_direction = prediction.get("direction", "NEUTRAL")
        actual_direction = actual.get("direction", "NEUTRAL")
        direction_correct = pred_direction == actual_direction

        # Profit/loss
        profit = actual.get("profit", 0)
        risk = actual.get("risk", 1)

        # Risk-adjusted score
        if profit > 0:
            score = min(profit / risk, 2.0)  # Cap at 2R
        else:
            score = max(profit / risk, -1.0)  # Floor at -1R

        # Bonus for correct direction
        if direction_correct:
            score += 0.2

        return max(-1, min(1, score))  # Normalize to [-1, 1]

    def record_trade_outcome(
        self,
        prediction_id: str,
        entry_price: float,
        exit_price: float,
        direction: str,
        profit: float
    ):
        """Record trade outcome."""
        actual = {
            "direction": direction,
            "entry": entry_price,
            "exit": exit_price,
            "profit": profit,
            "risk": abs(entry_price - exit_price)  # Simple risk estimate
        }
        self.record_outcome(prediction_id, actual)


# Example usage
if __name__ == "__main__":
    import random

    # Mock predictor
    def mock_predictor(data: Dict[str, Any]) -> Dict[str, Any]:
        directions = ["BUY", "SELL", "NEUTRAL"]
        return {
            "direction": random.choice(directions),
            "confidence": random.uniform(0.5, 0.9),
            "symbol": data.get("symbol", "UNKNOWN")
        }

    # Mock retrainer
    def mock_retrainer(feedback: List[Feedback]):
        print(f"Retraining with {len(feedback)} samples")

    # Create feedback loop
    loop = TradingFeedbackLoop(mock_predictor, mock_retrainer)

    # Simulate predictions and outcomes
    print("Simulating 100 predictions...")
    for i in range(100):
        # Make prediction
        pred = loop.predict({"symbol": "XAUUSD"}, category="metals")

        # Simulate outcome
        actual_direction = random.choice(["BUY", "SELL", "NEUTRAL"])
        profit = random.uniform(-100, 150) if pred["direction"] == actual_direction else random.uniform(-150, 50)

        loop.record_trade_outcome(
            prediction_id=pred["id"],
            entry_price=2000,
            exit_price=2000 + (profit / 10),
            direction=actual_direction,
            profit=profit
        )

    # Get insights
    print("\nFeedback Loop Insights:")
    print("-" * 50)
    insights = loop.get_insights()
    print(f"Success Rate: {insights['current_performance']['success_rate']:.1%}")
    print(f"Average Score: {insights['current_performance']['average_score']:.3f}")
    print(f"Trend: {insights['current_performance']['trend']:.3f}")
    print(f"Total Feedback: {insights['total_feedback']}")

    # Check retraining
    print("\nRetraining Check:")
    trigger = loop.check_retraining()
    print(f"Triggered: {trigger.triggered}")
    print(f"Reason: {trigger.reason}")
    print(f"Severity: {trigger.severity}")
    print(f"Action: {trigger.recommended_action}")
