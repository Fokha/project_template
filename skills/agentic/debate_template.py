"""
Debate Pattern Template
=======================
Multiple perspectives debate to reach better conclusions.

Use when:
- Complex decisions need analysis
- Multiple valid viewpoints exist
- Adversarial analysis helpful

Placeholders:
- {{MAX_ROUNDS}}: Maximum debate rounds
- {{MODERATOR_ENABLED}}: Whether to use moderator
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Stance(Enum):
    FOR = "for"
    AGAINST = "against"
    NEUTRAL = "neutral"


@dataclass
class Argument:
    """A single argument in the debate."""
    debater: str
    stance: Stance
    content: str
    evidence: List[str] = field(default_factory=list)
    rebuts: Optional[str] = None  # ID of argument this rebuts
    strength: float = 0.5  # 0-1


@dataclass
class DebateRound:
    """A round of debate."""
    round_number: int
    arguments: List[Argument]
    summary: Optional[str] = None


@dataclass
class DebateResult:
    """Final debate result."""
    topic: str
    rounds: List[DebateRound]
    winner: Optional[Stance]
    final_score: Dict[str, float]  # stance -> score
    synthesis: str
    confidence: float


class Debater:
    """A participant in the debate."""

    def __init__(
        self,
        name: str,
        stance: Stance,
        llm_client: Any,
        style: str = "analytical"
    ):
        self.name = name
        self.stance = stance
        self.llm = llm_client
        self.style = style
        self.arguments_made: List[Argument] = []

    def make_argument(
        self,
        topic: str,
        context: Dict[str, Any],
        opponent_arguments: List[Argument]
    ) -> Argument:
        """Generate an argument."""
        prompt = self._build_prompt(topic, context, opponent_arguments)
        response = self.llm.generate(prompt)

        argument = Argument(
            debater=self.name,
            stance=self.stance,
            content=response,
            evidence=self._extract_evidence(response)
        )

        # If rebutting, note which argument
        if opponent_arguments:
            argument.rebuts = f"{opponent_arguments[-1].debater}"

        self.arguments_made.append(argument)
        return argument

    def _build_prompt(
        self,
        topic: str,
        context: Dict[str, Any],
        opponent_arguments: List[Argument]
    ) -> str:
        prompt = f"""You are {self.name}, arguing {self.stance.value.upper()} the position.
Your style is {self.style}.

Topic: {topic}

Context:
{self._format_context(context)}
"""

        if opponent_arguments:
            prompt += f"""
Opponent's recent arguments:
{chr(10).join(f'- {a.debater}: {a.content[:200]}...' for a in opponent_arguments[-2:])}

Respond to their arguments while advancing your position.
"""
        else:
            prompt += """
Make your opening argument with clear reasoning and evidence.
"""

        prompt += """
Provide a concise, well-structured argument (2-3 paragraphs).
Include specific evidence or data points to support your position."""

        return prompt

    def _format_context(self, context: Dict[str, Any]) -> str:
        return "\n".join(f"- {k}: {v}" for k, v in context.items())

    def _extract_evidence(self, response: str) -> List[str]:
        """Extract evidence points from response."""
        # Simple extraction - could be enhanced
        evidence = []
        for line in response.split("\n"):
            if any(marker in line.lower() for marker in ["data:", "evidence:", "fact:", "statistic:"]):
                evidence.append(line.strip())
        return evidence


class Moderator:
    """Moderates the debate and synthesizes conclusion."""

    def __init__(self, llm_client: Any):
        self.llm = llm_client

    def summarize_round(self, round: DebateRound) -> str:
        """Summarize a debate round."""
        arguments_text = "\n\n".join([
            f"**{arg.debater} ({arg.stance.value}):**\n{arg.content}"
            for arg in round.arguments
        ])

        prompt = f"""Summarize this debate round objectively:

{arguments_text}

Provide a brief (2-3 sentence) summary of the key points made."""

        return self.llm.generate(prompt)

    def synthesize(self, rounds: List[DebateRound], topic: str) -> Tuple[str, Dict[str, float]]:
        """Synthesize final conclusion."""
        all_arguments = []
        for round in rounds:
            all_arguments.extend(round.arguments)

        prompt = f"""As a neutral moderator, synthesize the debate on: {topic}

Arguments made:
"""
        for arg in all_arguments:
            prompt += f"\n{arg.debater} ({arg.stance.value}): {arg.content[:300]}...\n"

        prompt += """
Provide:
1. A balanced synthesis combining the strongest points from each side
2. Score each position (for, against, neutral) from 0-1 based on argument strength
3. A final recommendation

Format as:
SYNTHESIS: [your synthesis]
SCORES: for=X.X, against=X.X, neutral=X.X
RECOMMENDATION: [your recommendation]"""

        response = self.llm.generate(prompt)

        # Parse response
        synthesis = response
        scores = {"for": 0.5, "against": 0.5, "neutral": 0.5}

        if "SCORES:" in response:
            try:
                scores_part = response.split("SCORES:")[1].split("\n")[0]
                for part in scores_part.split(","):
                    key, val = part.strip().split("=")
                    scores[key.strip()] = float(val.strip())
            except:
                pass

        if "SYNTHESIS:" in response:
            synthesis = response.split("SYNTHESIS:")[1].split("SCORES:")[0].strip()

        return synthesis, scores


class Debate:
    """
    Conduct a structured debate.

    Example:
        debate = Debate(topic="Should we enter a BUY position on XAUUSD?")
        debate.add_debater(Debater("Bull", Stance.FOR, llm))
        debate.add_debater(Debater("Bear", Stance.AGAINST, llm))
        result = debate.run(context={"price": 2000, "trend": "bullish"})
    """

    def __init__(
        self,
        topic: str,
        llm_client: Any,
        max_rounds: int = 3,
        use_moderator: bool = True
    ):
        self.topic = topic
        self.llm = llm_client
        self.max_rounds = max_rounds
        self.debaters: List[Debater] = []
        self.moderator = Moderator(llm_client) if use_moderator else None
        self.rounds: List[DebateRound] = []

    def add_debater(self, debater: Debater) -> "Debate":
        """Add a debater."""
        self.debaters.append(debater)
        return self

    def run(self, context: Dict[str, Any]) -> DebateResult:
        """Run the debate."""
        self.rounds = []

        for round_num in range(self.max_rounds):
            round_args = []

            for debater in self.debaters:
                # Get opponent arguments
                opponent_args = [
                    a for a in round_args
                    if a.debater != debater.name
                ]

                # Add arguments from previous rounds
                for prev_round in self.rounds:
                    for arg in prev_round.arguments:
                        if arg.debater != debater.name:
                            opponent_args.append(arg)

                argument = debater.make_argument(self.topic, context, opponent_args)
                round_args.append(argument)

            round = DebateRound(
                round_number=round_num + 1,
                arguments=round_args
            )

            if self.moderator:
                round.summary = self.moderator.summarize_round(round)

            self.rounds.append(round)

        # Synthesize result
        if self.moderator:
            synthesis, scores = self.moderator.synthesize(self.rounds, self.topic)
        else:
            synthesis = "No moderator synthesis"
            scores = {"for": 0.5, "against": 0.5}

        # Determine winner
        winner = max(scores.keys(), key=lambda k: scores[k])
        winner_stance = Stance(winner) if winner in [s.value for s in Stance] else None

        return DebateResult(
            topic=self.topic,
            rounds=self.rounds,
            winner=winner_stance,
            final_score=scores,
            synthesis=synthesis,
            confidence=max(scores.values())
        )


class TradingDebate:
    """Pre-built debate for trading decisions."""

    def __init__(self, llm_client: Any):
        self.llm = llm_client

    def debate_entry(
        self,
        symbol: str,
        market_data: Dict[str, Any]
    ) -> DebateResult:
        """Debate whether to enter a trade."""
        topic = f"Should we enter a position on {symbol}?"

        debate = Debate(topic, self.llm, max_rounds=2)

        # Bull debater
        debate.add_debater(Debater(
            name="Bull Analyst",
            stance=Stance.FOR,
            llm_client=self.llm,
            style="optimistic, focuses on upside potential"
        ))

        # Bear debater
        debate.add_debater(Debater(
            name="Bear Analyst",
            stance=Stance.AGAINST,
            llm_client=self.llm,
            style="cautious, focuses on risks"
        ))

        return debate.run(context={
            "symbol": symbol,
            **market_data
        })


# Example usage
if __name__ == "__main__":
    # Mock LLM
    class MockLLM:
        def generate(self, prompt):
            if "FOR" in prompt:
                return "I believe we should BUY because the trend is strong. Data: Price above 200 EMA."
            elif "AGAINST" in prompt:
                return "I advise caution. Risk factors include high volatility. Fact: VIX at elevated levels."
            else:
                return "SYNTHESIS: Both sides made valid points.\nSCORES: for=0.6, against=0.4\nRECOMMENDATION: Cautious BUY"

    debate = Debate(
        topic="Should we buy XAUUSD?",
        llm_client=MockLLM(),
        max_rounds=2
    )

    debate.add_debater(Debater("Bull", Stance.FOR, MockLLM()))
    debate.add_debater(Debater("Bear", Stance.AGAINST, MockLLM()))

    result = debate.run({"price": 2000, "trend": "bullish"})

    print(f"Topic: {result.topic}")
    print(f"Winner: {result.winner}")
    print(f"Scores: {result.final_score}")
    print(f"Synthesis: {result.synthesis[:200]}...")
