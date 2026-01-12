# ═══════════════════════════════════════════════════════════════
# REACT PLANNING PATTERN
# Reasoning + Acting for multi-step problem solving
# ═══════════════════════════════════════════════════════════════
#
# The ReAct pattern alternates between:
# - Thought: Analyze what you know and need
# - Action: Execute an API call or tool
# - Observation: Record what you learned
# - Repeat until: Final Answer is reached
#
# ═══════════════════════════════════════════════════════════════

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════


class StepType(Enum):
    THOUGHT = "thought"
    ACTION = "action"
    OBSERVATION = "observation"
    FINAL = "final_answer"


@dataclass
class ReActStep:
    """Single step in ReAct chain."""
    step_type: StepType
    content: str
    metadata: Optional[Dict] = None


@dataclass
class ReActResult:
    """Result of ReAct execution."""
    success: bool
    final_answer: str
    confidence: float
    steps: List[ReActStep]
    total_actions: int
    error: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# REACT EXECUTOR
# ═══════════════════════════════════════════════════════════════


class ReActExecutor:
    """
    Execute ReAct (Reasoning + Acting) pattern.

    Usage:
    ```python
    executor = ReActExecutor(
        tools={
            'get_price': get_price_function,
            'analyze': analyze_function,
        },
        max_steps=10
    )

    result = executor.execute(
        goal="Analyze XAUUSD and provide trading recommendation",
        context={"user_risk": "moderate"}
    )
    ```
    """

    def __init__(
        self,
        tools: Dict[str, Callable],
        max_steps: int = 10,
        min_confidence: float = 0.6
    ):
        self.tools = tools
        self.max_steps = max_steps
        self.min_confidence = min_confidence
        self.steps: List[ReActStep] = []

    def execute(
        self,
        goal: str,
        context: Optional[Dict] = None
    ) -> ReActResult:
        """
        Execute ReAct loop until goal is achieved.

        Args:
            goal: The objective to achieve
            context: Optional context dictionary

        Returns:
            ReActResult with final answer and all steps
        """
        self.steps = []
        context = context or {}

        try:
            # Initial thought
            self._think(f"Goal: {goal}. Let me analyze what I need.")

            action_count = 0
            for step in range(self.max_steps):
                # Determine next action
                next_action = self._determine_next_action(goal, context)

                if next_action['type'] == 'final':
                    # Ready to give final answer
                    return self._finalize(
                        next_action['answer'],
                        next_action.get('confidence', 0.8),
                        action_count
                    )

                # Execute action
                if next_action['type'] == 'action':
                    action_count += 1
                    result = self._execute_action(
                        next_action['tool'],
                        next_action.get('params', {})
                    )

                    # Record observation
                    self._observe(f"Result: {result}")

                    # Think about result
                    self._think(f"Based on this result, I can now...")

            # Max steps reached
            return ReActResult(
                success=False,
                final_answer="Could not reach conclusion within max steps",
                confidence=0.0,
                steps=self.steps,
                total_actions=action_count,
                error="Max steps exceeded"
            )

        except Exception as e:
            logger.error(f"ReAct execution error: {e}")
            return ReActResult(
                success=False,
                final_answer="",
                confidence=0.0,
                steps=self.steps,
                total_actions=0,
                error=str(e)
            )

    # ═══════════════════════════════════════════════════════════
    # STEP METHODS
    # ═══════════════════════════════════════════════════════════

    def _think(self, thought: str) -> None:
        """Record a thought step."""
        self.steps.append(ReActStep(
            step_type=StepType.THOUGHT,
            content=thought
        ))
        logger.debug(f"Thought: {thought}")

    def _act(self, action: str, tool: str, params: Dict) -> None:
        """Record an action step."""
        self.steps.append(ReActStep(
            step_type=StepType.ACTION,
            content=action,
            metadata={'tool': tool, 'params': params}
        ))
        logger.debug(f"Action: {action}")

    def _observe(self, observation: str) -> None:
        """Record an observation step."""
        self.steps.append(ReActStep(
            step_type=StepType.OBSERVATION,
            content=observation
        ))
        logger.debug(f"Observation: {observation}")

    # ═══════════════════════════════════════════════════════════
    # EXECUTION METHODS
    # ═══════════════════════════════════════════════════════════

    def _determine_next_action(
        self,
        goal: str,
        context: Dict
    ) -> Dict[str, Any]:
        """
        Determine the next action to take.

        Override this method with your LLM call or logic.

        Returns:
            {
                'type': 'action' | 'final',
                'tool': 'tool_name',  # if action
                'params': {...},       # if action
                'answer': 'text',      # if final
                'confidence': 0.8      # if final
            }
        """
        # TODO: Replace with your LLM call or logic
        #
        # Example prompt for LLM:
        # """
        # Goal: {goal}
        # Context: {context}
        # Steps taken: {self.steps}
        #
        # Available tools: {list(self.tools.keys())}
        #
        # What should I do next?
        # If more information needed, specify: ACTION: tool_name(params)
        # If ready to answer, specify: FINAL: answer with confidence
        # """

        # Placeholder - implement your logic
        return {
            'type': 'final',
            'answer': 'Implement your decision logic here',
            'confidence': 0.5
        }

    def _execute_action(self, tool_name: str, params: Dict) -> Any:
        """Execute a tool action."""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        self._act(
            f"Calling {tool_name} with {params}",
            tool_name,
            params
        )

        try:
            result = self.tools[tool_name](**params)
            return result
        except Exception as e:
            logger.error(f"Tool {tool_name} failed: {e}")
            return {'error': str(e)}

    def _finalize(
        self,
        answer: str,
        confidence: float,
        action_count: int
    ) -> ReActResult:
        """Create final result."""
        self.steps.append(ReActStep(
            step_type=StepType.FINAL,
            content=answer,
            metadata={'confidence': confidence}
        ))

        return ReActResult(
            success=confidence >= self.min_confidence,
            final_answer=answer,
            confidence=confidence,
            steps=self.steps,
            total_actions=action_count
        )

    # ═══════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════════

    def get_step_summary(self) -> str:
        """Get human-readable summary of steps."""
        lines = []
        for i, step in enumerate(self.steps, 1):
            prefix = {
                StepType.THOUGHT: "💭 Thought",
                StepType.ACTION: "⚡ Action",
                StepType.OBSERVATION: "👁️ Observation",
                StepType.FINAL: "✅ Final Answer"
            }.get(step.step_type, "")

            lines.append(f"{i}. {prefix}: {step.content[:100]}...")

        return "\n".join(lines)

    def to_dict(self) -> Dict:
        """Convert execution to dictionary."""
        return {
            'steps': [
                {
                    'type': s.step_type.value,
                    'content': s.content,
                    'metadata': s.metadata
                }
                for s in self.steps
            ],
            'total_steps': len(self.steps)
        }


# ═══════════════════════════════════════════════════════════════
# TRADING-SPECIFIC REACT EXECUTOR
# ═══════════════════════════════════════════════════════════════


class TradingReActExecutor(ReActExecutor):
    """
    ReAct executor specialized for trading analysis.

    Example:
    ```python
    executor = TradingReActExecutor(
        api_base_url="http://localhost:5050"
    )

    result = executor.analyze_symbol("XAUUSD")
    ```
    """

    def __init__(self, api_base_url: str, **kwargs):
        import requests
        self.api = api_base_url
        self.session = requests.Session()

        # Define trading tools
        tools = {
            'get_signal': self._get_signal,
            'get_sentiment': self._get_sentiment,
            'check_blackout': self._check_blackout,
            'get_strength': self._get_strength,
            'get_price': self._get_price,
        }

        super().__init__(tools=tools, **kwargs)

    def _get_signal(self, symbol: str) -> Dict:
        """Get ML signal for symbol."""
        resp = self.session.post(
            f"{self.api}/predict/signal",
            json={"symbol": symbol}
        )
        return resp.json()

    def _get_sentiment(self, symbol: str) -> Dict:
        """Get market sentiment."""
        resp = self.session.get(f"{self.api}/sentiment/{symbol}")
        return resp.json()

    def _check_blackout(self, symbol: str) -> Dict:
        """Check for news blackout."""
        resp = self.session.get(f"{self.api}/market/blackout/{symbol}")
        return resp.json()

    def _get_strength(self) -> Dict:
        """Get currency strength."""
        resp = self.session.get(f"{self.api}/currency/strength")
        return resp.json()

    def _get_price(self, symbol: str) -> Dict:
        """Get current price."""
        resp = self.session.get(f"{self.api}/realtime/price/{symbol}")
        return resp.json()

    def analyze_symbol(self, symbol: str) -> ReActResult:
        """
        Full ReAct analysis of a trading symbol.
        """
        return self.execute(
            goal=f"Analyze {symbol} and provide trading recommendation",
            context={"symbol": symbol}
        )


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Example tools
    def get_price(symbol: str) -> Dict:
        return {"symbol": symbol, "price": 2650.50, "change": 0.5}

    def analyze_trend(symbol: str) -> Dict:
        return {"symbol": symbol, "trend": "bullish", "strength": 0.75}

    # Create executor
    executor = ReActExecutor(
        tools={
            'get_price': get_price,
            'analyze_trend': analyze_trend,
        },
        max_steps=5
    )

    # Execute
    result = executor.execute(
        goal="Determine if XAUUSD is a good buy opportunity",
        context={"risk_level": "moderate"}
    )

    print(f"Success: {result.success}")
    print(f"Answer: {result.final_answer}")
    print(f"Confidence: {result.confidence}")
    print(f"Steps: {len(result.steps)}")
    print(f"Actions: {result.total_actions}")
