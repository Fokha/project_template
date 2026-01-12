"""
API Monitor Template
====================

Monitor API health, performance, and usage metrics.

Usage:
    from services.api_monitor import APIMonitor

    monitor = APIMonitor()
    monitor.record_request('/api/users', 200, 0.125)
    stats = monitor.get_stats()

Features:
- Request/response logging
- Performance metrics (latency, throughput)
- Error rate tracking
- Endpoint-level statistics
- Alert thresholds
"""

import sqlite3
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import defaultdict
import threading


@dataclass
class RequestMetrics:
    """Metrics for a single request."""
    endpoint: str
    method: str
    status_code: int
    latency_ms: float
    timestamp: datetime
    error_message: Optional[str] = None


@dataclass
class EndpointStats:
    """Statistics for an endpoint."""
    endpoint: str
    total_requests: int
    success_count: int
    error_count: int
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    p95_latency_ms: float
    error_rate: float
    requests_per_minute: float


class APIMonitor:
    """Monitor API health and performance."""

    def __init__(self, db_path: str = "data/api_monitor.db"):
        self.db_path = db_path
        self._lock = threading.Lock()

        # In-memory cache for fast writes
        self._request_buffer: List[RequestMetrics] = []
        self._buffer_size = 100
        self._last_flush = time.time()

        # Alert thresholds
        self.thresholds = {
            'max_latency_ms': 5000,
            'error_rate_percent': 5,
            'min_success_rate': 95,
        }

        # Initialize database
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT NOT NULL,
                method TEXT DEFAULT 'GET',
                status_code INTEGER NOT NULL,
                latency_ms REAL NOT NULL,
                error_message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                endpoint TEXT,
                message TEXT NOT NULL,
                severity TEXT DEFAULT 'warning',
                resolved BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_requests_endpoint ON api_requests(endpoint)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_requests_timestamp ON api_requests(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_requests_status ON api_requests(status_code)')

        conn.commit()
        conn.close()

    def record_request(
        self,
        endpoint: str,
        status_code: int,
        latency_ms: float,
        method: str = "GET",
        error_message: Optional[str] = None
    ):
        """Record an API request."""
        metrics = RequestMetrics(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            latency_ms=latency_ms,
            timestamp=datetime.now(),
            error_message=error_message
        )

        with self._lock:
            self._request_buffer.append(metrics)

            # Flush buffer if full or enough time passed
            if len(self._request_buffer) >= self._buffer_size or \
               time.time() - self._last_flush > 10:
                self._flush_buffer()

        # Check for alerts
        self._check_alerts(metrics)

    def _flush_buffer(self):
        """Flush request buffer to database."""
        if not self._request_buffer:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.executemany('''
            INSERT INTO api_requests (endpoint, method, status_code, latency_ms, error_message, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [
            (m.endpoint, m.method, m.status_code, m.latency_ms, m.error_message, m.timestamp)
            for m in self._request_buffer
        ])

        conn.commit()
        conn.close()

        self._request_buffer.clear()
        self._last_flush = time.time()

    def _check_alerts(self, metrics: RequestMetrics):
        """Check if request triggers any alerts."""
        alerts = []

        # High latency alert
        if metrics.latency_ms > self.thresholds['max_latency_ms']:
            alerts.append({
                'type': 'high_latency',
                'endpoint': metrics.endpoint,
                'message': f"High latency: {metrics.latency_ms:.0f}ms on {metrics.endpoint}",
                'severity': 'warning'
            })

        # Error alert
        if metrics.status_code >= 500:
            alerts.append({
                'type': 'server_error',
                'endpoint': metrics.endpoint,
                'message': f"Server error {metrics.status_code} on {metrics.endpoint}: {metrics.error_message}",
                'severity': 'error'
            })

        # Store alerts
        for alert in alerts:
            self._store_alert(alert)

    def _store_alert(self, alert: Dict):
        """Store an alert in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO api_alerts (alert_type, endpoint, message, severity)
            VALUES (?, ?, ?, ?)
        ''', (alert['type'], alert.get('endpoint'), alert['message'], alert['severity']))

        conn.commit()
        conn.close()

    def get_endpoint_stats(self, endpoint: str, hours: int = 24) -> Optional[EndpointStats]:
        """Get statistics for a specific endpoint."""
        # Flush buffer first
        with self._lock:
            self._flush_buffer()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        since = datetime.now() - timedelta(hours=hours)

        cursor.execute('''
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status_code < 400 THEN 1 ELSE 0 END) as success,
                SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as errors,
                AVG(latency_ms) as avg_latency,
                MIN(latency_ms) as min_latency,
                MAX(latency_ms) as max_latency
            FROM api_requests
            WHERE endpoint = ? AND timestamp > ?
        ''', (endpoint, since))

        row = cursor.fetchone()
        conn.close()

        if not row or row[0] == 0:
            return None

        total, success, errors, avg_lat, min_lat, max_lat = row

        return EndpointStats(
            endpoint=endpoint,
            total_requests=total,
            success_count=success or 0,
            error_count=errors or 0,
            avg_latency_ms=avg_lat or 0,
            min_latency_ms=min_lat or 0,
            max_latency_ms=max_lat or 0,
            p95_latency_ms=0,  # Would need all latencies to calculate
            error_rate=(errors / total * 100) if total > 0 else 0,
            requests_per_minute=total / (hours * 60)
        )

    def get_all_stats(self, hours: int = 24) -> Dict[str, EndpointStats]:
        """Get statistics for all endpoints."""
        with self._lock:
            self._flush_buffer()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        since = datetime.now() - timedelta(hours=hours)

        cursor.execute('''
            SELECT DISTINCT endpoint FROM api_requests WHERE timestamp > ?
        ''', (since,))

        endpoints = [row[0] for row in cursor.fetchall()]
        conn.close()

        stats = {}
        for endpoint in endpoints:
            endpoint_stats = self.get_endpoint_stats(endpoint, hours)
            if endpoint_stats:
                stats[endpoint] = endpoint_stats

        return stats

    def get_health_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get overall API health summary."""
        stats = self.get_all_stats(hours)

        if not stats:
            return {
                'status': 'unknown',
                'total_requests': 0,
                'overall_error_rate': 0,
                'avg_latency_ms': 0,
                'endpoints_count': 0
            }

        total_requests = sum(s.total_requests for s in stats.values())
        total_errors = sum(s.error_count for s in stats.values())
        avg_latency = sum(s.avg_latency_ms * s.total_requests for s in stats.values()) / total_requests if total_requests > 0 else 0

        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0

        # Determine status
        if error_rate > 10:
            status = 'critical'
        elif error_rate > 5:
            status = 'degraded'
        elif avg_latency > 2000:
            status = 'slow'
        else:
            status = 'healthy'

        return {
            'status': status,
            'total_requests': total_requests,
            'overall_error_rate': round(error_rate, 2),
            'avg_latency_ms': round(avg_latency, 2),
            'endpoints_count': len(stats),
            'top_errors': self._get_top_errors(hours)
        }

    def _get_top_errors(self, hours: int = 1, limit: int = 5) -> List[Dict]:
        """Get top error endpoints."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        since = datetime.now() - timedelta(hours=hours)

        cursor.execute('''
            SELECT endpoint, COUNT(*) as error_count
            FROM api_requests
            WHERE status_code >= 400 AND timestamp > ?
            GROUP BY endpoint
            ORDER BY error_count DESC
            LIMIT ?
        ''', (since, limit))

        errors = [{'endpoint': row[0], 'count': row[1]} for row in cursor.fetchall()]
        conn.close()

        return errors

    def get_recent_alerts(self, limit: int = 20, unresolved_only: bool = False) -> List[Dict]:
        """Get recent alerts."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if unresolved_only:
            cursor.execute('''
                SELECT id, alert_type, endpoint, message, severity, created_at
                FROM api_alerts
                WHERE resolved = FALSE
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
        else:
            cursor.execute('''
                SELECT id, alert_type, endpoint, message, severity, created_at
                FROM api_alerts
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))

        alerts = [{
            'id': row[0],
            'type': row[1],
            'endpoint': row[2],
            'message': row[3],
            'severity': row[4],
            'created_at': row[5]
        } for row in cursor.fetchall()]

        conn.close()
        return alerts

    def cleanup_old_data(self, days: int = 30):
        """Remove old request data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff = datetime.now() - timedelta(days=days)

        cursor.execute('DELETE FROM api_requests WHERE timestamp < ?', (cutoff,))
        cursor.execute('DELETE FROM api_alerts WHERE created_at < ? AND resolved = TRUE', (cutoff,))

        conn.commit()
        conn.close()


# Flask middleware example
def create_flask_middleware(monitor: APIMonitor):
    """Create Flask middleware for automatic monitoring."""

    def middleware(app):
        @app.before_request
        def before_request():
            from flask import request, g
            g.request_start_time = time.time()

        @app.after_request
        def after_request(response):
            from flask import request, g
            latency_ms = (time.time() - g.request_start_time) * 1000
            monitor.record_request(
                endpoint=request.path,
                method=request.method,
                status_code=response.status_code,
                latency_ms=latency_ms
            )
            return response

        return app

    return middleware


# Example usage
if __name__ == "__main__":
    monitor = APIMonitor()

    # Simulate some requests
    import random
    endpoints = ['/api/users', '/api/products', '/api/orders', '/health']

    for _ in range(100):
        endpoint = random.choice(endpoints)
        status = random.choices([200, 201, 400, 500], weights=[80, 10, 8, 2])[0]
        latency = random.uniform(50, 500) if status < 400 else random.uniform(100, 2000)

        monitor.record_request(endpoint, status, latency)

    # Get stats
    print("\n=== Health Summary ===")
    health = monitor.get_health_summary()
    print(f"Status: {health['status']}")
    print(f"Total Requests: {health['total_requests']}")
    print(f"Error Rate: {health['overall_error_rate']}%")
    print(f"Avg Latency: {health['avg_latency_ms']}ms")

    print("\n=== Endpoint Stats ===")
    for endpoint, stats in monitor.get_all_stats().items():
        print(f"{endpoint}: {stats.total_requests} requests, {stats.error_rate:.1f}% errors, {stats.avg_latency_ms:.0f}ms avg")
