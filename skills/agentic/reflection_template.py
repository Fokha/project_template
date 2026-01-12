"""
Reflection Pattern Template
===========================
Self-critique and improvement before final output.

Use when:
- Quality is critical
- Output needs validation
- Iterative improvement needed

Placeholders:
- {{MAX_ITERATIONS}}: Maximum reflection iterations
- {{QUALITY_THRESHOLD}}: Minimum quality score (0-1)
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Critique:
    """Result of self-critique."""
    score: float  # 0-1
    issues: List[str]
    suggestions: List[str]
    should_revise: bool


@dataclass
class ReflectionResult:
    """Final result after reflection."""
    success: bool
    final_output: Any
    iterations: int
    initial_score: float
    final_score: float
    critique_history: List[Critique]
    execution_time_ms: float


class ReflectionAgent:
    """
    Agent that reflects on and improves its output.

    Example:
        agent = ReflectionAgent(llm_client, quality_threshold=0.8)
        result = agent.generate_with_reflection(
            task="Write a trading analysis for XAUUSD",
            context={"price": 2000, "trend": "bullish"}
        )
    """

    def __init__(
        self,
        llm_client: Any,
        max_iterations: int = 3,
        quality_threshold: float = 0.8
    ):
        self.llm = llm_client
        self.max_iterations = max_iterations
        self.quality_threshold = quality_threshold

    def generate_with_reflection(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        custom_critic: Optional[Callable[[Any], Critique]] = None
    ) -> ReflectionResult:
        """Generate output with reflection loop."""
        start_time = datetime.now()
        context = context or {}
        critique_history = []

        # Initial generation
        output = self._generate(task, context)
        initial_critique = custom_critic(output) if custom_critic else self._critique(output, task)
        critique_history.append(initial_critique)
        initial_score = initial_critique.score

        # Reflection loop
        for iteration in range(self.max_iterations):
            if not initial_critique.should_revise:
                break

            # Revise based on critique
            output = self._revise(output, initial_critique, task, context)

            # Re-critique
            critique = custom_critic(output) if custom_critic else self._critique(output, task)
            critique_history.append(critique)

            if not critique.should_revise:
                break

            initial_critique = critique

        final_score = critique_history[-1].score

        return ReflectionResult(
            success=final_score >= self.quality_threshold,
            final_output=output,
            iterations=len(critique_history),
            initial_score=initial_score,
            final_score=final_score,
            critique_history=critique_history,
            execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000
        )

    def _generate(self, task: str, context: Dict[str, Any]) -> str:
        """Generate initial output."""
        prompt = f"""Task: {task}

Context:
{self._format_context(context)}

Provide a thorough and well-structured response."""

        return self.llm.generate(prompt)

    def _critique(self, output: str, task: str) -> Critique:
        """Self-critique the output."""
        prompt = f"""Critique this output for the task: {task}

Output to critique:
{output}

Evaluate on:
1. Completeness - Does it address all aspects?
2. Accuracy - Is the information correct?
3. Clarity - Is it well-organized and clear?
4. Actionability - Can someone act on this?

Respond with JSON:
{{
    "score": 0.0-1.0,
    "issues": ["issue1", "issue2"],
    "suggestions": ["suggestion1", "suggestion2"],
    "should_revise": true/false
}}"""

        response = self.llm.generate(prompt)

        try:
            import json
            data = json.loads(response)
            return Critique(
                score=data.get("score", 0.5),
                issues=data.get("issues", []),
                suggestions=data.get("suggestions", []),
                should_revise=data.get("should_revise", False)
            )
        except:
            # Default critique if parsing fails
            return Critique(
                score=0.5,
                issues=["Could not parse critique"],
                suggestions=["Try again"],
                should_revise=True
            )

    def _revise(
        self,
        output: str,
        critique: Critique,
        task: str,
        context: Dict[str, Any]
    ) -> str:
        """Revise output based on critique."""
        prompt = f"""Revise this output based on the critique.

Original task: {task}

Current output:
{output}

Issues identified:
{chr(10).join(f'- {issue}' for issue in critique.issues)}

Suggestions:
{chr(10).join(f'- {s}' for s in critique.suggestions)}

Provide an improved version that addresses all issues."""

        return self.llm.generate(prompt)

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context for prompt."""
        return "\n".join(f"- {k}: {v}" for k, v in context.items())


class TradingSignalReflector:
    """Specialized reflector for trading signals."""

    def __init__(self, llm_client: Any):
        self.agent = ReflectionAgent(llm_client, max_iterations=2, quality_threshold=0.7)

    def validate_signal(
        self,
        signal: Dict[str, Any],
        market_context: Dict[str, Any]
    ) -> ReflectionResult:
        """Validate and improve a trading signal."""

        def signal_critic(output: str) -> Critique:
            """Custom critic for trading signals."""
            issues = []
            suggestions = []
            score = 1.0

            # Check for required elements
            required = ["direction", "entry", "stop_loss", "take_profit", "confidence"]
            for req in required:
                if req.lower() not in output.lower():
                    issues.append(f"Missing {req}")
                    score -= 0.1

            # Check risk/reward
            if "risk" not in output.lower() or "reward" not in output.lower():
                issues.append("Risk/reward not mentioned")
                suggestions.append("Include risk/reward ratio analysis")
                score -= 0.1

            # Check confidence level
            if "%" not in output:
                suggestions.append("Include specific confidence percentage")
                score -= 0.05

            should_revise = score < 0.7 or len(issues) > 2

            return Critique(
                score=max(0, score),
                issues=issues,
                suggestions=suggestions,
                should_revise=should_revise
            )

        task = f"""Analyze and validate this trading signal:
Signal: {signal}
Market Context: {market_context}

Provide:
1. Signal validation (confirm or reject)
2. Entry, stop loss, take profit levels
3. Risk/reward analysis
4. Confidence level
5. Key factors supporting/against the trade"""

        return self.agent.generate_with_reflection(
            task=task,
            context=market_context,
            custom_critic=signal_critic
        )


class MultiCriteriaReflector:
    """Reflect using multiple criteria."""

    def __init__(self, llm_client: Any, criteria: List[Dict[str, Any]]):
        """
        Args:
            criteria: List of {"name": str, "weight": float, "checker": Callable}
        """
        self.llm = llm_client
        self.criteria = criteria

    def evaluate(self, output: Any) -> Dict[str, Any]:
        """Evaluate output against all criteria."""
        scores = {}
        total_weight = sum(c["weight"] for c in self.criteria)

        for criterion in self.criteria:
            name = criterion["name"]
            checker = criterion["checker"]
            weight = criterion["weight"]

            score = checker(output)
            scores[name] = {
                "score": score,
                "weight": weight,
                "weighted_score": score * weight / total_weight
            }

        overall_score = sum(s["weighted_score"] for s in scores.values())

        return {
            "overall_score": overall_score,
            "criteria_scores": scores,
            "pass": overall_score >= 0.7
        }


# Example usage
if __name__ == "__main__":
    # Mock LLM client
    class MockLLM:
        def __init__(self):
            self.call_count = 0

        def generate(self, prompt: str) -> str:
            self.call_count += 1
            if "critique" in prompt.lower():
                import json
                return json.dumps({
                    "score": 0.6 if self.call_count < 3 else 0.85,
                    "issues": ["Could be more specific"] if self.call_count < 3 else [],
                    "suggestions": ["Add more detail"] if self.call_count < 3 else [],
                    "should_revise": self.call_count < 3
                })
            return f"Generated response #{self.call_count} for: {prompt[:50]}..."

    agent = ReflectionAgent(MockLLM(), max_iterations=3, quality_threshold=0.8)

    result = agent.generate_with_reflection(
        task="Analyze XAUUSD for potential trade entry",
        context={"price": 2000, "trend": "bullish", "sentiment": "positive"}
    )

    print(f"Success: {result.success}")
    print(f"Iterations: {result.iterations}")
    print(f"Score improvement: {result.initial_score:.0%} -> {result.final_score:.0%}")
    print(f"Final output: {result.final_output[:100]}...")
