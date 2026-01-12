"""
Dynamic Prompting Pattern Template
==================================
Adapt prompts based on context, history, and performance.

Use when:
- Prompts need to be context-aware
- Performance-based prompt optimization
- A/B testing of prompts
- Personalization required

Placeholders:
- {{MAX_PROMPT_LENGTH}}: Maximum prompt token length
- {{OPTIMIZATION_INTERVAL}}: How often to optimize prompts
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from string import Template
import logging
from datetime import datetime
import random
import json
import re

logger = logging.getLogger(__name__)


@dataclass
class PromptVariant:
    """A variant of a prompt for A/B testing."""
    id: str
    template: str
    success_count: int = 0
    total_count: int = 0
    average_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def success_rate(self) -> float:
        return self.success_count / self.total_count if self.total_count > 0 else 0.5


@dataclass
class PromptContext:
    """Context for prompt generation."""
    task: str
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratedPrompt:
    """A generated prompt with metadata."""
    content: str
    variant_id: Optional[str] = None
    context_used: Dict[str, Any] = field(default_factory=dict)
    token_count: int = 0


class PromptTemplate(ABC):
    """Abstract prompt template."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate(self, context: PromptContext) -> str:
        """Generate prompt from context."""
        pass

    @abstractmethod
    def get_placeholders(self) -> List[str]:
        """Return list of placeholder names."""
        pass


class StringPromptTemplate(PromptTemplate):
    """Simple string-based template."""

    def __init__(self, name: str, template: str):
        super().__init__(name)
        self.template = template
        self._placeholders = self._extract_placeholders()

    def _extract_placeholders(self) -> List[str]:
        """Extract placeholder names from template."""
        return re.findall(r'\{(\w+)\}', self.template)

    def generate(self, context: PromptContext) -> str:
        """Generate prompt by filling placeholders."""
        values = {
            "task": context.task,
            **context.user_preferences,
            **context.metadata
        }
        try:
            return self.template.format(**values)
        except KeyError as e:
            logger.warning(f"Missing placeholder value: {e}")
            return self.template

    def get_placeholders(self) -> List[str]:
        return self._placeholders


class ConditionalPromptTemplate(PromptTemplate):
    """Template with conditional sections."""

    def __init__(self, name: str, base: str, conditions: Dict[str, Dict[str, str]]):
        super().__init__(name)
        self.base = base
        self.conditions = conditions  # {condition_key: {value: additional_prompt}}

    def generate(self, context: PromptContext) -> str:
        """Generate prompt with conditional additions."""
        prompt = self.base

        for condition_key, value_map in self.conditions.items():
            value = context.metadata.get(condition_key)
            if value and value in value_map:
                prompt += "\n" + value_map[value]

        return prompt.format(
            task=context.task,
            **context.user_preferences,
            **context.metadata
        )

    def get_placeholders(self) -> List[str]:
        placeholders = set(re.findall(r'\{(\w+)\}', self.base))
        for value_map in self.conditions.values():
            for template in value_map.values():
                placeholders.update(re.findall(r'\{(\w+)\}', template))
        return list(placeholders)


class PromptOptimizer:
    """Optimize prompts based on performance."""

    def __init__(
        self,
        exploration_rate: float = 0.1,
        min_samples: int = 10
    ):
        self.variants: Dict[str, List[PromptVariant]] = {}
        self.exploration_rate = exploration_rate
        self.min_samples = min_samples

    def add_variant(self, prompt_name: str, variant: PromptVariant):
        """Add a prompt variant for testing."""
        if prompt_name not in self.variants:
            self.variants[prompt_name] = []
        self.variants[prompt_name].append(variant)

    def select_variant(self, prompt_name: str) -> Optional[PromptVariant]:
        """Select best variant using Thompson Sampling."""
        variants = self.variants.get(prompt_name, [])
        if not variants:
            return None

        # Exploration: random selection
        if random.random() < self.exploration_rate:
            return random.choice(variants)

        # Thompson Sampling for exploitation
        samples = []
        for variant in variants:
            # Beta distribution sampling
            alpha = variant.success_count + 1
            beta = variant.total_count - variant.success_count + 1
            sample = random.betavariate(alpha, beta)
            samples.append((sample, variant))

        return max(samples, key=lambda x: x[0])[1]

    def record_outcome(
        self,
        prompt_name: str,
        variant_id: str,
        success: bool,
        score: float
    ):
        """Record outcome for a prompt variant."""
        variants = self.variants.get(prompt_name, [])
        for variant in variants:
            if variant.id == variant_id:
                variant.total_count += 1
                if success:
                    variant.success_count += 1
                # Update running average
                old_avg = variant.average_score
                variant.average_score = old_avg + (score - old_avg) / variant.total_count
                break

    def get_best_variant(self, prompt_name: str) -> Optional[PromptVariant]:
        """Get statistically best variant."""
        variants = self.variants.get(prompt_name, [])
        if not variants:
            return None

        # Only consider variants with enough samples
        qualified = [v for v in variants if v.total_count >= self.min_samples]
        if not qualified:
            return max(variants, key=lambda v: v.total_count)

        return max(qualified, key=lambda v: v.success_rate)


class PromptPersonalizer:
    """Personalize prompts based on user preferences."""

    def __init__(self):
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self.style_templates: Dict[str, str] = {
            "concise": "Be brief and direct. ",
            "detailed": "Provide comprehensive details. ",
            "technical": "Use technical language and precision. ",
            "casual": "Use a friendly, conversational tone. ",
            "formal": "Maintain a professional, formal tone. "
        }
        self.expertise_prefixes: Dict[str, str] = {
            "beginner": "Explain concepts simply. ",
            "intermediate": "",
            "expert": "Skip basic explanations. "
        }

    def set_user_profile(self, user_id: str, profile: Dict[str, Any]):
        """Set user profile for personalization."""
        self.user_profiles[user_id] = profile

    def personalize(self, prompt: str, user_id: str) -> str:
        """Personalize prompt for user."""
        profile = self.user_profiles.get(user_id, {})

        prefix = ""

        # Add style preference
        style = profile.get("style", "detailed")
        if style in self.style_templates:
            prefix += self.style_templates[style]

        # Add expertise level
        expertise = profile.get("expertise", "intermediate")
        if expertise in self.expertise_prefixes:
            prefix += self.expertise_prefixes[expertise]

        # Add custom preferences
        custom_prefs = profile.get("custom_preferences", [])
        for pref in custom_prefs:
            prefix += f"{pref}. "

        return prefix + prompt if prefix else prompt


class DynamicPromptBuilder:
    """
    Build prompts dynamically based on context and performance.

    Example:
        builder = DynamicPromptBuilder()
        builder.add_template("analysis", StringPromptTemplate(...))

        prompt = builder.build(
            template_name="analysis",
            context=PromptContext(task="Analyze XAUUSD"),
            user_id="user123"
        )
    """

    def __init__(
        self,
        max_tokens: int = 4000,
        optimize: bool = True
    ):
        self.templates: Dict[str, PromptTemplate] = {}
        self.optimizer = PromptOptimizer() if optimize else None
        self.personalizer = PromptPersonalizer()
        self.max_tokens = max_tokens
        self.history_context_limit = 5

    def add_template(self, name: str, template: PromptTemplate):
        """Add a prompt template."""
        self.templates[name] = template

    def add_variant(self, template_name: str, variant_id: str, template_str: str):
        """Add a variant for A/B testing."""
        if self.optimizer:
            self.optimizer.add_variant(
                template_name,
                PromptVariant(id=variant_id, template=template_str)
            )

    def build(
        self,
        template_name: str,
        context: PromptContext,
        user_id: Optional[str] = None,
        include_history: bool = True
    ) -> GeneratedPrompt:
        """Build a dynamic prompt."""
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")

        # Check for optimized variant
        variant = None
        if self.optimizer:
            variant = self.optimizer.select_variant(template_name)

        # Generate base prompt
        if variant:
            prompt = variant.template.format(
                task=context.task,
                **context.user_preferences,
                **context.metadata
            )
        else:
            prompt = template.generate(context)

        # Add history context
        if include_history and context.history:
            history_section = self._format_history(context.history)
            prompt = f"{history_section}\n\n{prompt}"

        # Add constraints
        if context.constraints:
            constraints_section = self._format_constraints(context.constraints)
            prompt = f"{prompt}\n\n{constraints_section}"

        # Personalize
        if user_id:
            prompt = self.personalizer.personalize(prompt, user_id)

        # Estimate tokens and truncate if needed
        token_count = self._estimate_tokens(prompt)
        if token_count > self.max_tokens:
            prompt = self._truncate(prompt, self.max_tokens)
            token_count = self.max_tokens

        return GeneratedPrompt(
            content=prompt,
            variant_id=variant.id if variant else None,
            context_used={
                "task": context.task,
                "history_items": len(context.history),
                "constraints": list(context.constraints.keys())
            },
            token_count=token_count
        )

    def record_outcome(
        self,
        template_name: str,
        variant_id: str,
        success: bool,
        score: float
    ):
        """Record prompt outcome for optimization."""
        if self.optimizer and variant_id:
            self.optimizer.record_outcome(template_name, variant_id, success, score)

    def _format_history(self, history: List[Dict[str, Any]]) -> str:
        """Format history for context."""
        recent = history[-self.history_context_limit:]
        lines = ["Previous context:"]
        for item in recent:
            if "query" in item and "result" in item:
                lines.append(f"- Q: {item['query'][:100]}")
                lines.append(f"  A: {item['result'][:100]}")
        return "\n".join(lines)

    def _format_constraints(self, constraints: Dict[str, Any]) -> str:
        """Format constraints."""
        lines = ["Constraints:"]
        for key, value in constraints.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)."""
        return len(text) // 4

    def _truncate(self, text: str, max_tokens: int) -> str:
        """Truncate text to max tokens."""
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text
        return text[:max_chars - 20] + "\n[Truncated...]"


class TradingPromptBuilder(DynamicPromptBuilder):
    """Prompt builder specialized for trading analysis."""

    def __init__(self):
        super().__init__(max_tokens=3000)
        self._setup_trading_templates()

    def _setup_trading_templates(self):
        """Setup trading-specific templates."""
        # Signal analysis template
        self.add_template("signal_analysis", ConditionalPromptTemplate(
            name="signal_analysis",
            base="""Analyze the trading signal for {symbol}.

Current Market Data:
- Price: {price}
- Trend: {trend}
- Volatility: {volatility}

Provide your analysis in this format:
1. Signal Direction (BUY/SELL/NEUTRAL)
2. Confidence (0-100%)
3. Key Reasons
4. Risk Factors
5. Recommended Entry/SL/TP""",
            conditions={
                "market_regime": {
                    "trending": "\nNote: Market is trending - favor momentum strategies.",
                    "ranging": "\nNote: Market is ranging - favor mean reversion.",
                    "volatile": "\nNote: High volatility - reduce position sizes."
                },
                "time_of_day": {
                    "session_open": "\nNote: Session just opened - watch for false breakouts.",
                    "session_close": "\nNote: Session closing - reduce new positions."
                }
            }
        ))

        # Risk assessment template
        self.add_template("risk_assessment", StringPromptTemplate(
            name="risk_assessment",
            template="""Assess the risk for this trade:

Symbol: {symbol}
Direction: {direction}
Position Size: {size}
Account Balance: {balance}

Consider:
1. Position size relative to account
2. Current drawdown status
3. Correlated positions
4. News events
5. Volatility conditions

Provide risk level (LOW/MEDIUM/HIGH/EXTREME) and reasoning."""
        ))

        # Add variants for A/B testing
        self.add_variant(
            "signal_analysis",
            "detailed_v1",
            """Perform comprehensive technical analysis for {symbol}.

Price: {price} | Trend: {trend} | Vol: {volatility}

Required Analysis:
- Multi-timeframe confluence
- Key support/resistance levels
- Momentum indicators
- Volume analysis
- Pattern recognition

Output Format:
SIGNAL: [BUY/SELL/NEUTRAL]
CONFIDENCE: [0-100]%
ENTRY: [price]
SL: [price]
TP: [price]
REASONING: [detailed explanation]"""
        )

        self.add_variant(
            "signal_analysis",
            "concise_v1",
            """Quick {symbol} analysis.
Price: {price}, Trend: {trend}, Vol: {volatility}

Respond with: SIGNAL | CONFIDENCE% | ENTRY | SL | TP | REASON (1 sentence)"""
        )


# Example usage
if __name__ == "__main__":
    # Create builder
    builder = TradingPromptBuilder()

    # Set user profile
    builder.personalizer.set_user_profile("trader1", {
        "style": "technical",
        "expertise": "expert",
        "custom_preferences": ["Focus on risk-reward ratio"]
    })

    # Build prompt
    context = PromptContext(
        task="Generate trading signal",
        metadata={
            "symbol": "XAUUSD",
            "price": 2000.50,
            "trend": "bullish",
            "volatility": "medium",
            "market_regime": "trending"
        },
        history=[
            {"query": "XAUUSD analysis", "result": "Bullish bias, key support at 1980"}
        ],
        constraints={
            "max_risk": "2%",
            "session": "London"
        }
    )

    prompt = builder.build(
        template_name="signal_analysis",
        context=context,
        user_id="trader1"
    )

    print("Generated Prompt:")
    print("-" * 50)
    print(prompt.content)
    print("-" * 50)
    print(f"Variant: {prompt.variant_id}")
    print(f"Token count: {prompt.token_count}")

    # Record outcome
    builder.record_outcome("signal_analysis", prompt.variant_id, True, 0.8)
