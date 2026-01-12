"""
Parallelization Pattern Template
================================
Execute multiple independent tasks concurrently.

Use when:
- Tasks don't depend on each other
- Speed is important
- Multiple data sources need querying

Placeholders:
- {{MAX_WORKERS}}: Maximum concurrent workers
- {{TIMEOUT_SECONDS}}: Timeout per task
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import logging
from datetime import datetime
import threading

logger = logging.getLogger(__name__)


@dataclass
class ParallelTask:
    """A task to execute in parallel."""
    id: str
    func: Callable[..., Any]
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[float] = None


@dataclass
class TaskResult:
    """Result of a single task."""
    task_id: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time_ms: float = 0


@dataclass
class ParallelResult:
    """Result of parallel execution."""
    total_tasks: int
    successful: int
    failed: int
    results: Dict[str, TaskResult]
    total_time_ms: float


class ParallelExecutor:
    """
    Execute multiple tasks in parallel.

    Example:
        executor = ParallelExecutor(max_workers=4)
        executor.add_task(ParallelTask("t1", fetch_data, args=("XAUUSD",)))
        executor.add_task(ParallelTask("t2", fetch_data, args=("EURUSD",)))
        result = executor.execute()
    """

    def __init__(self, max_workers: int = 4, default_timeout: float = 30.0):
        self.max_workers = max_workers
        self.default_timeout = default_timeout
        self.tasks: List[ParallelTask] = []
        self._lock = threading.Lock()

    def add_task(self, task: ParallelTask) -> "ParallelExecutor":
        """Add a task to execute."""
        self.tasks.append(task)
        return self

    def add_tasks(self, tasks: List[ParallelTask]) -> "ParallelExecutor":
        """Add multiple tasks."""
        self.tasks.extend(tasks)
        return self

    def clear(self) -> "ParallelExecutor":
        """Clear all tasks."""
        self.tasks.clear()
        return self

    def execute(self) -> ParallelResult:
        """Execute all tasks in parallel."""
        start_time = datetime.now()
        results: Dict[str, TaskResult] = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self._execute_task, task): task
                for task in self.tasks
            }

            # Collect results as they complete
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result(timeout=task.timeout or self.default_timeout)
                    results[task.id] = result
                except TimeoutError:
                    results[task.id] = TaskResult(
                        task_id=task.id,
                        success=False,
                        result=None,
                        error="Task timed out"
                    )
                except Exception as e:
                    results[task.id] = TaskResult(
                        task_id=task.id,
                        success=False,
                        result=None,
                        error=str(e)
                    )

        successful = sum(1 for r in results.values() if r.success)

        return ParallelResult(
            total_tasks=len(self.tasks),
            successful=successful,
            failed=len(self.tasks) - successful,
            results=results,
            total_time_ms=(datetime.now() - start_time).total_seconds() * 1000
        )

    def _execute_task(self, task: ParallelTask) -> TaskResult:
        """Execute a single task."""
        start_time = datetime.now()
        try:
            result = task.func(*task.args, **task.kwargs)
            return TaskResult(
                task_id=task.id,
                success=True,
                result=result,
                execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")
            return TaskResult(
                task_id=task.id,
                success=False,
                result=None,
                error=str(e),
                execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )


class FanOutFanIn:
    """
    Fan-out: Split work across workers
    Fan-in: Combine results

    Useful for map-reduce style operations.
    """

    def __init__(
        self,
        max_workers: int = 4,
        combiner: Optional[Callable[[List[Any]], Any]] = None
    ):
        self.executor = ParallelExecutor(max_workers=max_workers)
        self.combiner = combiner or self._default_combiner

    def _default_combiner(self, results: List[Any]) -> List[Any]:
        """Default: return list of results."""
        return results

    def map(
        self,
        func: Callable[[Any], Any],
        items: List[Any]
    ) -> Any:
        """Map function over items and combine results."""
        # Fan-out: create tasks for each item
        for i, item in enumerate(items):
            self.executor.add_task(ParallelTask(
                id=f"item_{i}",
                func=func,
                args=(item,)
            ))

        # Execute in parallel
        result = self.executor.execute()

        # Fan-in: combine results
        successful_results = [
            r.result for r in result.results.values()
            if r.success
        ]

        return self.combiner(successful_results)


class MultiSourceFetcher:
    """
    Fetch data from multiple sources in parallel.

    Example for trading: Fetch signals from multiple timeframes simultaneously.
    """

    def __init__(self, max_workers: int = 4):
        self.executor = ParallelExecutor(max_workers=max_workers)

    def fetch_all(
        self,
        fetchers: Dict[str, Callable[[], Any]],
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        Fetch from all sources.

        Args:
            fetchers: Dict of name -> fetch function
            timeout: Timeout per fetch

        Returns:
            Dict of name -> result (or error)
        """
        for name, fetcher in fetchers.items():
            self.executor.add_task(ParallelTask(
                id=name,
                func=fetcher,
                timeout=timeout
            ))

        result = self.executor.execute()

        return {
            task_id: (r.result if r.success else {"error": r.error})
            for task_id, r in result.results.items()
        }


class TradingParallelAnalysis:
    """Pre-built parallel analysis for trading."""

    def __init__(self, api_client: Any, max_workers: int = 4):
        self.api = api_client
        self.executor = ParallelExecutor(max_workers=max_workers)

    def analyze_symbol(self, symbol: str) -> Dict[str, Any]:
        """Run multiple analyses on a symbol in parallel."""
        self.executor.clear()

        # Add all analysis tasks
        self.executor.add_task(ParallelTask(
            id="signal",
            func=lambda: self.api.get_signal(symbol)
        ))
        self.executor.add_task(ParallelTask(
            id="sentiment",
            func=lambda: self.api.get_sentiment(symbol)
        ))
        self.executor.add_task(ParallelTask(
            id="news",
            func=lambda: self.api.get_news(symbol)
        ))
        self.executor.add_task(ParallelTask(
            id="smc",
            func=lambda: self.api.get_smc_analysis(symbol)
        ))
        self.executor.add_task(ParallelTask(
            id="strength",
            func=lambda: self.api.get_currency_strength(symbol)
        ))

        # Execute and combine
        result = self.executor.execute()

        return {
            "symbol": symbol,
            "analysis": {
                task_id: (r.result if r.success else None)
                for task_id, r in result.results.items()
            },
            "execution_time_ms": result.total_time_ms,
            "success_rate": result.successful / result.total_tasks
        }

    def analyze_multiple_symbols(self, symbols: List[str]) -> Dict[str, Any]:
        """Analyze multiple symbols in parallel."""
        fetcher = MultiSourceFetcher(max_workers=len(symbols))

        fetchers = {
            symbol: lambda s=symbol: self.analyze_symbol(s)
            for symbol in symbols
        }

        return fetcher.fetch_all(fetchers)


# Example usage
if __name__ == "__main__":
    import time

    def slow_task(name: str, delay: float) -> str:
        time.sleep(delay)
        return f"Task {name} completed after {delay}s"

    # Test parallel execution
    executor = ParallelExecutor(max_workers=4)
    executor.add_task(ParallelTask("a", slow_task, args=("A", 1.0)))
    executor.add_task(ParallelTask("b", slow_task, args=("B", 0.5)))
    executor.add_task(ParallelTask("c", slow_task, args=("C", 0.8)))
    executor.add_task(ParallelTask("d", slow_task, args=("D", 0.3)))

    result = executor.execute()

    print(f"Total time: {result.total_time_ms:.0f}ms (sequential would be ~2600ms)")
    print(f"Success: {result.successful}/{result.total_tasks}")
    for task_id, r in result.results.items():
        print(f"  {task_id}: {r.result} ({r.execution_time_ms:.0f}ms)")
