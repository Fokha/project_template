"""
Orchestrator-Workers Pattern Template
=====================================
Central orchestrator coordinates multiple worker agents.

Use when:
- Complex tasks need decomposition
- Different specialists needed
- Work needs coordination

Placeholders:
- {{ORCHESTRATOR_NAME}}: Name of orchestrator
- {{MAX_WORKERS}}: Maximum worker agents
"""

from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid

logger = logging.getLogger(__name__)


class WorkerStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkTask:
    """A task to be assigned to a worker."""
    id: str
    type: str
    payload: Dict[str, Any]
    priority: int = 0
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None


class Worker(ABC):
    """Abstract base class for workers."""

    def __init__(self, worker_id: str, capabilities: List[str]):
        self.worker_id = worker_id
        self.capabilities = capabilities
        self.status = WorkerStatus.IDLE
        self.current_task: Optional[str] = None

    def can_handle(self, task_type: str) -> bool:
        """Check if worker can handle task type."""
        return task_type in self.capabilities or "*" in self.capabilities

    @abstractmethod
    def execute(self, task: WorkTask) -> Any:
        """Execute a task."""
        pass


class FunctionWorker(Worker):
    """Worker that executes a function."""

    def __init__(
        self,
        worker_id: str,
        capabilities: List[str],
        handler: Callable[[WorkTask], Any]
    ):
        super().__init__(worker_id, capabilities)
        self.handler = handler

    def execute(self, task: WorkTask) -> Any:
        self.status = WorkerStatus.BUSY
        self.current_task = task.id
        try:
            result = self.handler(task)
            self.status = WorkerStatus.COMPLETED
            return result
        except Exception as e:
            self.status = WorkerStatus.FAILED
            raise
        finally:
            self.current_task = None
            self.status = WorkerStatus.IDLE


class Orchestrator:
    """
    Central coordinator for worker agents.

    Example:
        orchestrator = Orchestrator()
        orchestrator.register_worker(FunctionWorker("w1", ["analysis"], analyze_fn))
        orchestrator.register_worker(FunctionWorker("w2", ["signal"], signal_fn))

        orchestrator.add_task(WorkTask("t1", "analysis", {"symbol": "XAUUSD"}))
        orchestrator.add_task(WorkTask("t2", "signal", {"symbol": "XAUUSD"}, dependencies=["t1"]))

        result = orchestrator.execute_all()
    """

    def __init__(self, max_concurrent: int = 4):
        self.workers: Dict[str, Worker] = {}
        self.tasks: Dict[str, WorkTask] = {}
        self.max_concurrent = max_concurrent
        self.completed_tasks: Set[str] = set()

    def register_worker(self, worker: Worker) -> "Orchestrator":
        """Register a worker."""
        self.workers[worker.worker_id] = worker
        logger.info(f"Registered worker: {worker.worker_id} with capabilities: {worker.capabilities}")
        return self

    def add_task(self, task: WorkTask) -> "Orchestrator":
        """Add a task to the queue."""
        self.tasks[task.id] = task
        return self

    def add_tasks(self, tasks: List[WorkTask]) -> "Orchestrator":
        """Add multiple tasks."""
        for task in tasks:
            self.add_task(task)
        return self

    def _get_ready_tasks(self) -> List[WorkTask]:
        """Get tasks that are ready to execute (dependencies met)."""
        ready = []
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                # Check if all dependencies are completed
                deps_met = all(
                    dep in self.completed_tasks
                    for dep in task.dependencies
                )
                if deps_met:
                    ready.append(task)

        # Sort by priority (higher first)
        ready.sort(key=lambda t: t.priority, reverse=True)
        return ready

    def _find_worker(self, task: WorkTask) -> Optional[Worker]:
        """Find an available worker for a task."""
        for worker in self.workers.values():
            if worker.status == WorkerStatus.IDLE and worker.can_handle(task.type):
                return worker
        return None

    def execute_all(self, timeout: float = 60.0) -> Dict[str, Any]:
        """Execute all tasks respecting dependencies."""
        start_time = datetime.now()
        results = {}

        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            futures = {}

            while len(self.completed_tasks) < len(self.tasks):
                # Check timeout
                if (datetime.now() - start_time).total_seconds() > timeout:
                    logger.error("Orchestrator timeout")
                    break

                # Get ready tasks
                ready_tasks = self._get_ready_tasks()

                # Assign tasks to workers
                for task in ready_tasks:
                    worker = self._find_worker(task)
                    if worker:
                        task.status = TaskStatus.ASSIGNED
                        task.assigned_to = worker.worker_id
                        future = executor.submit(self._execute_task, worker, task)
                        futures[future] = task

                # Check completed futures
                for future in list(futures.keys()):
                    if future.done():
                        task = futures.pop(future)
                        try:
                            result = future.result()
                            task.result = result
                            task.status = TaskStatus.COMPLETED
                            results[task.id] = {"success": True, "result": result}
                        except Exception as e:
                            task.error = str(e)
                            task.status = TaskStatus.FAILED
                            results[task.id] = {"success": False, "error": str(e)}

                        self.completed_tasks.add(task.id)

        return {
            "total_tasks": len(self.tasks),
            "completed": len(self.completed_tasks),
            "results": results,
            "execution_time_ms": (datetime.now() - start_time).total_seconds() * 1000
        }

    def _execute_task(self, worker: Worker, task: WorkTask) -> Any:
        """Execute a task with a worker."""
        task.status = TaskStatus.IN_PROGRESS
        return worker.execute(task)


class TradingOrchestrator(Orchestrator):
    """Pre-built orchestrator for trading analysis."""

    def __init__(self, api_client: Any):
        super().__init__(max_concurrent=4)
        self.api = api_client
        self._setup_workers()

    def _setup_workers(self):
        """Setup trading workers."""
        # Technical analysis worker
        self.register_worker(FunctionWorker(
            "technical_worker",
            ["technical", "signal"],
            self._technical_handler
        ))

        # Sentiment worker
        self.register_worker(FunctionWorker(
            "sentiment_worker",
            ["sentiment"],
            self._sentiment_handler
        ))

        # Risk worker
        self.register_worker(FunctionWorker(
            "risk_worker",
            ["risk"],
            self._risk_handler
        ))

        # News worker
        self.register_worker(FunctionWorker(
            "news_worker",
            ["news"],
            self._news_handler
        ))

    def _technical_handler(self, task: WorkTask) -> Dict:
        symbol = task.payload.get("symbol")
        return {"type": "technical", "symbol": symbol, "signal": "BUY", "confidence": 75}

    def _sentiment_handler(self, task: WorkTask) -> Dict:
        symbol = task.payload.get("symbol")
        return {"type": "sentiment", "symbol": symbol, "score": 0.65, "direction": "bullish"}

    def _risk_handler(self, task: WorkTask) -> Dict:
        return {"type": "risk", "max_position": 0.02, "risk_score": "medium"}

    def _news_handler(self, task: WorkTask) -> Dict:
        symbol = task.payload.get("symbol")
        return {"type": "news", "symbol": symbol, "blackout": False, "events": []}

    def analyze_symbol(self, symbol: str) -> Dict[str, Any]:
        """Run full analysis for a symbol."""
        self.tasks.clear()
        self.completed_tasks.clear()

        # Create analysis tasks
        self.add_task(WorkTask(
            id="technical",
            type="technical",
            payload={"symbol": symbol},
            priority=10
        ))

        self.add_task(WorkTask(
            id="sentiment",
            type="sentiment",
            payload={"symbol": symbol},
            priority=8
        ))

        self.add_task(WorkTask(
            id="news",
            type="news",
            payload={"symbol": symbol},
            priority=9
        ))

        # Risk depends on technical analysis
        self.add_task(WorkTask(
            id="risk",
            type="risk",
            payload={"symbol": symbol},
            priority=7,
            dependencies=["technical"]
        ))

        return self.execute_all()


# Example usage
if __name__ == "__main__":
    # Create mock API client
    class MockAPI:
        pass

    orchestrator = TradingOrchestrator(MockAPI())
    result = orchestrator.analyze_symbol("XAUUSD")

    print(f"Completed: {result['completed']}/{result['total_tasks']}")
    print(f"Time: {result['execution_time_ms']:.0f}ms")
    for task_id, task_result in result["results"].items():
        print(f"  {task_id}: {task_result}")
