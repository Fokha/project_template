# ═══════════════════════════════════════════════════════════════
# CONSENSUS PATTERN TEMPLATE
# Multi-agent voting for reliable decisions
# ═══════════════════════════════════════════════════════════════
#
# Pattern: Multiple agents vote on a decision
# Use Case: High-stakes decisions, trading signals, content moderation
#
# ═══════════════════════════════════════════════════════════════

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════


class VoteType(Enum):
    """Types of votes an agent can cast."""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"


class ConsensusMethod(Enum):
    """Methods for reaching consensus."""
    MAJORITY = "majority"         # >50% approve
    SUPERMAJORITY = "supermajority"  # >66% approve
    UNANIMOUS = "unanimous"       # 100% approve
    WEIGHTED = "weighted"         # By agent expertise


@dataclass
class AgentVote:
    """Single agent's vote."""
    agent_id: str
    vote: VoteType
    confidence: float           # 0-1
    reasoning: str
    weight: float = 1.0        # For weighted voting


@dataclass
class ConsensusResult:
    """Result of consensus process."""
    decision: VoteType
    confidence: float
    votes: List[AgentVote]
    approve_count: int
    reject_count: int
    abstain_count: int
    method: ConsensusMethod
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_approved(self) -> bool:
        return self.decision == VoteType.APPROVE


# ═══════════════════════════════════════════════════════════════
# AGENT INTERFACE
# ═══════════════════════════════════════════════════════════════


class ConsensusAgent:
    """
    Base class for consensus-participating agents.

    Override the vote() method with your logic.
    """

    def __init__(self, agent_id: str, expertise: float = 1.0):
        self.agent_id = agent_id
        self.expertise = expertise  # Weight in weighted voting

    def vote(self, context: Dict[str, Any]) -> AgentVote:
        """
        Cast a vote on the given context.

        Override this method in subclasses.
        """
        raise NotImplementedError("Subclass must implement vote()")


# ═══════════════════════════════════════════════════════════════
# CONSENSUS ENGINE
# ═══════════════════════════════════════════════════════════════


class ConsensusEngine:
    """
    Orchestrates multi-agent voting for consensus.

    Usage:
        engine = ConsensusEngine(method=ConsensusMethod.MAJORITY)
        engine.add_agent(TechnicalAnalystAgent("tech_1"))
        engine.add_agent(FundamentalAnalystAgent("fund_1"))
        engine.add_agent(SentimentAnalystAgent("sent_1"))

        result = engine.reach_consensus({"symbol": "XAUUSD", "signal": "BUY"})
        if result.is_approved:
            execute_trade()
    """

    def __init__(
        self,
        method: ConsensusMethod = ConsensusMethod.MAJORITY,
        min_confidence: float = 0.6,
        timeout_seconds: int = 30
    ):
        self.method = method
        self.min_confidence = min_confidence
        self.timeout_seconds = timeout_seconds
        self.agents: List[ConsensusAgent] = []

    def add_agent(self, agent: ConsensusAgent):
        """Add an agent to the consensus group."""
        self.agents.append(agent)
        logger.info(f"Added agent: {agent.agent_id} (expertise: {agent.expertise})")

    def remove_agent(self, agent_id: str):
        """Remove an agent from the consensus group."""
        self.agents = [a for a in self.agents if a.agent_id != agent_id]

    def reach_consensus(self, context: Dict[str, Any]) -> ConsensusResult:
        """
        Run the consensus process.

        Args:
            context: Information for agents to vote on

        Returns:
            ConsensusResult with final decision
        """
        if not self.agents:
            raise ValueError("No agents registered for consensus")

        logger.info(f"Starting consensus with {len(self.agents)} agents")

        # Collect votes
        votes = []
        for agent in self.agents:
            try:
                vote = agent.vote(context)
                vote.weight = agent.expertise
                votes.append(vote)
                logger.info(f"  {agent.agent_id}: {vote.vote.value} ({vote.confidence:.2f})")
            except Exception as e:
                logger.error(f"Agent {agent.agent_id} failed to vote: {e}")
                # Abstain on error
                votes.append(AgentVote(
                    agent_id=agent.agent_id,
                    vote=VoteType.ABSTAIN,
                    confidence=0.0,
                    reasoning=f"Error: {str(e)}",
                    weight=agent.expertise,
                ))

        # Calculate consensus
        return self._calculate_consensus(votes)

    def _calculate_consensus(self, votes: List[AgentVote]) -> ConsensusResult:
        """Calculate final consensus from votes."""
        approve_count = sum(1 for v in votes if v.vote == VoteType.APPROVE)
        reject_count = sum(1 for v in votes if v.vote == VoteType.REJECT)
        abstain_count = sum(1 for v in votes if v.vote == VoteType.ABSTAIN)

        voting_count = approve_count + reject_count  # Exclude abstains

        if voting_count == 0:
            return ConsensusResult(
                decision=VoteType.ABSTAIN,
                confidence=0.0,
                votes=votes,
                approve_count=approve_count,
                reject_count=reject_count,
                abstain_count=abstain_count,
                method=self.method,
            )

        # Calculate based on method
        if self.method == ConsensusMethod.UNANIMOUS:
            decision, confidence = self._unanimous_vote(votes, voting_count)
        elif self.method == ConsensusMethod.SUPERMAJORITY:
            decision, confidence = self._supermajority_vote(votes, voting_count)
        elif self.method == ConsensusMethod.WEIGHTED:
            decision, confidence = self._weighted_vote(votes)
        else:  # MAJORITY
            decision, confidence = self._majority_vote(votes, voting_count)

        return ConsensusResult(
            decision=decision,
            confidence=confidence,
            votes=votes,
            approve_count=approve_count,
            reject_count=reject_count,
            abstain_count=abstain_count,
            method=self.method,
        )

    def _majority_vote(self, votes: List[AgentVote], voting_count: int) -> tuple:
        """Simple majority (>50%)."""
        approve_count = sum(1 for v in votes if v.vote == VoteType.APPROVE)
        approve_ratio = approve_count / voting_count

        if approve_ratio > 0.5:
            avg_confidence = self._avg_confidence(votes, VoteType.APPROVE)
            return VoteType.APPROVE, avg_confidence
        else:
            avg_confidence = self._avg_confidence(votes, VoteType.REJECT)
            return VoteType.REJECT, avg_confidence

    def _supermajority_vote(self, votes: List[AgentVote], voting_count: int) -> tuple:
        """Supermajority (>66%)."""
        approve_count = sum(1 for v in votes if v.vote == VoteType.APPROVE)
        approve_ratio = approve_count / voting_count

        if approve_ratio >= 0.67:
            avg_confidence = self._avg_confidence(votes, VoteType.APPROVE)
            return VoteType.APPROVE, avg_confidence
        else:
            avg_confidence = self._avg_confidence(votes, VoteType.REJECT)
            return VoteType.REJECT, avg_confidence

    def _unanimous_vote(self, votes: List[AgentVote], voting_count: int) -> tuple:
        """Unanimous approval required."""
        approve_count = sum(1 for v in votes if v.vote == VoteType.APPROVE)

        if approve_count == voting_count:
            avg_confidence = self._avg_confidence(votes, VoteType.APPROVE)
            return VoteType.APPROVE, avg_confidence
        else:
            avg_confidence = self._avg_confidence(votes, VoteType.REJECT)
            return VoteType.REJECT, avg_confidence

    def _weighted_vote(self, votes: List[AgentVote]) -> tuple:
        """Weighted vote based on agent expertise."""
        total_weight = sum(v.weight for v in votes if v.vote != VoteType.ABSTAIN)

        if total_weight == 0:
            return VoteType.ABSTAIN, 0.0

        approve_weight = sum(v.weight * v.confidence for v in votes if v.vote == VoteType.APPROVE)
        reject_weight = sum(v.weight * v.confidence for v in votes if v.vote == VoteType.REJECT)

        if approve_weight > reject_weight:
            confidence = approve_weight / total_weight
            return VoteType.APPROVE, confidence
        else:
            confidence = reject_weight / total_weight
            return VoteType.REJECT, confidence

    def _avg_confidence(self, votes: List[AgentVote], vote_type: VoteType) -> float:
        """Calculate average confidence for a vote type."""
        matching = [v.confidence for v in votes if v.vote == vote_type]
        return sum(matching) / len(matching) if matching else 0.0


# ═══════════════════════════════════════════════════════════════
# EXAMPLE: TRADING SIGNAL CONSENSUS
# ═══════════════════════════════════════════════════════════════


class TechnicalAnalystAgent(ConsensusAgent):
    """Agent that votes based on technical indicators."""

    def vote(self, context: Dict[str, Any]) -> AgentVote:
        # Simulated technical analysis
        signal = context.get("signal", "NEUTRAL")
        rsi = context.get("rsi", 50)
        trend = context.get("trend", "NEUTRAL")

        # Vote logic
        if signal == "BUY" and rsi < 70 and trend in ["UP", "NEUTRAL"]:
            return AgentVote(
                agent_id=self.agent_id,
                vote=VoteType.APPROVE,
                confidence=0.8,
                reasoning=f"Technical: RSI={rsi}, Trend={trend}, signal aligned",
            )
        elif signal == "SELL" and rsi > 30 and trend in ["DOWN", "NEUTRAL"]:
            return AgentVote(
                agent_id=self.agent_id,
                vote=VoteType.APPROVE,
                confidence=0.8,
                reasoning=f"Technical: RSI={rsi}, Trend={trend}, signal aligned",
            )
        else:
            return AgentVote(
                agent_id=self.agent_id,
                vote=VoteType.REJECT,
                confidence=0.6,
                reasoning=f"Technical: Conditions not met",
            )


class SentimentAnalystAgent(ConsensusAgent):
    """Agent that votes based on market sentiment."""

    def vote(self, context: Dict[str, Any]) -> AgentVote:
        sentiment_score = context.get("sentiment", 0.5)
        signal = context.get("signal", "NEUTRAL")

        # Sentiment alignment
        if signal == "BUY" and sentiment_score > 0.6:
            return AgentVote(
                agent_id=self.agent_id,
                vote=VoteType.APPROVE,
                confidence=sentiment_score,
                reasoning=f"Sentiment bullish ({sentiment_score:.2f})",
            )
        elif signal == "SELL" and sentiment_score < 0.4:
            return AgentVote(
                agent_id=self.agent_id,
                vote=VoteType.APPROVE,
                confidence=1 - sentiment_score,
                reasoning=f"Sentiment bearish ({sentiment_score:.2f})",
            )
        else:
            return AgentVote(
                agent_id=self.agent_id,
                vote=VoteType.ABSTAIN,
                confidence=0.5,
                reasoning=f"Sentiment neutral ({sentiment_score:.2f})",
            )


class RiskManagerAgent(ConsensusAgent):
    """Agent that votes based on risk parameters."""

    def vote(self, context: Dict[str, Any]) -> AgentVote:
        risk_level = context.get("risk_level", "MEDIUM")
        daily_loss = context.get("daily_loss_pct", 0)
        open_positions = context.get("open_positions", 0)

        # Risk checks
        if daily_loss > 3:
            return AgentVote(
                agent_id=self.agent_id,
                vote=VoteType.REJECT,
                confidence=0.95,
                reasoning=f"Daily loss too high: {daily_loss}%",
            )
        if open_positions >= 5:
            return AgentVote(
                agent_id=self.agent_id,
                vote=VoteType.REJECT,
                confidence=0.9,
                reasoning=f"Too many open positions: {open_positions}",
            )
        if risk_level == "HIGH":
            return AgentVote(
                agent_id=self.agent_id,
                vote=VoteType.APPROVE,
                confidence=0.6,
                reasoning="Risk acceptable but elevated",
            )
        else:
            return AgentVote(
                agent_id=self.agent_id,
                vote=VoteType.APPROVE,
                confidence=0.85,
                reasoning="Risk within normal parameters",
            )


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    # Create consensus engine
    engine = ConsensusEngine(
        method=ConsensusMethod.WEIGHTED,
        min_confidence=0.6,
    )

    # Add agents with different expertise weights
    engine.add_agent(TechnicalAnalystAgent("tech_1", expertise=1.5))
    engine.add_agent(SentimentAnalystAgent("sent_1", expertise=1.0))
    engine.add_agent(RiskManagerAgent("risk_1", expertise=2.0))  # Risk has highest weight

    # Trading context
    context = {
        "symbol": "XAUUSD",
        "signal": "BUY",
        "rsi": 45,
        "trend": "UP",
        "sentiment": 0.7,
        "risk_level": "MEDIUM",
        "daily_loss_pct": 1.5,
        "open_positions": 2,
    }

    # Reach consensus
    result = engine.reach_consensus(context)

    # Print results
    print("\n" + "=" * 60)
    print("CONSENSUS RESULT")
    print("=" * 60)
    print(f"Decision:   {result.decision.value.upper()}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Method:     {result.method.value}")
    print(f"\nVotes: {result.approve_count} approve, {result.reject_count} reject, {result.abstain_count} abstain")
    print("\nIndividual Votes:")
    for vote in result.votes:
        print(f"  {vote.agent_id}: {vote.vote.value} ({vote.confidence:.2f}) - {vote.reasoning}")
