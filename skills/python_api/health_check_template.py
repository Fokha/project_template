# ═══════════════════════════════════════════════════════════════
# HEALTH CHECK TEMPLATE
# Service monitoring endpoints for Flask APIs
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Register health check blueprint
# 3. Add custom health checks as needed
#
# ═══════════════════════════════════════════════════════════════

import os
import sys
import time
import logging
import threading
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from flask import Blueprint, jsonify

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════


class HealthStatus(Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class CheckResult:
    """Result of a single health check."""
    name: str
    status: HealthStatus
    message: str = ""
    duration_ms: float = 0
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "duration_ms": round(self.duration_ms, 2),
            "metadata": self.metadata,
        }


@dataclass
class HealthReport:
    """Complete health report."""
    status: HealthStatus
    version: str
    uptime: float
    timestamp: str
    checks: List[CheckResult] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "status": self.status.value,
            "version": self.version,
            "uptime_seconds": round(self.uptime, 2),
            "timestamp": self.timestamp,
            "checks": [c.to_dict() for c in self.checks],
        }


# ═══════════════════════════════════════════════════════════════
# HEALTH CHECK REGISTRY
# ═══════════════════════════════════════════════════════════════


class HealthCheckRegistry:
    """
    Registry for health checks.

    Register custom checks that will be run on health endpoints.
    """

    def __init__(self, version: str = "1.0.0"):
        self.version = version
        self.start_time = time.time()
        self.checks: Dict[str, Callable] = {}
        self._lock = threading.Lock()

    def register(self, name: str, check_func: Callable[[], CheckResult]):
        """
        Register a health check.

        Args:
            name: Unique check name
            check_func: Function that returns CheckResult
        """
        with self._lock:
            self.checks[name] = check_func
        logger.info(f"Registered health check: {name}")

    def unregister(self, name: str):
        """Remove a health check."""
        with self._lock:
            self.checks.pop(name, None)

    def run_all(self) -> HealthReport:
        """Run all health checks and return report."""
        results = []
        overall_status = HealthStatus.HEALTHY

        with self._lock:
            check_funcs = dict(self.checks)

        for name, check_func in check_funcs.items():
            start = time.time()
            try:
                result = check_func()
                result.duration_ms = (time.time() - start) * 1000
            except Exception as e:
                result = CheckResult(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check failed: {str(e)}",
                    duration_ms=(time.time() - start) * 1000,
                )
                logger.exception(f"Health check failed: {name}")

            results.append(result)

            # Update overall status
            if result.status == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
            elif result.status == HealthStatus.DEGRADED and overall_status != HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.DEGRADED

        return HealthReport(
            status=overall_status,
            version=self.version,
            uptime=time.time() - self.start_time,
            timestamp=datetime.utcnow().isoformat(),
            checks=results,
        )

    def run_check(self, name: str) -> Optional[CheckResult]:
        """Run a specific health check."""
        check_func = self.checks.get(name)
        if not check_func:
            return None

        start = time.time()
        try:
            result = check_func()
            result.duration_ms = (time.time() - start) * 1000
            return result
        except Exception as e:
            return CheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed: {str(e)}",
                duration_ms=(time.time() - start) * 1000,
            )


# ═══════════════════════════════════════════════════════════════
# BUILT-IN CHECKS
# ═══════════════════════════════════════════════════════════════


def create_database_check(db_path: str) -> Callable:
    """Create a database connectivity check."""
    def check() -> CheckResult:
        import sqlite3
        try:
            conn = sqlite3.connect(db_path, timeout=5)
            cursor = conn.execute("SELECT 1")
            cursor.fetchone()
            conn.close()
            return CheckResult(
                name="database",
                status=HealthStatus.HEALTHY,
                message="Database connection OK",
            )
        except Exception as e:
            return CheckResult(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database error: {str(e)}",
            )
    return check


def create_disk_space_check(path: str = "/", threshold_percent: int = 90) -> Callable:
    """Create a disk space check."""
    def check() -> CheckResult:
        import shutil
        try:
            total, used, free = shutil.disk_usage(path)
            used_percent = (used / total) * 100

            if used_percent >= threshold_percent:
                return CheckResult(
                    name="disk_space",
                    status=HealthStatus.DEGRADED,
                    message=f"Disk usage high: {used_percent:.1f}%",
                    metadata={
                        "total_gb": round(total / (1024**3), 2),
                        "used_gb": round(used / (1024**3), 2),
                        "free_gb": round(free / (1024**3), 2),
                        "used_percent": round(used_percent, 1),
                    }
                )

            return CheckResult(
                name="disk_space",
                status=HealthStatus.HEALTHY,
                message=f"Disk usage: {used_percent:.1f}%",
                metadata={
                    "total_gb": round(total / (1024**3), 2),
                    "free_gb": round(free / (1024**3), 2),
                    "used_percent": round(used_percent, 1),
                }
            )
        except Exception as e:
            return CheckResult(
                name="disk_space",
                status=HealthStatus.UNHEALTHY,
                message=f"Disk check failed: {str(e)}",
            )
    return check


def create_memory_check(threshold_percent: int = 90) -> Callable:
    """Create a memory usage check."""
    def check() -> CheckResult:
        try:
            import psutil
            memory = psutil.virtual_memory()

            if memory.percent >= threshold_percent:
                return CheckResult(
                    name="memory",
                    status=HealthStatus.DEGRADED,
                    message=f"Memory usage high: {memory.percent}%",
                    metadata={
                        "total_gb": round(memory.total / (1024**3), 2),
                        "available_gb": round(memory.available / (1024**3), 2),
                        "used_percent": memory.percent,
                    }
                )

            return CheckResult(
                name="memory",
                status=HealthStatus.HEALTHY,
                message=f"Memory usage: {memory.percent}%",
                metadata={
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": memory.percent,
                }
            )
        except ImportError:
            return CheckResult(
                name="memory",
                status=HealthStatus.HEALTHY,
                message="psutil not installed, skipping memory check",
            )
        except Exception as e:
            return CheckResult(
                name="memory",
                status=HealthStatus.UNHEALTHY,
                message=f"Memory check failed: {str(e)}",
            )
    return check


def create_external_api_check(url: str, timeout: int = 5) -> Callable:
    """Create an external API health check."""
    def check() -> CheckResult:
        import urllib.request
        try:
            start = time.time()
            req = urllib.request.Request(url, method='GET')
            with urllib.request.urlopen(req, timeout=timeout) as response:
                latency = (time.time() - start) * 1000
                if response.status == 200:
                    return CheckResult(
                        name=f"external_api_{url.split('/')[2]}",
                        status=HealthStatus.HEALTHY,
                        message=f"API responding ({latency:.0f}ms)",
                        metadata={"url": url, "latency_ms": round(latency, 2)}
                    )
                else:
                    return CheckResult(
                        name=f"external_api_{url.split('/')[2]}",
                        status=HealthStatus.DEGRADED,
                        message=f"API returned {response.status}",
                        metadata={"url": url, "status_code": response.status}
                    )
        except Exception as e:
            return CheckResult(
                name=f"external_api_{url.split('/')[2]}",
                status=HealthStatus.UNHEALTHY,
                message=f"API unreachable: {str(e)}",
                metadata={"url": url}
            )
    return check


def create_redis_check(host: str = "localhost", port: int = 6379) -> Callable:
    """Create a Redis connectivity check."""
    def check() -> CheckResult:
        try:
            import redis
            client = redis.Redis(host=host, port=port, socket_timeout=5)
            client.ping()
            return CheckResult(
                name="redis",
                status=HealthStatus.HEALTHY,
                message="Redis connection OK",
                metadata={"host": host, "port": port}
            )
        except ImportError:
            return CheckResult(
                name="redis",
                status=HealthStatus.HEALTHY,
                message="redis-py not installed, skipping Redis check",
            )
        except Exception as e:
            return CheckResult(
                name="redis",
                status=HealthStatus.UNHEALTHY,
                message=f"Redis error: {str(e)}",
                metadata={"host": host, "port": port}
            )
    return check


# ═══════════════════════════════════════════════════════════════
# FLASK BLUEPRINT
# ═══════════════════════════════════════════════════════════════


def create_health_blueprint(registry: HealthCheckRegistry) -> Blueprint:
    """Create Flask blueprint for health endpoints."""

    bp = Blueprint('health', __name__)

    @bp.route('/health', methods=['GET'])
    def health():
        """
        GET /health

        Full health check with all registered checks.
        Returns 200 if healthy, 503 if unhealthy.
        """
        report = registry.run_all()
        status_code = 200 if report.status != HealthStatus.UNHEALTHY else 503
        return jsonify(report.to_dict()), status_code

    @bp.route('/health/live', methods=['GET'])
    def liveness():
        """
        GET /health/live

        Kubernetes liveness probe.
        Returns 200 if the process is running.
        """
        return jsonify({
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat(),
        }), 200

    @bp.route('/health/ready', methods=['GET'])
    def readiness():
        """
        GET /health/ready

        Kubernetes readiness probe.
        Returns 200 if ready to serve traffic.
        """
        report = registry.run_all()
        ready = report.status != HealthStatus.UNHEALTHY

        return jsonify({
            "status": "ready" if ready else "not_ready",
            "checks_passed": sum(1 for c in report.checks if c.status == HealthStatus.HEALTHY),
            "checks_total": len(report.checks),
            "timestamp": datetime.utcnow().isoformat(),
        }), 200 if ready else 503

    @bp.route('/health/<check_name>', methods=['GET'])
    def single_check(check_name: str):
        """
        GET /health/<check_name>

        Run a specific health check.
        """
        result = registry.run_check(check_name)
        if result is None:
            return jsonify({"error": f"Check not found: {check_name}"}), 404

        status_code = 200 if result.status != HealthStatus.UNHEALTHY else 503
        return jsonify(result.to_dict()), status_code

    @bp.route('/version', methods=['GET'])
    def version():
        """
        GET /version

        Return application version info.
        """
        return jsonify({
            "version": registry.version,
            "python_version": sys.version,
            "uptime_seconds": round(time.time() - registry.start_time, 2),
        }), 200

    return bp


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    from flask import Flask

    print("=" * 60)
    print("HEALTH CHECK TEMPLATE DEMO")
    print("=" * 60)

    # Create registry
    registry = HealthCheckRegistry(version="1.0.0")

    # Register built-in checks
    registry.register("disk_space", create_disk_space_check("/"))
    registry.register("memory", create_memory_check())

    # Register custom check
    def custom_check() -> CheckResult:
        return CheckResult(
            name="custom",
            status=HealthStatus.HEALTHY,
            message="Custom check passed",
            metadata={"custom_value": 42}
        )

    registry.register("custom", custom_check)

    # Run checks manually
    print("\n--- Running Health Checks ---")
    report = registry.run_all()
    print(f"\nOverall Status: {report.status.value}")
    print(f"Version: {report.version}")
    print(f"Uptime: {report.uptime:.2f}s")

    print("\nCheck Results:")
    for check in report.checks:
        status_icon = "" if check.status == HealthStatus.HEALTHY else "" if check.status == HealthStatus.DEGRADED else ""
        print(f"  {status_icon} {check.name}: {check.status.value} ({check.duration_ms:.2f}ms)")
        if check.metadata:
            for key, value in check.metadata.items():
                print(f"      {key}: {value}")

    # Create Flask app
    print("\n--- Flask Integration ---")
    app = Flask(__name__)
    health_bp = create_health_blueprint(registry)
    app.register_blueprint(health_bp)

    print("\nRegistered endpoints:")
    print("  GET /health       - Full health check")
    print("  GET /health/live  - Liveness probe")
    print("  GET /health/ready - Readiness probe")
    print("  GET /health/<name> - Single check")
    print("  GET /version      - Version info")

    # Uncomment to run Flask server
    # app.run(debug=True, port=5050)
