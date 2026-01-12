"""
Monitoring & Alerting Template
==============================
Patterns for system monitoring and alerting.

Use when:
- System health monitoring needed
- Performance metrics collection
- Alerting on anomalies
- Dashboard creation

Placeholders:
- {{ALERT_THRESHOLD}}: Alert threshold value
- {{SCRAPE_INTERVAL}}: Metrics scrape interval
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime, timedelta
import logging
import time
import threading
from collections import deque

logger = logging.getLogger(__name__)


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """A single metric."""
    name: str
    type: MetricType
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    unit: str = ""
    description: str = ""


@dataclass
class Alert:
    """An alert event."""
    name: str
    severity: AlertSeverity
    message: str
    metric_name: str
    current_value: float
    threshold: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False


@dataclass
class AlertRule:
    """Alert rule definition."""
    name: str
    metric_name: str
    condition: str  # >, <, >=, <=, ==
    threshold: float
    severity: AlertSeverity
    duration: int = 0  # seconds to wait before alerting
    message_template: str = ""
    labels: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """Collect and store metrics."""

    def __init__(self, max_history: int = 1000):
        self.metrics: Dict[str, deque] = {}
        self.max_history = max_history
        self._lock = threading.Lock()

    def record(self, metric: Metric):
        """Record a metric."""
        with self._lock:
            key = f"{metric.name}:{self._labels_key(metric.labels)}"
            if key not in self.metrics:
                self.metrics[key] = deque(maxlen=self.max_history)
            self.metrics[key].append(metric)

    def get_latest(self, name: str, labels: Dict[str, str] = None) -> Optional[Metric]:
        """Get latest value for a metric."""
        key = f"{name}:{self._labels_key(labels or {})}"
        with self._lock:
            if key in self.metrics and self.metrics[key]:
                return self.metrics[key][-1]
        return None

    def get_history(
        self,
        name: str,
        labels: Dict[str, str] = None,
        duration_seconds: int = 300
    ) -> List[Metric]:
        """Get metric history."""
        key = f"{name}:{self._labels_key(labels or {})}"
        cutoff = datetime.now() - timedelta(seconds=duration_seconds)

        with self._lock:
            if key not in self.metrics:
                return []
            return [m for m in self.metrics[key] if m.timestamp >= cutoff]

    def _labels_key(self, labels: Dict[str, str]) -> str:
        """Create key from labels."""
        return ",".join(f"{k}={v}" for k, v in sorted(labels.items()))


class AlertManager:
    """Manage alerts and notifications."""

    def __init__(self):
        self.rules: List[AlertRule] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.handlers: List[Callable[[Alert], None]] = []
        self._pending: Dict[str, tuple] = {}  # For duration-based alerts

    def add_rule(self, rule: AlertRule):
        """Add an alert rule."""
        self.rules.append(rule)

    def add_handler(self, handler: Callable[[Alert], None]):
        """Add alert notification handler."""
        self.handlers.append(handler)

    def check_alerts(self, collector: MetricsCollector):
        """Check all alert rules."""
        for rule in self.rules:
            metric = collector.get_latest(rule.metric_name, rule.labels)
            if metric is None:
                continue

            triggered = self._evaluate_condition(
                metric.value, rule.condition, rule.threshold
            )

            alert_key = f"{rule.name}:{self._labels_key(rule.labels)}"

            if triggered:
                if rule.duration > 0:
                    # Check duration
                    if alert_key not in self._pending:
                        self._pending[alert_key] = (datetime.now(), rule, metric)
                    else:
                        pending_time, _, _ = self._pending[alert_key]
                        elapsed = (datetime.now() - pending_time).total_seconds()
                        if elapsed >= rule.duration:
                            self._fire_alert(rule, metric)
                            del self._pending[alert_key]
                else:
                    self._fire_alert(rule, metric)
            else:
                # Clear pending and resolve active
                if alert_key in self._pending:
                    del self._pending[alert_key]
                if alert_key in self.active_alerts:
                    self._resolve_alert(alert_key)

    def _evaluate_condition(
        self,
        value: float,
        condition: str,
        threshold: float
    ) -> bool:
        """Evaluate alert condition."""
        if condition == ">":
            return value > threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<":
            return value < threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return value == threshold
        return False

    def _fire_alert(self, rule: AlertRule, metric: Metric):
        """Fire an alert."""
        alert_key = f"{rule.name}:{self._labels_key(rule.labels)}"

        if alert_key in self.active_alerts:
            return  # Already active

        message = rule.message_template.format(
            name=rule.name,
            value=metric.value,
            threshold=rule.threshold
        ) if rule.message_template else f"{rule.name}: {metric.value} {rule.condition} {rule.threshold}"

        alert = Alert(
            name=rule.name,
            severity=rule.severity,
            message=message,
            metric_name=rule.metric_name,
            current_value=metric.value,
            threshold=rule.threshold,
            labels=rule.labels
        )

        self.active_alerts[alert_key] = alert
        self.alert_history.append(alert)

        logger.warning(f"Alert fired: {alert.message}")

        for handler in self.handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")

    def _resolve_alert(self, alert_key: str):
        """Resolve an active alert."""
        if alert_key in self.active_alerts:
            alert = self.active_alerts[alert_key]
            alert.resolved = True
            del self.active_alerts[alert_key]
            logger.info(f"Alert resolved: {alert.name}")

    def _labels_key(self, labels: Dict[str, str]) -> str:
        """Create key from labels."""
        return ",".join(f"{k}={v}" for k, v in sorted(labels.items()))


class PrometheusExporter:
    """Export metrics in Prometheus format."""

    def __init__(self, collector: MetricsCollector):
        self.collector = collector

    def export(self) -> str:
        """Export all metrics in Prometheus format."""
        lines = []

        for key, history in self.collector.metrics.items():
            if not history:
                continue

            latest = history[-1]

            # Add HELP and TYPE
            lines.append(f"# HELP {latest.name} {latest.description}")
            lines.append(f"# TYPE {latest.name} {latest.type.value}")

            # Add metric line
            labels_str = ",".join(f'{k}="{v}"' for k, v in latest.labels.items())
            if labels_str:
                lines.append(f"{latest.name}{{{labels_str}}} {latest.value}")
            else:
                lines.append(f"{latest.name} {latest.value}")

        return "\n".join(lines)


class HealthChecker:
    """Health check implementation."""

    def __init__(self):
        self.checks: Dict[str, Callable[[], Dict[str, Any]]] = {}

    def register(self, name: str, check_fn: Callable[[], Dict[str, Any]]):
        """Register a health check."""
        self.checks[name] = check_fn

    def check_all(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = {}
        overall_healthy = True

        for name, check_fn in self.checks.items():
            try:
                start = time.time()
                result = check_fn()
                duration_ms = (time.time() - start) * 1000

                results[name] = {
                    "status": result.get("status", "unknown"),
                    "healthy": result.get("healthy", False),
                    "duration_ms": round(duration_ms, 2),
                    "details": result.get("details", {})
                }

                if not result.get("healthy", False):
                    overall_healthy = False

            except Exception as e:
                results[name] = {
                    "status": "error",
                    "healthy": False,
                    "error": str(e)
                }
                overall_healthy = False

        return {
            "healthy": overall_healthy,
            "timestamp": datetime.now().isoformat(),
            "checks": results
        }


def create_trading_monitoring() -> tuple:
    """Create monitoring setup for trading system."""
    collector = MetricsCollector()
    alert_manager = AlertManager()
    health_checker = HealthChecker()

    # Add alert rules
    alert_manager.add_rule(AlertRule(
        name="High CPU Usage",
        metric_name="system_cpu_percent",
        condition=">=",
        threshold=90,
        severity=AlertSeverity.WARNING,
        duration=60,
        message_template="CPU usage at {value}% (threshold: {threshold}%)"
    ))

    alert_manager.add_rule(AlertRule(
        name="API Latency High",
        metric_name="api_latency_p99",
        condition=">=",
        threshold=1000,
        severity=AlertSeverity.ERROR,
        message_template="API P99 latency at {value}ms (threshold: {threshold}ms)"
    ))

    alert_manager.add_rule(AlertRule(
        name="Error Rate High",
        metric_name="api_error_rate",
        condition=">=",
        threshold=5,
        severity=AlertSeverity.CRITICAL,
        message_template="API error rate at {value}% (threshold: {threshold}%)"
    ))

    alert_manager.add_rule(AlertRule(
        name="Signal Success Rate Low",
        metric_name="signal_success_rate",
        condition="<",
        threshold=50,
        severity=AlertSeverity.WARNING,
        duration=300,
        message_template="Signal success rate dropped to {value}%"
    ))

    # Register health checks
    def check_api():
        return {"status": "ok", "healthy": True, "details": {"endpoint": "/health"}}

    def check_database():
        return {"status": "ok", "healthy": True, "details": {"connections": 5}}

    def check_cache():
        return {"status": "ok", "healthy": True, "details": {"hit_rate": 0.95}}

    health_checker.register("api", check_api)
    health_checker.register("database", check_database)
    health_checker.register("cache", check_cache)

    return collector, alert_manager, health_checker


# Example usage
if __name__ == "__main__":
    collector, alert_manager, health_checker = create_trading_monitoring()

    # Add Telegram alert handler
    def telegram_handler(alert: Alert):
        print(f"[TELEGRAM] {alert.severity.value.upper()}: {alert.message}")

    alert_manager.add_handler(telegram_handler)

    # Simulate metrics
    collector.record(Metric(
        name="system_cpu_percent",
        type=MetricType.GAUGE,
        value=75,
        description="System CPU usage percentage"
    ))

    collector.record(Metric(
        name="api_latency_p99",
        type=MetricType.GAUGE,
        value=250,
        unit="ms",
        description="API P99 latency"
    ))

    collector.record(Metric(
        name="signal_success_rate",
        type=MetricType.GAUGE,
        value=65,
        unit="%",
        description="Signal prediction success rate"
    ))

    # Check alerts
    print("Checking alerts...")
    alert_manager.check_alerts(collector)

    # Export Prometheus format
    print("\nPrometheus metrics:")
    print("-" * 50)
    exporter = PrometheusExporter(collector)
    print(exporter.export())

    # Health check
    print("\nHealth check:")
    print("-" * 50)
    health = health_checker.check_all()
    print(f"Overall: {'HEALTHY' if health['healthy'] else 'UNHEALTHY'}")
    for name, check in health['checks'].items():
        status = "✓" if check['healthy'] else "✗"
        print(f"  {status} {name}: {check['status']} ({check['duration_ms']}ms)")
