"""
Hierarchical Agents Pattern Template
====================================
Supervisor delegates to specialist sub-agents.

Use when:
- Tasks need different expertise
- Complex workflows need coordination
- Clear responsibility delegation needed

Placeholders:
- {{SUPERVISOR_NAME}}: Name of supervisor agent
- {{MAX_DELEGATION_DEPTH}}: Maximum nesting level
"""

from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    SUPERVISOR = "supervisor"
    SPECIALIST = "specialist"
    WORKER = "worker"


@dataclass
class AgentCapability:
    """Capability of an agent."""
    name: str
    description: str
    expertise_level: float = 0.8  # 0-1


@dataclass
class Task:
    """Task to be executed."""
    id: str
    type: str
    description: str
    payload: Dict[str, Any]
    priority: int = 0
    parent_task_id: Optional[str] = None
    assigned_to: Optional[str] = None
    result: Optional[Any] = None
    status: str = "pending"


@dataclass
class DelegationDecision:
    """Decision about task delegation."""
    delegate: bool
    target_agent: Optional[str] = None
    reason: str = ""
    sub_tasks: List[Task] = field(default_factory=list)


class Agent(ABC):
    """Base agent class."""

    def __init__(
        self,
        agent_id: str,
        name: str,
        role: AgentRole,
        capabilities: List[AgentCapability]
    ):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.capabilities = {c.name: c for c in capabilities}
        self.subordinates: Dict[str, "Agent"] = {}
        self.supervisor: Optional["Agent"] = None

    def can_handle(self, task_type: str) -> bool:
        """Check if agent can handle task type."""
        return task_type in self.capabilities or "*" in self.capabilities

    def get_expertise(self, task_type: str) -> float:
        """Get expertise level for task type."""
        if task_type in self.capabilities:
            return self.capabilities[task_type].expertise_level
        return 0

    @abstractmethod
    def process(self, task: Task) -> Any:
        """Process a task."""
        pass

    def add_subordinate(self, agent: "Agent"):
        """Add a subordinate agent."""
        self.subordinates[agent.agent_id] = agent
        agent.supervisor = self


class SupervisorAgent(Agent):
    """Supervisor that delegates to specialists."""

    def __init__(
        self,
        agent_id: str,
        name: str,
        llm_client: Any = None
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            role=AgentRole.SUPERVISOR,
            capabilities=[AgentCapability("*", "Can supervise all tasks")]
        )
        self.llm = llm_client
        self.task_history: List[Task] = []

    def process(self, task: Task) -> Any:
        """Process task, potentially delegating."""
        logger.info(f"Supervisor {self.name} received task: {task.description}")

        # Decide whether to delegate
        decision = self._decide_delegation(task)

        if decision.delegate and decision.target_agent:
            # Delegate to subordinate
            subordinate = self.subordinates.get(decision.target_agent)
            if subordinate:
                logger.info(f"Delegating to {subordinate.name}: {decision.reason}")
                task.assigned_to = subordinate.agent_id
                result = subordinate.process(task)

                # Verify result if needed
                verified = self._verify_result(task, result)
                return verified
            else:
                logger.warning(f"Target agent {decision.target_agent} not found")

        # Handle sub-tasks if decomposed
        if decision.sub_tasks:
            results = []
            for sub_task in decision.sub_tasks:
                sub_result = self.process(sub_task)
                results.append(sub_result)
            return self._combine_results(results)

        # Handle directly
        return self._handle_directly(task)

    def _decide_delegation(self, task: Task) -> DelegationDecision:
        """Decide whether to delegate and to whom."""
        # Find best subordinate
        best_agent = None
        best_expertise = 0

        for agent_id, agent in self.subordinates.items():
            if agent.can_handle(task.type):
                expertise = agent.get_expertise(task.type)
                if expertise > best_expertise:
                    best_expertise = expertise
                    best_agent = agent_id

        if best_agent and best_expertise > 0.5:
            return DelegationDecision(
                delegate=True,
                target_agent=best_agent,
                reason=f"Best expertise ({best_expertise:.0%})"
            )

        # Check if task should be decomposed
        if self._should_decompose(task):
            sub_tasks = self._decompose_task(task)
            return DelegationDecision(
                delegate=False,
                sub_tasks=sub_tasks,
                reason="Task decomposed into sub-tasks"
            )

        return DelegationDecision(
            delegate=False,
            reason="Handling directly"
        )

    def _should_decompose(self, task: Task) -> bool:
        """Check if task should be broken down."""
        # Simple heuristic - can be enhanced with LLM
        complexity_indicators = ["and", "also", "multiple", "all"]
        return any(ind in task.description.lower() for ind in complexity_indicators)

    def _decompose_task(self, task: Task) -> List[Task]:
        """Break task into sub-tasks."""
        # Simple decomposition - can be enhanced with LLM
        sub_tasks = []

        # Example: split by "and"
        parts = task.description.split(" and ")
        for i, part in enumerate(parts):
            sub_tasks.append(Task(
                id=f"{task.id}_sub_{i}",
                type=task.type,
                description=part.strip(),
                payload=task.payload,
                parent_task_id=task.id
            ))

        return sub_tasks if len(sub_tasks) > 1 else []

    def _handle_directly(self, task: Task) -> Any:
        """Handle task directly without delegation."""
        if self.llm:
            prompt = f"""As supervisor {self.name}, handle this task:
Task: {task.description}
Type: {task.type}
Data: {task.payload}

Provide a clear response."""
            return self.llm.generate(prompt)
        return {"status": "handled_directly", "task_id": task.id}

    def _verify_result(self, task: Task, result: Any) -> Any:
        """Verify subordinate's result."""
        # Simple verification - can be enhanced
        if result is None:
            logger.warning(f"Null result for task {task.id}")
            return {"status": "error", "message": "No result from subordinate"}
        return result

    def _combine_results(self, results: List[Any]) -> Any:
        """Combine results from sub-tasks."""
        return {"combined_results": results}


class SpecialistAgent(Agent):
    """Specialist agent with specific expertise."""

    def __init__(
        self,
        agent_id: str,
        name: str,
        specialization: str,
        handler: Callable[[Task], Any],
        expertise_level: float = 0.9
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            role=AgentRole.SPECIALIST,
            capabilities=[AgentCapability(
                specialization,
                f"Expert in {specialization}",
                expertise_level
            )]
        )
        self.specialization = specialization
        self.handler = handler

    def process(self, task: Task) -> Any:
        """Process task using specialized handler."""
        logger.info(f"Specialist {self.name} processing: {task.description}")
        try:
            return self.handler(task)
        except Exception as e:
            logger.error(f"Specialist {self.name} failed: {e}")
            # Escalate to supervisor
            if self.supervisor:
                return self.supervisor._handle_directly(task)
            raise


class AgentHierarchy:
    """
    Manage a hierarchy of agents.

    Example:
        hierarchy = AgentHierarchy()

        supervisor = SupervisorAgent("sup_1", "Trading Supervisor", llm)
        hierarchy.add_agent(supervisor)

        technical = SpecialistAgent("tech_1", "Technical Analyst", "technical", tech_handler)
        hierarchy.add_agent(technical, supervisor_id="sup_1")

        result = hierarchy.execute_task(Task(...))
    """

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.root_agents: Set[str] = set()

    def add_agent(
        self,
        agent: Agent,
        supervisor_id: Optional[str] = None
    ) -> "AgentHierarchy":
        """Add an agent to the hierarchy."""
        self.agents[agent.agent_id] = agent

        if supervisor_id and supervisor_id in self.agents:
            supervisor = self.agents[supervisor_id]
            supervisor.add_subordinate(agent)
        else:
            self.root_agents.add(agent.agent_id)

        return self

    def execute_task(self, task: Task) -> Any:
        """Execute a task through the hierarchy."""
        # Find best root agent
        best_agent = None
        best_score = 0

        for agent_id in self.root_agents:
            agent = self.agents[agent_id]
            if agent.can_handle(task.type):
                score = agent.get_expertise(task.type)
                if score > best_score:
                    best_score = score
                    best_agent = agent

        if best_agent:
            return best_agent.process(task)
        else:
            raise ValueError(f"No agent can handle task type: {task.type}")

    def get_structure(self) -> Dict[str, Any]:
        """Get hierarchy structure."""
        def build_tree(agent: Agent) -> Dict:
            return {
                "id": agent.agent_id,
                "name": agent.name,
                "role": agent.role.value,
                "capabilities": list(agent.capabilities.keys()),
                "subordinates": [
                    build_tree(sub) for sub in agent.subordinates.values()
                ]
            }

        return {
            "roots": [
                build_tree(self.agents[agent_id])
                for agent_id in self.root_agents
            ]
        }


# Trading-specific hierarchy
def create_trading_hierarchy(llm_client: Any) -> AgentHierarchy:
    """Create a pre-built trading agent hierarchy."""
    hierarchy = AgentHierarchy()

    # Supervisor
    supervisor = SupervisorAgent(
        "trading_supervisor",
        "Trading Supervisor",
        llm_client
    )
    hierarchy.add_agent(supervisor)

    # Technical analyst
    def technical_handler(task: Task) -> Dict:
        return {"type": "technical", "analysis": "Bullish trend", "confidence": 0.75}

    hierarchy.add_agent(
        SpecialistAgent("technical", "Technical Analyst", "technical", technical_handler),
        supervisor_id="trading_supervisor"
    )

    # Fundamental analyst
    def fundamental_handler(task: Task) -> Dict:
        return {"type": "fundamental", "analysis": "Strong fundamentals", "confidence": 0.8}

    hierarchy.add_agent(
        SpecialistAgent("fundamental", "Fundamental Analyst", "fundamental", fundamental_handler),
        supervisor_id="trading_supervisor"
    )

    # Risk manager
    def risk_handler(task: Task) -> Dict:
        return {"type": "risk", "recommendation": "Position size: 0.02 lots", "max_loss": 100}

    hierarchy.add_agent(
        SpecialistAgent("risk", "Risk Manager", "risk", risk_handler),
        supervisor_id="trading_supervisor"
    )

    return hierarchy


# Example usage
if __name__ == "__main__":
    # Mock LLM
    class MockLLM:
        def generate(self, prompt):
            return f"Supervisor response for: {prompt[:50]}..."

    hierarchy = create_trading_hierarchy(MockLLM())

    # Print structure
    import json
    print("Hierarchy structure:")
    print(json.dumps(hierarchy.get_structure(), indent=2))

    # Execute task
    task = Task(
        id="task_1",
        type="technical",
        description="Analyze XAUUSD for entry",
        payload={"symbol": "XAUUSD"}
    )

    result = hierarchy.execute_task(task)
    print(f"\nResult: {result}")
