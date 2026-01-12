"""
Guardrails Pattern Template
===========================
Validate and filter AI outputs for safety and quality.

Use when:
- Output safety is critical
- Quality standards must be met
- Harmful content must be blocked

Placeholders:
- {{STRICTNESS_LEVEL}}: low, medium, or high
- {{ALLOWED_TOPICS}}: List of allowed topics
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)


class ViolationType(Enum):
    HARMFUL_CONTENT = "harmful_content"
    OFF_TOPIC = "off_topic"
    LOW_QUALITY = "low_quality"
    SENSITIVE_DATA = "sensitive_data"
    HALLUCINATION = "hallucination"
    UNSAFE_ACTION = "unsafe_action"


@dataclass
class GuardrailResult:
    """Result of guardrail check."""
    passed: bool
    violations: List[str] = field(default_factory=list)
    violation_types: List[ViolationType] = field(default_factory=list)
    modified_output: Optional[str] = None
    confidence: float = 1.0


class Guardrail(ABC):
    """Abstract base for guardrails."""

    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled

    @abstractmethod
    def check(self, output: Any, context: Dict[str, Any] = None) -> GuardrailResult:
        """Check output against this guardrail."""
        pass


class ContentFilterGuardrail(Guardrail):
    """Filter harmful or inappropriate content."""

    def __init__(
        self,
        blocked_patterns: List[str] = None,
        blocked_words: List[str] = None
    ):
        super().__init__("content_filter")
        self.blocked_patterns = blocked_patterns or []
        self.blocked_words = blocked_words or []

    def check(self, output: Any, context: Dict[str, Any] = None) -> GuardrailResult:
        text = str(output).lower()
        violations = []

        # Check blocked words
        for word in self.blocked_words:
            if word.lower() in text:
                violations.append(f"Blocked word: {word}")

        # Check patterns
        for pattern in self.blocked_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(f"Blocked pattern: {pattern}")

        return GuardrailResult(
            passed=len(violations) == 0,
            violations=violations,
            violation_types=[ViolationType.HARMFUL_CONTENT] if violations else []
        )


class TopicGuardrail(Guardrail):
    """Ensure output stays on topic."""

    def __init__(
        self,
        allowed_topics: List[str],
        topic_keywords: Dict[str, List[str]] = None
    ):
        super().__init__("topic_filter")
        self.allowed_topics = allowed_topics
        self.topic_keywords = topic_keywords or {}

    def check(self, output: Any, context: Dict[str, Any] = None) -> GuardrailResult:
        text = str(output).lower()

        # Check if any allowed topic is present
        on_topic = False
        for topic in self.allowed_topics:
            if topic.lower() in text:
                on_topic = True
                break
            # Check keywords
            keywords = self.topic_keywords.get(topic, [])
            if any(kw.lower() in text for kw in keywords):
                on_topic = True
                break

        if not on_topic and len(text) > 50:  # Allow short responses
            return GuardrailResult(
                passed=False,
                violations=["Output appears off-topic"],
                violation_types=[ViolationType.OFF_TOPIC]
            )

        return GuardrailResult(passed=True)


class QualityGuardrail(Guardrail):
    """Check output quality."""

    def __init__(
        self,
        min_length: int = 10,
        max_length: int = 10000,
        require_structure: bool = False
    ):
        super().__init__("quality_filter")
        self.min_length = min_length
        self.max_length = max_length
        self.require_structure = require_structure

    def check(self, output: Any, context: Dict[str, Any] = None) -> GuardrailResult:
        text = str(output)
        violations = []

        # Length checks
        if len(text) < self.min_length:
            violations.append(f"Output too short ({len(text)} chars)")

        if len(text) > self.max_length:
            violations.append(f"Output too long ({len(text)} chars)")

        # Structure check
        if self.require_structure:
            if not any(marker in text for marker in ["\n", ":", "-", "1.", "*"]):
                violations.append("Output lacks structure")

        return GuardrailResult(
            passed=len(violations) == 0,
            violations=violations,
            violation_types=[ViolationType.LOW_QUALITY] if violations else []
        )


class SensitiveDataGuardrail(Guardrail):
    """Detect and redact sensitive data."""

    def __init__(self, redact: bool = True):
        super().__init__("sensitive_data")
        self.redact = redact
        # Common PII patterns
        self.patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "api_key": r"\b[A-Za-z0-9]{32,}\b"
        }

    def check(self, output: Any, context: Dict[str, Any] = None) -> GuardrailResult:
        text = str(output)
        violations = []
        modified = text

        for data_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                violations.append(f"Detected {data_type}: {len(matches)} instance(s)")
                if self.redact:
                    modified = re.sub(pattern, f"[REDACTED {data_type.upper()}]", modified)

        return GuardrailResult(
            passed=len(violations) == 0,
            violations=violations,
            violation_types=[ViolationType.SENSITIVE_DATA] if violations else [],
            modified_output=modified if self.redact and violations else None
        )


class TradingGuardrail(Guardrail):
    """Trading-specific guardrails."""

    def __init__(
        self,
        max_confidence: float = 1.0,
        require_disclaimer: bool = True,
        block_guaranteed_returns: bool = True
    ):
        super().__init__("trading_guardrail")
        self.max_confidence = max_confidence
        self.require_disclaimer = require_disclaimer
        self.block_guaranteed_returns = block_guaranteed_returns

    def check(self, output: Any, context: Dict[str, Any] = None) -> GuardrailResult:
        text = str(output).lower()
        violations = []

        # Block guaranteed returns language
        if self.block_guaranteed_returns:
            guarantee_phrases = [
                "guaranteed", "100% sure", "definitely will",
                "can't lose", "risk-free", "sure thing"
            ]
            for phrase in guarantee_phrases:
                if phrase in text:
                    violations.append(f"Contains guarantee language: '{phrase}'")

        # Check for disclaimer in trading advice
        if self.require_disclaimer and context:
            is_advice = context.get("is_trading_advice", False)
            if is_advice:
                has_disclaimer = any(d in text for d in [
                    "not financial advice", "risk", "disclaimer",
                    "consult", "own research"
                ])
                if not has_disclaimer:
                    violations.append("Trading advice without risk disclaimer")

        return GuardrailResult(
            passed=len(violations) == 0,
            violations=violations,
            violation_types=[ViolationType.UNSAFE_ACTION] if violations else []
        )


class GuardrailChain:
    """
    Chain multiple guardrails together.

    Example:
        chain = GuardrailChain()
        chain.add(ContentFilterGuardrail(blocked_words=["spam"]))
        chain.add(QualityGuardrail(min_length=20))
        result = chain.check(output)
    """

    def __init__(self, fail_fast: bool = True):
        self.guardrails: List[Guardrail] = []
        self.fail_fast = fail_fast

    def add(self, guardrail: Guardrail) -> "GuardrailChain":
        """Add a guardrail to the chain."""
        self.guardrails.append(guardrail)
        return self

    def check(
        self,
        output: Any,
        context: Dict[str, Any] = None
    ) -> GuardrailResult:
        """Run all guardrails."""
        all_violations = []
        all_types = []
        modified = output

        for guardrail in self.guardrails:
            if not guardrail.enabled:
                continue

            result = guardrail.check(modified, context)

            all_violations.extend(result.violations)
            all_types.extend(result.violation_types)

            if result.modified_output:
                modified = result.modified_output

            if self.fail_fast and not result.passed:
                break

        return GuardrailResult(
            passed=len(all_violations) == 0,
            violations=all_violations,
            violation_types=list(set(all_types)),
            modified_output=modified if modified != output else None
        )


def create_trading_guardrails() -> GuardrailChain:
    """Create standard guardrails for trading outputs."""
    chain = GuardrailChain()

    # Content filter
    chain.add(ContentFilterGuardrail(
        blocked_words=["guaranteed profit", "can't lose", "insider"],
        blocked_patterns=[r"pump\s*and\s*dump", r"get\s*rich\s*quick"]
    ))

    # Quality
    chain.add(QualityGuardrail(
        min_length=20,
        max_length=5000,
        require_structure=False
    ))

    # Sensitive data
    chain.add(SensitiveDataGuardrail(redact=True))

    # Trading specific
    chain.add(TradingGuardrail(
        require_disclaimer=True,
        block_guaranteed_returns=True
    ))

    return chain


# Example usage
if __name__ == "__main__":
    chain = create_trading_guardrails()

    # Test outputs
    test_outputs = [
        "XAUUSD looks bullish. Consider BUY with SL at 1950.",
        "This is a guaranteed profit! You can't lose!",
        "Buy now for 100% returns!",
        "Analysis suggests upside potential. This is not financial advice, always do your own research.",
    ]

    for output in test_outputs:
        result = chain.check(output, {"is_trading_advice": True})
        status = "PASS" if result.passed else "FAIL"
        print(f"\n[{status}] Output: {output[:50]}...")
        if result.violations:
            for v in result.violations:
                print(f"  - {v}")
