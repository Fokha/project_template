"""
Prompt Chaining Pattern Template
================================
Sequential processing where each step's output feeds into the next.

Use when:
- Complex tasks need to be broken into steps
- Each step depends on the previous result
- You need structured, predictable output

Placeholders:
- {{CHAIN_NAME}}: Name of this chain
- {{STEP_COUNT}}: Number of steps in chain
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ChainStep:
    """A single step in the prompt chain."""
    name: str
    prompt_template: str
    output_key: str
    required_inputs: List[str] = field(default_factory=list)
    validator: Optional[Callable[[Any], bool]] = None
    transformer: Optional[Callable[[Any], Any]] = None


@dataclass
class ChainResult:
    """Result of chain execution."""
    success: bool
    outputs: Dict[str, Any]
    steps_completed: int
    total_steps: int
    error: Optional[str] = None
    execution_time_ms: float = 0


class PromptChain:
    """
    Execute a sequence of prompts where each step builds on previous results.

    Example:
        chain = PromptChain("analysis_chain")
        chain.add_step(ChainStep(
            name="extract",
            prompt_template="Extract key entities from: {input_text}",
            output_key="entities"
        ))
        chain.add_step(ChainStep(
            name="analyze",
            prompt_template="Analyze these entities: {entities}",
            output_key="analysis",
            required_inputs=["entities"]
        ))
        result = chain.execute({"input_text": "..."}, llm_client)
    """

    def __init__(self, name: str):
        self.name = name
        self.steps: List[ChainStep] = []
        self.context: Dict[str, Any] = {}

    def add_step(self, step: ChainStep) -> "PromptChain":
        """Add a step to the chain."""
        self.steps.append(step)
        return self

    def execute(
        self,
        initial_input: Dict[str, Any],
        llm_client: Any,
        stop_on_error: bool = True
    ) -> ChainResult:
        """Execute all steps in sequence."""
        start_time = datetime.now()
        self.context = initial_input.copy()
        outputs = {}
        steps_completed = 0

        for i, step in enumerate(self.steps):
            logger.info(f"Executing step {i+1}/{len(self.steps)}: {step.name}")

            try:
                # Check required inputs
                missing = [k for k in step.required_inputs if k not in self.context]
                if missing:
                    raise ValueError(f"Missing required inputs: {missing}")

                # Build prompt
                prompt = step.prompt_template.format(**self.context)

                # Execute LLM call
                response = llm_client.generate(prompt)

                # Transform if needed
                result = response
                if step.transformer:
                    result = step.transformer(response)

                # Validate if needed
                if step.validator and not step.validator(result):
                    raise ValueError(f"Validation failed for step: {step.name}")

                # Store result
                outputs[step.output_key] = result
                self.context[step.output_key] = result
                steps_completed += 1

            except Exception as e:
                logger.error(f"Step {step.name} failed: {e}")
                if stop_on_error:
                    return ChainResult(
                        success=False,
                        outputs=outputs,
                        steps_completed=steps_completed,
                        total_steps=len(self.steps),
                        error=str(e),
                        execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000
                    )

        return ChainResult(
            success=True,
            outputs=outputs,
            steps_completed=steps_completed,
            total_steps=len(self.steps),
            execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000
        )


class TradingAnalysisChain(PromptChain):
    """
    Pre-built chain for trading analysis.
    Steps: Extract data -> Analyze trend -> Generate signal -> Validate
    """

    def __init__(self):
        super().__init__("trading_analysis")

        # Step 1: Extract market data
        self.add_step(ChainStep(
            name="extract_data",
            prompt_template="""
            Extract key market data for {symbol}:
            - Current price and recent price action
            - Key support/resistance levels
            - Volume trends
            - Any notable patterns

            Price data: {price_data}
            """,
            output_key="extracted_data"
        ))

        # Step 2: Analyze trend
        self.add_step(ChainStep(
            name="analyze_trend",
            prompt_template="""
            Based on the extracted data, analyze the trend:
            {extracted_data}

            Determine:
            1. Primary trend direction (bullish/bearish/neutral)
            2. Trend strength (strong/moderate/weak)
            3. Key levels to watch
            """,
            output_key="trend_analysis",
            required_inputs=["extracted_data"]
        ))

        # Step 3: Generate signal
        self.add_step(ChainStep(
            name="generate_signal",
            prompt_template="""
            Based on the trend analysis, generate a trading signal:
            {trend_analysis}

            Provide:
            1. Direction: BUY, SELL, or NEUTRAL
            2. Confidence: 0-100%
            3. Entry price suggestion
            4. Stop loss level
            5. Take profit level
            """,
            output_key="signal",
            required_inputs=["trend_analysis"]
        ))

        # Step 4: Validate signal
        self.add_step(ChainStep(
            name="validate_signal",
            prompt_template="""
            Validate this trading signal:
            {signal}

            Check:
            1. Risk/reward ratio (should be >= 1:2)
            2. Signal alignment with trend
            3. Any conflicting indicators

            Return: VALID or INVALID with reason
            """,
            output_key="validation",
            required_inputs=["signal"]
        ))


# Convenience functions
def create_simple_chain(
    steps: List[tuple],  # List of (name, prompt_template, output_key)
) -> PromptChain:
    """Create a simple chain from tuples."""
    chain = PromptChain("simple_chain")
    for i, (name, template, output_key) in enumerate(steps):
        required = [steps[i-1][2]] if i > 0 else []
        chain.add_step(ChainStep(
            name=name,
            prompt_template=template,
            output_key=output_key,
            required_inputs=required
        ))
    return chain


# Example usage
if __name__ == "__main__":
    # Simple example
    chain = create_simple_chain([
        ("summarize", "Summarize this text: {input_text}", "summary"),
        ("extract_topics", "Extract topics from: {summary}", "topics"),
        ("generate_tags", "Generate tags from: {topics}", "tags"),
    ])

    # Mock LLM client for testing
    class MockLLM:
        def generate(self, prompt):
            return f"Mock response for: {prompt[:50]}..."

    result = chain.execute(
        {"input_text": "This is a sample text about AI and machine learning."},
        MockLLM()
    )

    print(f"Success: {result.success}")
    print(f"Steps: {result.steps_completed}/{result.total_steps}")
    print(f"Outputs: {result.outputs}")
