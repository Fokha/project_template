# ═══════════════════════════════════════════════════════════════
# BACKGROUND TASK TEMPLATE
# Async task execution with threading and queue management
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Create tasks by subclassing BackgroundTask
# 3. Submit tasks to TaskManager
#
# ═══════════════════════════════════════════════════════════════

import threading
import queue
import logging
import time
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, Future
import uuid

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskResult:
    """Result of task execution."""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: str = None
    started_at: datetime = None
    completed_at: datetime = None
    duration: float = None

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration": self.duration,
        }


@dataclass
class TaskInfo:
    """Information about a task."""
    task_id: str
    name: str
    status: TaskStatus
    progress: int = 0  # 0-100
    message: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════
# BASE TASK CLASS
# ═══════════════════════════════════════════════════════════════


class BackgroundTask:
    """
    Base class for background tasks.

    Subclass and implement execute() method.
    """

    name: str = "background_task"

    def __init__(self, **kwargs):
        self.task_id = str(uuid.uuid4())[:8]
        self.params = kwargs
        self.progress = 0
        self.message = ""
        self._cancelled = False

    def execute(self) -> Any:
        """
        Execute the task. Override in subclass.

        Returns:
            Task result (any serializable type)
        """
        raise NotImplementedError("Subclass must implement execute()")

    def update_progress(self, progress: int, message: str = ""):
        """Update task progress (0-100)."""
        self.progress = min(100, max(0, progress))
        self.message = message
        logger.debug(f"Task {self.task_id}: {self.progress}% - {message}")

    def cancel(self):
        """Request task cancellation."""
        self._cancelled = True

    @property
    def is_cancelled(self) -> bool:
        """Check if cancellation was requested."""
        return self._cancelled


# ═══════════════════════════════════════════════════════════════
# TASK MANAGER
# ═══════════════════════════════════════════════════════════════


class TaskManager:
    """
    Manages background task execution.

    Features:
    - Thread pool execution
    - Task status tracking
    - Progress monitoring
    - Task cancellation
    """

    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, TaskInfo] = {}
        self.results: Dict[str, TaskResult] = {}
        self.futures: Dict[str, Future] = {}
        self._lock = threading.Lock()

    def submit(self, task: BackgroundTask) -> str:
        """
        Submit a task for execution.

        Args:
            task: BackgroundTask instance

        Returns:
            Task ID for status polling
        """
        task_id = task.task_id

        with self._lock:
            self.tasks[task_id] = TaskInfo(
                task_id=task_id,
                name=task.name,
                status=TaskStatus.PENDING,
                metadata=task.params,
            )

        future = self.executor.submit(self._execute_task, task)
        self.futures[task_id] = future

        logger.info(f"Task submitted: {task_id} ({task.name})")
        return task_id

    def _execute_task(self, task: BackgroundTask) -> TaskResult:
        """Execute a task and capture result."""
        task_id = task.task_id
        started_at = datetime.utcnow()

        with self._lock:
            self.tasks[task_id].status = TaskStatus.RUNNING
            self.tasks[task_id].started_at = started_at

        try:
            logger.info(f"Task started: {task_id}")
            result = task.execute()

            completed_at = datetime.utcnow()
            duration = (completed_at - started_at).total_seconds()

            task_result = TaskResult(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                result=result,
                started_at=started_at,
                completed_at=completed_at,
                duration=duration,
            )

            with self._lock:
                self.tasks[task_id].status = TaskStatus.COMPLETED
                self.tasks[task_id].progress = 100
                self.results[task_id] = task_result

            logger.info(f"Task completed: {task_id} ({duration:.2f}s)")

        except Exception as e:
            completed_at = datetime.utcnow()
            duration = (completed_at - started_at).total_seconds()

            task_result = TaskResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                error=str(e),
                started_at=started_at,
                completed_at=completed_at,
                duration=duration,
            )

            with self._lock:
                self.tasks[task_id].status = TaskStatus.FAILED
                self.tasks[task_id].message = str(e)
                self.results[task_id] = task_result

            logger.exception(f"Task failed: {task_id}")

        return task_result

    def get_status(self, task_id: str) -> Optional[TaskInfo]:
        """Get task status."""
        return self.tasks.get(task_id)

    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """Get task result (None if not completed)."""
        return self.results.get(task_id)

    def wait(self, task_id: str, timeout: float = None) -> TaskResult:
        """Wait for task completion."""
        future = self.futures.get(task_id)
        if future:
            future.result(timeout=timeout)
        return self.results.get(task_id)

    def cancel(self, task_id: str) -> bool:
        """Cancel a pending task."""
        future = self.futures.get(task_id)
        if future and not future.done():
            cancelled = future.cancel()
            if cancelled:
                with self._lock:
                    self.tasks[task_id].status = TaskStatus.CANCELLED
            return cancelled
        return False

    def list_tasks(self, status: TaskStatus = None) -> List[TaskInfo]:
        """List all tasks, optionally filtered by status."""
        with self._lock:
            tasks = list(self.tasks.values())

        if status:
            tasks = [t for t in tasks if t.status == status]

        return tasks

    def cleanup(self, max_age_hours: int = 24):
        """Remove old completed/failed tasks."""
        cutoff = datetime.utcnow().timestamp() - (max_age_hours * 3600)

        with self._lock:
            to_remove = [
                task_id for task_id, info in self.tasks.items()
                if info.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
                and info.created_at.timestamp() < cutoff
            ]

            for task_id in to_remove:
                del self.tasks[task_id]
                self.results.pop(task_id, None)
                self.futures.pop(task_id, None)

        logger.info(f"Cleaned up {len(to_remove)} old tasks")

    def shutdown(self, wait: bool = True):
        """Shutdown the task manager."""
        self.executor.shutdown(wait=wait)
        logger.info("Task manager shut down")


# ═══════════════════════════════════════════════════════════════
# SCHEDULED TASK RUNNER
# ═══════════════════════════════════════════════════════════════


class ScheduledTaskRunner:
    """
    Run tasks on a schedule.

    Simple alternative to APScheduler for basic needs.
    """

    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
        self.schedules: Dict[str, Dict] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def schedule(
        self,
        name: str,
        task_factory: Callable[[], BackgroundTask],
        interval_seconds: int
    ):
        """
        Schedule a task to run periodically.

        Args:
            name: Unique schedule name
            task_factory: Function that creates task instance
            interval_seconds: Run every N seconds
        """
        self.schedules[name] = {
            "factory": task_factory,
            "interval": interval_seconds,
            "last_run": 0,
        }
        logger.info(f"Scheduled '{name}' every {interval_seconds}s")

    def start(self):
        """Start the scheduler."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Scheduler started")

    def stop(self):
        """Stop the scheduler."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Scheduler stopped")

    def _run_loop(self):
        """Main scheduler loop."""
        while self._running:
            now = time.time()

            for name, schedule in self.schedules.items():
                if now - schedule["last_run"] >= schedule["interval"]:
                    try:
                        task = schedule["factory"]()
                        self.task_manager.submit(task)
                        schedule["last_run"] = now
                        logger.debug(f"Triggered scheduled task: {name}")
                    except Exception as e:
                        logger.exception(f"Error creating scheduled task {name}")

            time.sleep(1)  # Check every second


# ═══════════════════════════════════════════════════════════════
# FLASK INTEGRATION
# ═══════════════════════════════════════════════════════════════


def create_task_endpoints(app, task_manager: TaskManager):
    """Add task management endpoints to Flask app."""
    from flask import jsonify, request

    @app.route('/api/tasks', methods=['GET'])
    def list_tasks():
        """List all tasks."""
        status_filter = request.args.get('status')
        if status_filter:
            status = TaskStatus(status_filter)
            tasks = task_manager.list_tasks(status)
        else:
            tasks = task_manager.list_tasks()

        return jsonify({
            "success": True,
            "data": [
                {
                    "task_id": t.task_id,
                    "name": t.name,
                    "status": t.status.value,
                    "progress": t.progress,
                    "message": t.message,
                }
                for t in tasks
            ]
        })

    @app.route('/api/tasks/<task_id>', methods=['GET'])
    def get_task(task_id):
        """Get task status and result."""
        info = task_manager.get_status(task_id)
        if not info:
            return jsonify({"success": False, "error": "Task not found"}), 404

        result = task_manager.get_result(task_id)

        return jsonify({
            "success": True,
            "data": {
                "task_id": info.task_id,
                "name": info.name,
                "status": info.status.value,
                "progress": info.progress,
                "message": info.message,
                "result": result.result if result else None,
                "error": result.error if result else None,
            }
        })

    @app.route('/api/tasks/<task_id>/cancel', methods=['POST'])
    def cancel_task(task_id):
        """Cancel a pending task."""
        cancelled = task_manager.cancel(task_id)
        return jsonify({
            "success": cancelled,
            "message": "Task cancelled" if cancelled else "Could not cancel task"
        })


# ═══════════════════════════════════════════════════════════════
# EXAMPLE TASKS
# ═══════════════════════════════════════════════════════════════


class DataProcessingTask(BackgroundTask):
    """Example: Process a batch of data."""

    name = "data_processing"

    def execute(self) -> Dict:
        items = self.params.get('items', [])
        total = len(items)
        processed = []

        for i, item in enumerate(items):
            if self.is_cancelled:
                return {"status": "cancelled", "processed": len(processed)}

            # Simulate processing
            time.sleep(0.1)
            processed.append({"id": item, "result": item * 2})

            self.update_progress(
                int((i + 1) / total * 100),
                f"Processed {i + 1}/{total} items"
            )

        return {"status": "completed", "processed": len(processed), "results": processed}


class ReportGenerationTask(BackgroundTask):
    """Example: Generate a report."""

    name = "report_generation"

    def execute(self) -> Dict:
        report_type = self.params.get('type', 'summary')

        self.update_progress(10, "Gathering data...")
        time.sleep(0.5)

        self.update_progress(40, "Analyzing...")
        time.sleep(0.5)

        self.update_progress(70, "Generating report...")
        time.sleep(0.5)

        self.update_progress(100, "Complete")

        return {
            "report_type": report_type,
            "generated_at": datetime.utcnow().isoformat(),
            "data": {"metric1": 100, "metric2": 200},
        }


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("BACKGROUND TASK DEMO")
    print("=" * 60)

    # Create task manager
    manager = TaskManager(max_workers=2)

    # Submit tasks
    task1 = DataProcessingTask(items=[1, 2, 3, 4, 5])
    task2 = ReportGenerationTask(type="weekly")

    task_id1 = manager.submit(task1)
    task_id2 = manager.submit(task2)

    print(f"\nSubmitted tasks: {task_id1}, {task_id2}")

    # Poll status
    print("\nPolling status...")
    for _ in range(10):
        time.sleep(0.3)

        for task_id in [task_id1, task_id2]:
            info = manager.get_status(task_id)
            print(f"  {task_id}: {info.status.value} ({info.progress}%) - {info.message}")

        # Check if both done
        if all(
            manager.get_status(tid).status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
            for tid in [task_id1, task_id2]
        ):
            break

    # Get results
    print("\nResults:")
    for task_id in [task_id1, task_id2]:
        result = manager.get_result(task_id)
        print(f"  {task_id}: {result.to_dict()}")

    # Cleanup
    manager.shutdown()
    print("\nDone!")
