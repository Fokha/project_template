"""
Deployment Automation Template
==============================
Patterns for automated deployments.

Use when:
- Automated deployments needed
- Rolling updates required
- Blue-green deployments
- Canary releases

Placeholders:
- {{DEPLOY_TARGET}}: Deployment target (staging/production)
- {{ROLLBACK_TIMEOUT}}: Time before auto-rollback
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
import logging
import time

logger = logging.getLogger(__name__)


class DeploymentStrategy(Enum):
    ROLLING = "rolling"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    RECREATE = "recreate"


class DeploymentStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class DeploymentConfig:
    """Deployment configuration."""
    name: str
    version: str
    environment: str
    strategy: DeploymentStrategy = DeploymentStrategy.ROLLING
    replicas: int = 3
    max_surge: int = 1
    max_unavailable: int = 0
    health_check_path: str = "/health"
    health_check_interval: int = 10
    rollback_on_failure: bool = True
    timeout_seconds: int = 300


@dataclass
class DeploymentResult:
    """Result of a deployment."""
    status: DeploymentStatus
    version: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0
    message: str = ""
    rollback_version: Optional[str] = None


class Deployer(ABC):
    """Abstract deployer."""

    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.history: List[DeploymentResult] = []

    @abstractmethod
    def deploy(self) -> DeploymentResult:
        """Execute deployment."""
        pass

    @abstractmethod
    def rollback(self, version: str) -> DeploymentResult:
        """Rollback to a previous version."""
        pass

    @abstractmethod
    def get_current_version(self) -> str:
        """Get currently deployed version."""
        pass


class RollingDeployer(Deployer):
    """Rolling deployment strategy."""

    def __init__(self, config: DeploymentConfig, health_checker: Callable[[], bool]):
        super().__init__(config)
        self.health_checker = health_checker
        self._current_version = "0.0.0"

    def deploy(self) -> DeploymentResult:
        """Execute rolling deployment."""
        started = datetime.now()
        logger.info(f"Starting rolling deployment of {self.config.name} v{self.config.version}")

        try:
            total_replicas = self.config.replicas
            batch_size = self.config.max_surge + 1

            for i in range(0, total_replicas, batch_size):
                batch_end = min(i + batch_size, total_replicas)
                logger.info(f"Deploying replicas {i+1} to {batch_end}")

                # Simulate deployment
                time.sleep(0.5)

                # Health check
                if not self._wait_for_healthy():
                    raise Exception("Health check failed")

            self._current_version = self.config.version
            completed = datetime.now()

            result = DeploymentResult(
                status=DeploymentStatus.SUCCEEDED,
                version=self.config.version,
                started_at=started,
                completed_at=completed,
                duration_seconds=(completed - started).total_seconds(),
                message="Deployment completed successfully"
            )

        except Exception as e:
            completed = datetime.now()
            result = DeploymentResult(
                status=DeploymentStatus.FAILED,
                version=self.config.version,
                started_at=started,
                completed_at=completed,
                duration_seconds=(completed - started).total_seconds(),
                message=str(e)
            )

            if self.config.rollback_on_failure and self.history:
                logger.warning("Initiating automatic rollback")
                self.rollback(self.history[-1].version)

        self.history.append(result)
        return result

    def rollback(self, version: str) -> DeploymentResult:
        """Rollback to previous version."""
        started = datetime.now()
        logger.info(f"Rolling back to version {version}")

        try:
            # Simulate rollback
            time.sleep(1)
            self._current_version = version

            result = DeploymentResult(
                status=DeploymentStatus.ROLLED_BACK,
                version=version,
                started_at=started,
                completed_at=datetime.now(),
                message="Rollback completed"
            )

        except Exception as e:
            result = DeploymentResult(
                status=DeploymentStatus.FAILED,
                version=version,
                started_at=started,
                completed_at=datetime.now(),
                message=f"Rollback failed: {e}"
            )

        return result

    def get_current_version(self) -> str:
        return self._current_version

    def _wait_for_healthy(self, timeout: int = 60) -> bool:
        """Wait for deployment to become healthy."""
        start = time.time()
        while time.time() - start < timeout:
            if self.health_checker():
                return True
            time.sleep(self.config.health_check_interval)
        return False


class BlueGreenDeployer(Deployer):
    """Blue-green deployment strategy."""

    def __init__(self, config: DeploymentConfig, health_checker: Callable[[], bool]):
        super().__init__(config)
        self.health_checker = health_checker
        self.active_env = "blue"
        self._versions = {"blue": "0.0.0", "green": "0.0.0"}

    def deploy(self) -> DeploymentResult:
        """Execute blue-green deployment."""
        started = datetime.now()
        inactive_env = "green" if self.active_env == "blue" else "blue"

        logger.info(f"Deploying to {inactive_env} environment")

        try:
            # Deploy to inactive environment
            self._versions[inactive_env] = self.config.version
            time.sleep(1)  # Simulate deployment

            # Health check inactive environment
            if not self.health_checker():
                raise Exception(f"Health check failed for {inactive_env}")

            # Switch traffic
            logger.info(f"Switching traffic from {self.active_env} to {inactive_env}")
            self.active_env = inactive_env

            result = DeploymentResult(
                status=DeploymentStatus.SUCCEEDED,
                version=self.config.version,
                started_at=started,
                completed_at=datetime.now(),
                message=f"Deployed to {inactive_env}, traffic switched"
            )

        except Exception as e:
            result = DeploymentResult(
                status=DeploymentStatus.FAILED,
                version=self.config.version,
                started_at=started,
                completed_at=datetime.now(),
                message=str(e)
            )

        self.history.append(result)
        return result

    def rollback(self, version: str) -> DeploymentResult:
        """Switch back to previous environment."""
        started = datetime.now()
        inactive_env = "green" if self.active_env == "blue" else "blue"

        logger.info(f"Switching back to {inactive_env}")
        self.active_env = inactive_env

        return DeploymentResult(
            status=DeploymentStatus.ROLLED_BACK,
            version=self._versions[inactive_env],
            started_at=started,
            completed_at=datetime.now(),
            message=f"Traffic switched back to {inactive_env}"
        )

    def get_current_version(self) -> str:
        return self._versions[self.active_env]


class CanaryDeployer(Deployer):
    """Canary deployment strategy."""

    def __init__(
        self,
        config: DeploymentConfig,
        health_checker: Callable[[], bool],
        metrics_checker: Callable[[], Dict[str, float]]
    ):
        super().__init__(config)
        self.health_checker = health_checker
        self.metrics_checker = metrics_checker
        self._current_version = "0.0.0"
        self.canary_stages = [5, 25, 50, 75, 100]  # Percentage rollout

    def deploy(self) -> DeploymentResult:
        """Execute canary deployment."""
        started = datetime.now()
        logger.info(f"Starting canary deployment of v{self.config.version}")

        try:
            for stage in self.canary_stages:
                logger.info(f"Canary stage: {stage}% traffic")

                # Update traffic split
                time.sleep(1)

                # Check metrics
                metrics = self.metrics_checker()
                if not self._validate_metrics(metrics):
                    raise Exception(f"Metrics validation failed at {stage}%")

                # Health check
                if not self.health_checker():
                    raise Exception(f"Health check failed at {stage}%")

                if stage < 100:
                    # Wait before next stage
                    time.sleep(2)

            self._current_version = self.config.version

            result = DeploymentResult(
                status=DeploymentStatus.SUCCEEDED,
                version=self.config.version,
                started_at=started,
                completed_at=datetime.now(),
                message="Canary deployment completed"
            )

        except Exception as e:
            result = DeploymentResult(
                status=DeploymentStatus.FAILED,
                version=self.config.version,
                started_at=started,
                completed_at=datetime.now(),
                message=str(e)
            )

            if self.config.rollback_on_failure:
                logger.warning("Rolling back canary")
                self.rollback(self._current_version)

        self.history.append(result)
        return result

    def rollback(self, version: str) -> DeploymentResult:
        """Rollback canary deployment."""
        started = datetime.now()
        logger.info(f"Rolling back to v{version}")

        return DeploymentResult(
            status=DeploymentStatus.ROLLED_BACK,
            version=version,
            started_at=started,
            completed_at=datetime.now(),
            message="Canary rolled back to 0%"
        )

    def get_current_version(self) -> str:
        return self._current_version

    def _validate_metrics(self, metrics: Dict[str, float]) -> bool:
        """Validate deployment metrics."""
        # Error rate should be low
        if metrics.get("error_rate", 0) > 5:
            return False
        # Latency should be acceptable
        if metrics.get("p99_latency", 0) > 1000:
            return False
        return True


class DeploymentManager:
    """Manage deployments across environments."""

    def __init__(self):
        self.deployers: Dict[str, Deployer] = {}
        self.deployment_history: List[Dict[str, Any]] = []

    def register_environment(self, env: str, deployer: Deployer):
        """Register a deployment environment."""
        self.deployers[env] = deployer

    def deploy(self, env: str, version: str) -> DeploymentResult:
        """Deploy to an environment."""
        if env not in self.deployers:
            raise ValueError(f"Unknown environment: {env}")

        deployer = self.deployers[env]
        deployer.config.version = version

        result = deployer.deploy()

        self.deployment_history.append({
            "environment": env,
            "version": version,
            "status": result.status.value,
            "timestamp": datetime.now().isoformat()
        })

        return result

    def get_status(self) -> Dict[str, Any]:
        """Get deployment status for all environments."""
        status = {}
        for env, deployer in self.deployers.items():
            status[env] = {
                "current_version": deployer.get_current_version(),
                "last_deployment": deployer.history[-1] if deployer.history else None
            }
        return status


# Example usage
if __name__ == "__main__":
    # Health checker
    def health_check():
        return True

    # Metrics checker
    def metrics_check():
        return {"error_rate": 0.5, "p99_latency": 250}

    # Create deployer
    config = DeploymentConfig(
        name="trading-api",
        version="2.0.0",
        environment="production",
        strategy=DeploymentStrategy.CANARY,
        replicas=3,
        rollback_on_failure=True
    )

    deployer = CanaryDeployer(config, health_check, metrics_check)

    # Execute deployment
    print("Starting canary deployment...")
    print("-" * 50)
    result = deployer.deploy()

    print(f"\nDeployment Status: {result.status.value}")
    print(f"Version: {result.version}")
    print(f"Duration: {result.duration_seconds:.1f}s")
    print(f"Message: {result.message}")
