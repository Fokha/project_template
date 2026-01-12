"""
Human-in-the-Loop Pattern Template
==================================
Incorporate human approval and feedback in AI workflows.

Use when:
- High-stakes decisions need human oversight
- Confidence is below threshold
- Regulatory compliance requires human approval
- Learning from human corrections

Placeholders:
- {{APPROVAL_TIMEOUT}}: Seconds to wait for human response
- {{AUTO_APPROVE_THRESHOLD}}: Confidence level for auto-approval
"""

from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import logging
from datetime import datetime, timedelta
import threading
import queue
import uuid

logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    TIMEOUT = "timeout"
    AUTO_APPROVED = "auto_approved"


@dataclass
class ApprovalRequest:
    """Request for human approval."""
    id: str
    action: Dict[str, Any]
    context: Dict[str, Any]
    reason: str
    confidence: float
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    human_feedback: Optional[str] = None
    modified_action: Optional[Dict[str, Any]] = None


@dataclass
class HumanFeedback:
    """Feedback from human reviewer."""
    request_id: str
    approved: bool
    feedback: Optional[str] = None
    modifications: Optional[Dict[str, Any]] = None
    reviewer: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class ApprovalChannel(ABC):
    """Abstract channel for human communication."""

    @abstractmethod
    def send_request(self, request: ApprovalRequest) -> bool:
        """Send approval request to human."""
        pass

    @abstractmethod
    def get_response(self, request_id: str, timeout: float) -> Optional[HumanFeedback]:
        """Get human response."""
        pass


class ConsoleApprovalChannel(ApprovalChannel):
    """Console-based approval for testing."""

    def send_request(self, request: ApprovalRequest) -> bool:
        print(f"\n{'='*50}")
        print(f"APPROVAL REQUEST: {request.id}")
        print(f"{'='*50}")
        print(f"Action: {request.action}")
        print(f"Context: {request.context}")
        print(f"Reason: {request.reason}")
        print(f"Confidence: {request.confidence:.0%}")
        print(f"{'='*50}")
        return True

    def get_response(self, request_id: str, timeout: float) -> Optional[HumanFeedback]:
        try:
            response = input(f"Approve? (y/n/m for modify): ").strip().lower()
            if response == 'y':
                return HumanFeedback(request_id=request_id, approved=True)
            elif response == 'n':
                feedback = input("Reason for rejection: ")
                return HumanFeedback(request_id=request_id, approved=False, feedback=feedback)
            elif response == 'm':
                # In real impl, would gather modifications
                return HumanFeedback(
                    request_id=request_id,
                    approved=True,
                    modifications={"modified": True}
                )
        except Exception:
            pass
        return None


class QueueApprovalChannel(ApprovalChannel):
    """Queue-based approval for async workflows."""

    def __init__(self):
        self.pending: Dict[str, ApprovalRequest] = {}
        self.responses: Dict[str, HumanFeedback] = {}
        self._lock = threading.Lock()

    def send_request(self, request: ApprovalRequest) -> bool:
        with self._lock:
            self.pending[request.id] = request
        return True

    def get_response(self, request_id: str, timeout: float) -> Optional[HumanFeedback]:
        start = datetime.now()
        while (datetime.now() - start).total_seconds() < timeout:
            with self._lock:
                if request_id in self.responses:
                    return self.responses.pop(request_id)
            threading.Event().wait(0.1)
        return None

    def submit_response(self, feedback: HumanFeedback):
        """Submit human response (called by UI/webhook)."""
        with self._lock:
            self.responses[feedback.request_id] = feedback
            if feedback.request_id in self.pending:
                del self.pending[feedback.request_id]

    def get_pending(self) -> List[ApprovalRequest]:
        """Get all pending requests."""
        with self._lock:
            return list(self.pending.values())


class HumanInTheLoop:
    """
    Human-in-the-loop workflow manager.

    Example:
        hitl = HumanInTheLoop(
            channel=QueueApprovalChannel(),
            auto_approve_threshold=0.9
        )

        result = hitl.request_approval(
            action={"type": "trade", "symbol": "XAUUSD"},
            context={"confidence": 0.75},
            reason="High value trade"
        )
    """

    def __init__(
        self,
        channel: ApprovalChannel,
        auto_approve_threshold: float = 0.95,
        default_timeout: float = 300,  # 5 minutes
        on_approval: Optional[Callable[[ApprovalRequest], None]] = None,
        on_rejection: Optional[Callable[[ApprovalRequest, str], None]] = None
    ):
        self.channel = channel
        self.auto_approve_threshold = auto_approve_threshold
        self.default_timeout = default_timeout
        self.on_approval = on_approval
        self.on_rejection = on_rejection
        self.history: List[ApprovalRequest] = []

    def request_approval(
        self,
        action: Dict[str, Any],
        context: Dict[str, Any],
        reason: str,
        confidence: float = 0.5,
        timeout: Optional[float] = None
    ) -> ApprovalRequest:
        """Request human approval for an action."""
        timeout = timeout or self.default_timeout

        request = ApprovalRequest(
            id=str(uuid.uuid4()),
            action=action,
            context=context,
            reason=reason,
            confidence=confidence,
            expires_at=datetime.now() + timedelta(seconds=timeout)
        )

        # Auto-approve if confidence is high enough
        if confidence >= self.auto_approve_threshold:
            request.status = ApprovalStatus.AUTO_APPROVED
            logger.info(f"Auto-approved request {request.id} (confidence: {confidence:.0%})")
            self.history.append(request)
            return request

        # Send to human
        self.channel.send_request(request)

        # Wait for response
        response = self.channel.get_response(request.id, timeout)

        if response is None:
            request.status = ApprovalStatus.TIMEOUT
            logger.warning(f"Request {request.id} timed out")
        elif response.approved:
            if response.modifications:
                request.status = ApprovalStatus.MODIFIED
                request.modified_action = response.modifications
            else:
                request.status = ApprovalStatus.APPROVED
            request.human_feedback = response.feedback

            if self.on_approval:
                self.on_approval(request)
        else:
            request.status = ApprovalStatus.REJECTED
            request.human_feedback = response.feedback

            if self.on_rejection:
                self.on_rejection(request, response.feedback or "")

        self.history.append(request)
        return request

    def is_approved(self, request: ApprovalRequest) -> bool:
        """Check if request was approved."""
        return request.status in [
            ApprovalStatus.APPROVED,
            ApprovalStatus.MODIFIED,
            ApprovalStatus.AUTO_APPROVED
        ]

    def get_final_action(self, request: ApprovalRequest) -> Dict[str, Any]:
        """Get the final action (possibly modified)."""
        if request.status == ApprovalStatus.MODIFIED and request.modified_action:
            return {**request.action, **request.modified_action}
        return request.action


class EscalationPolicy:
    """Define escalation rules for approval."""

    def __init__(self):
        self.rules: List[Dict[str, Any]] = []

    def add_rule(
        self,
        condition: Callable[[Dict[str, Any]], bool],
        escalate_to: str,
        priority: int = 0
    ) -> "EscalationPolicy":
        """Add escalation rule."""
        self.rules.append({
            "condition": condition,
            "escalate_to": escalate_to,
            "priority": priority
        })
        self.rules.sort(key=lambda r: r["priority"], reverse=True)
        return self

    def get_escalation(self, context: Dict[str, Any]) -> Optional[str]:
        """Get escalation target for context."""
        for rule in self.rules:
            if rule["condition"](context):
                return rule["escalate_to"]
        return None


class TradingHITL(HumanInTheLoop):
    """Human-in-the-loop specialized for trading."""

    def __init__(
        self,
        channel: ApprovalChannel,
        max_auto_approve_size: float = 0.01,  # lot size
        max_auto_approve_risk: float = 100,   # dollars
    ):
        super().__init__(channel, auto_approve_threshold=0.95)
        self.max_auto_approve_size = max_auto_approve_size
        self.max_auto_approve_risk = max_auto_approve_risk

        # Escalation policy
        self.escalation = EscalationPolicy()
        self.escalation.add_rule(
            condition=lambda c: c.get("risk_amount", 0) > 500,
            escalate_to="senior_trader",
            priority=10
        )
        self.escalation.add_rule(
            condition=lambda c: c.get("symbol") in ["XAUUSD", "BTCUSD"],
            escalate_to="specialist",
            priority=5
        )

    def request_trade_approval(
        self,
        symbol: str,
        direction: str,
        lot_size: float,
        confidence: float,
        risk_amount: float,
        analysis: Dict[str, Any]
    ) -> ApprovalRequest:
        """Request approval for a trade."""
        action = {
            "type": "trade",
            "symbol": symbol,
            "direction": direction,
            "lot_size": lot_size
        }

        context = {
            "confidence": confidence,
            "risk_amount": risk_amount,
            "analysis": analysis
        }

        # Check if can auto-approve
        can_auto_approve = (
            confidence >= self.auto_approve_threshold and
            lot_size <= self.max_auto_approve_size and
            risk_amount <= self.max_auto_approve_risk
        )

        # Determine reason
        reasons = []
        if lot_size > self.max_auto_approve_size:
            reasons.append(f"Large position size ({lot_size} lots)")
        if risk_amount > self.max_auto_approve_risk:
            reasons.append(f"High risk amount (${risk_amount})")
        if confidence < 0.8:
            reasons.append(f"Low confidence ({confidence:.0%})")

        reason = "; ".join(reasons) if reasons else "Standard approval"

        # Check escalation
        escalate_to = self.escalation.get_escalation(context)
        if escalate_to:
            reason += f" [Escalate to: {escalate_to}]"

        return self.request_approval(
            action=action,
            context=context,
            reason=reason,
            confidence=confidence if can_auto_approve else 0  # Force human review
        )


class FeedbackCollector:
    """Collect and learn from human feedback."""

    def __init__(self):
        self.feedback_history: List[Dict[str, Any]] = []

    def record_feedback(
        self,
        request: ApprovalRequest,
        outcome: Optional[Dict[str, Any]] = None
    ):
        """Record feedback for learning."""
        self.feedback_history.append({
            "request_id": request.id,
            "action": request.action,
            "context": request.context,
            "confidence": request.confidence,
            "status": request.status.value,
            "human_feedback": request.human_feedback,
            "modifications": request.modified_action,
            "outcome": outcome,
            "timestamp": datetime.now().isoformat()
        })

    def get_rejection_patterns(self) -> List[Dict[str, Any]]:
        """Analyze patterns in rejections."""
        rejections = [f for f in self.feedback_history if f["status"] == "rejected"]
        patterns = {}

        for r in rejections:
            # Group by action type
            action_type = r["action"].get("type", "unknown")
            if action_type not in patterns:
                patterns[action_type] = {"count": 0, "reasons": []}
            patterns[action_type]["count"] += 1
            if r["human_feedback"]:
                patterns[action_type]["reasons"].append(r["human_feedback"])

        return [{"type": k, **v} for k, v in patterns.items()]

    def get_modification_patterns(self) -> List[Dict[str, Any]]:
        """Analyze patterns in modifications."""
        modifications = [f for f in self.feedback_history if f["status"] == "modified"]
        # Analyze what gets modified
        return modifications


# Example usage
if __name__ == "__main__":
    # Create channel and HITL
    channel = ConsoleApprovalChannel()
    hitl = TradingHITL(channel)

    # Simulate trade approval
    print("Testing Human-in-the-Loop for Trading\n")

    # Test 1: Low confidence trade (needs approval)
    result = hitl.request_trade_approval(
        symbol="XAUUSD",
        direction="BUY",
        lot_size=0.05,
        confidence=0.65,
        risk_amount=150,
        analysis={"trend": "bullish", "support": 1980}
    )

    print(f"\nResult: {result.status.value}")
    if hitl.is_approved(result):
        final_action = hitl.get_final_action(result)
        print(f"Executing: {final_action}")
    else:
        print(f"Trade not executed. Reason: {result.human_feedback or result.status.value}")
