"""
Self-Improvement Pattern Template
=================================
Learn from results and improve over time.

Use when:
- System needs to adapt
- Historical data available
- Continuous learning wanted

Placeholders:
- {{LEARNING_RATE}}: How fast to adapt (0-1)
- {{HISTORY_SIZE}}: Number of results to track
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import logging
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)


@dataclass
class Outcome:
    """Record of an action and its outcome."""
    action: Dict[str, Any]
    context: Dict[str, Any]
    result: Any
    success: bool
    score: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Lesson:
    """A learned lesson from outcomes."""
    pattern: str
    condition: Dict[str, Any]
    recommendation: str
    confidence: float
    support: int  # Number of outcomes supporting this lesson


class OutcomeTracker:
    """Track and analyze outcomes."""

    def __init__(self, max_history: int = 1000):
        self.history: deque = deque(maxlen=max_history)

    def record(self, outcome: Outcome):
        """Record an outcome."""
        self.history.append(outcome)

    def get_recent(self, n: int = 100) -> List[Outcome]:
        """Get recent outcomes."""
        return list(self.history)[-n:]

    def get_by_context(self, context_filter: Dict[str, Any]) -> List[Outcome]:
        """Get outcomes matching context."""
        results = []
        for outcome in self.history:
            if all(outcome.context.get(k) == v for k, v in context_filter.items()):
                results.append(outcome)
        return results

    def success_rate(self, context_filter: Optional[Dict[str, Any]] = None) -> float:
        """Calculate success rate."""
        outcomes = self.get_by_context(context_filter) if context_filter else list(self.history)
        if not outcomes:
            return 0
        return sum(1 for o in outcomes if o.success) / len(outcomes)

    def average_score(self, context_filter: Optional[Dict[str, Any]] = None) -> float:
        """Calculate average score."""
        outcomes = self.get_by_context(context_filter) if context_filter else list(self.history)
        if not outcomes:
            return 0
        return sum(o.score for o in outcomes) / len(outcomes)


class LessonLearner:
    """Learn lessons from outcomes."""

    def __init__(self, min_support: int = 5, min_confidence: float = 0.7):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.lessons: List[Lesson] = []

    def learn_from_outcomes(self, outcomes: List[Outcome]) -> List[Lesson]:
        """Extract lessons from outcomes."""
        new_lessons = []

        # Group by context patterns
        patterns = self._find_patterns(outcomes)

        for pattern, pattern_outcomes in patterns.items():
            if len(pattern_outcomes) < self.min_support:
                continue

            success_rate = sum(1 for o in pattern_outcomes if o.success) / len(pattern_outcomes)

            if success_rate >= self.min_confidence:
                # Strong positive pattern
                lesson = Lesson(
                    pattern=pattern,
                    condition=pattern_outcomes[0].context,
                    recommendation="CONTINUE - This pattern works well",
                    confidence=success_rate,
                    support=len(pattern_outcomes)
                )
                new_lessons.append(lesson)
            elif success_rate <= (1 - self.min_confidence):
                # Strong negative pattern
                lesson = Lesson(
                    pattern=pattern,
                    condition=pattern_outcomes[0].context,
                    recommendation="AVOID - This pattern often fails",
                    confidence=1 - success_rate,
                    support=len(pattern_outcomes)
                )
                new_lessons.append(lesson)

        self.lessons.extend(new_lessons)
        return new_lessons

    def _find_patterns(self, outcomes: List[Outcome]) -> Dict[str, List[Outcome]]:
        """Group outcomes by patterns."""
        patterns = {}
        for outcome in outcomes:
            # Create pattern key from context
            key = self._context_to_pattern(outcome.context)
            if key not in patterns:
                patterns[key] = []
            patterns[key].append(outcome)
        return patterns

    def _context_to_pattern(self, context: Dict[str, Any]) -> str:
        """Convert context to pattern string."""
        # Simplified - can be more sophisticated
        sorted_items = sorted(context.items())
        return "|".join(f"{k}={v}" for k, v in sorted_items)

    def get_advice(self, context: Dict[str, Any]) -> Optional[Lesson]:
        """Get advice for a context based on lessons."""
        pattern = self._context_to_pattern(context)

        # Find matching lessons
        for lesson in sorted(self.lessons, key=lambda l: l.confidence, reverse=True):
            if lesson.pattern == pattern:
                return lesson

        return None


class SelfImprovingAgent:
    """
    Agent that improves based on outcomes.

    Example:
        agent = SelfImprovingAgent(
            action_fn=generate_signal,
            evaluation_fn=evaluate_trade
        )
        action = agent.decide(context)
        agent.record_outcome(action, context, result)
    """

    def __init__(
        self,
        action_fn: Callable[[Dict[str, Any]], Any],
        evaluation_fn: Callable[[Any], Tuple[bool, float]],
        learning_rate: float = 0.1
    ):
        self.action_fn = action_fn
        self.evaluation_fn = evaluation_fn
        self.learning_rate = learning_rate

        self.tracker = OutcomeTracker()
        self.learner = LessonLearner()

        # Adjustable parameters
        self.params: Dict[str, float] = {}

    def decide(self, context: Dict[str, Any]) -> Any:
        """Make a decision with learned adjustments."""
        # Check for lessons
        advice = self.learner.get_advice(context)
        if advice:
            logger.info(f"Applying lesson: {advice.recommendation} (conf: {advice.confidence:.0%})")

        # Generate action
        adjusted_context = self._apply_adjustments(context)
        return self.action_fn(adjusted_context)

    def record_outcome(
        self,
        action: Any,
        context: Dict[str, Any],
        result: Any
    ):
        """Record and learn from outcome."""
        success, score = self.evaluation_fn(result)

        outcome = Outcome(
            action={"action": str(action)},
            context=context,
            result=result,
            success=success,
            score=score
        )

        self.tracker.record(outcome)

        # Periodic learning
        if len(self.tracker.history) % 10 == 0:
            self._learn()

    def _learn(self):
        """Learn from recent outcomes."""
        recent = self.tracker.get_recent(100)
        if len(recent) >= 20:
            new_lessons = self.learner.learn_from_outcomes(recent)
            if new_lessons:
                logger.info(f"Learned {len(new_lessons)} new lessons")

            # Adjust parameters based on outcomes
            self._adjust_params(recent)

    def _adjust_params(self, outcomes: List[Outcome]):
        """Adjust parameters based on outcomes."""
        if not outcomes:
            return

        # Calculate performance delta
        recent_score = sum(o.score for o in outcomes[-20:]) / 20
        older_score = sum(o.score for o in outcomes[:-20]) / max(1, len(outcomes) - 20)

        delta = recent_score - older_score

        # If performance improved, reinforce current params
        # If declined, adjust params
        for param_name, param_value in self.params.items():
            if delta < 0:
                # Performance declined - make small adjustment
                adjustment = self.learning_rate * (0.5 - param_value)
                self.params[param_name] = max(0, min(1, param_value + adjustment))

    def _apply_adjustments(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply learned adjustments to context."""
        adjusted = context.copy()

        # Apply parameter adjustments
        for param_name, param_value in self.params.items():
            if param_name in adjusted:
                # Blend original with learned adjustment
                original = adjusted[param_name]
                if isinstance(original, (int, float)):
                    adjusted[param_name] = original * (1 - self.learning_rate) + param_value * self.learning_rate

        return adjusted

    def get_stats(self) -> Dict[str, Any]:
        """Get learning statistics."""
        return {
            "total_outcomes": len(self.tracker.history),
            "success_rate": self.tracker.success_rate(),
            "average_score": self.tracker.average_score(),
            "lessons_learned": len(self.learner.lessons),
            "adjusted_params": self.params.copy()
        }

    def save_state(self, path: str):
        """Save learned state to file."""
        state = {
            "params": self.params,
            "lessons": [
                {
                    "pattern": l.pattern,
                    "condition": l.condition,
                    "recommendation": l.recommendation,
                    "confidence": l.confidence,
                    "support": l.support
                }
                for l in self.learner.lessons
            ]
        }
        with open(path, "w") as f:
            json.dump(state, f, indent=2, default=str)

    def load_state(self, path: str):
        """Load learned state from file."""
        if os.path.exists(path):
            with open(path, "r") as f:
                state = json.load(f)
            self.params = state.get("params", {})
            self.learner.lessons = [
                Lesson(**l) for l in state.get("lessons", [])
            ]


# Example usage
if __name__ == "__main__":
    import random

    # Mock action function
    def generate_signal(context):
        threshold = context.get("threshold", 0.5)
        strength = context.get("signal_strength", 0.5)
        return {"direction": "BUY" if strength > threshold else "NEUTRAL"}

    # Mock evaluation function
    def evaluate_trade(result):
        # Simulate: BUY signals have 60% chance of success
        if result["direction"] == "BUY":
            success = random.random() < 0.6
            score = random.uniform(0.4, 1.0) if success else random.uniform(0, 0.4)
        else:
            success = True  # NEUTRAL is always "safe"
            score = 0.5
        return success, score

    # Create agent
    agent = SelfImprovingAgent(
        action_fn=generate_signal,
        evaluation_fn=evaluate_trade
    )

    # Simulate trading
    for i in range(100):
        context = {
            "signal_strength": random.uniform(0.3, 0.9),
            "threshold": 0.5
        }

        action = agent.decide(context)
        result = {"direction": action["direction"]}
        agent.record_outcome(action, context, result)

    # Print stats
    stats = agent.get_stats()
    print(f"Total outcomes: {stats['total_outcomes']}")
    print(f"Success rate: {stats['success_rate']:.0%}")
    print(f"Lessons learned: {stats['lessons_learned']}")
