"""
Docker Container Template
=========================
Patterns for Docker containerization and orchestration.

Use when:
- Containerizing applications
- Multi-stage builds needed
- Docker Compose orchestration
- Container health management

Placeholders:
- {{BASE_IMAGE}}: Base Docker image
- {{APP_PORT}}: Application port
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class DockerConfig:
    """Docker configuration."""
    image_name: str
    tag: str = "latest"
    base_image: str = "python:3.11-slim"
    app_port: int = 8000
    working_dir: str = "/app"
    user: str = "appuser"
    environment: Dict[str, str] = field(default_factory=dict)
    volumes: List[str] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)


class DockerfileGenerator:
    """Generate Dockerfile content."""

    def __init__(self, config: DockerConfig):
        self.config = config

    def generate_python_app(
        self,
        requirements_file: str = "requirements.txt",
        entry_point: str = "python main.py",
        multi_stage: bool = True
    ) -> str:
        """Generate Dockerfile for Python application."""
        if multi_stage:
            return self._generate_multi_stage(requirements_file, entry_point)
        return self._generate_single_stage(requirements_file, entry_point)

    def _generate_multi_stage(
        self,
        requirements_file: str,
        entry_point: str
    ) -> str:
        """Generate multi-stage Dockerfile."""
        return f'''# Multi-stage build for {self.config.image_name}
# Stage 1: Build
FROM {self.config.base_image} AS builder

WORKDIR {self.config.working_dir}

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY {requirements_file} .
RUN pip install --no-cache-dir --user -r {requirements_file}

# Stage 2: Production
FROM {self.config.base_image}

# Labels
{self._generate_labels()}

# Create non-root user
RUN useradd --create-home --shell /bin/bash {self.config.user}

WORKDIR {self.config.working_dir}

# Copy dependencies from builder
COPY --from=builder /root/.local /home/{self.config.user}/.local
ENV PATH=/home/{self.config.user}/.local/bin:$PATH

# Copy application
COPY --chown={self.config.user}:{self.config.user} . .

# Switch to non-root user
USER {self.config.user}

# Environment variables
{self._generate_env_vars()}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:{self.config.app_port}/health')" || exit 1

# Expose port
EXPOSE {self.config.app_port}

# Entry point
CMD [{', '.join(f'"{x}"' for x in entry_point.split())}]
'''

    def _generate_single_stage(
        self,
        requirements_file: str,
        entry_point: str
    ) -> str:
        """Generate single-stage Dockerfile."""
        return f'''# Single-stage build for {self.config.image_name}
FROM {self.config.base_image}

{self._generate_labels()}

# Create non-root user
RUN useradd --create-home --shell /bin/bash {self.config.user}

WORKDIR {self.config.working_dir}

# Install dependencies
COPY {requirements_file} .
RUN pip install --no-cache-dir -r {requirements_file}

# Copy application
COPY --chown={self.config.user}:{self.config.user} . .

USER {self.config.user}

{self._generate_env_vars()}

EXPOSE {self.config.app_port}

CMD [{', '.join(f'"{x}"' for x in entry_point.split())}]
'''

    def _generate_labels(self) -> str:
        """Generate LABEL instructions."""
        labels = {
            "maintainer": "team@example.com",
            "version": self.config.tag,
            "description": f"{self.config.image_name} container",
            **self.config.labels
        }
        lines = ["LABEL \\"]
        for key, value in labels.items():
            lines.append(f'    {key}="{value}" \\')
        return "\n".join(lines).rstrip(" \\")

    def _generate_env_vars(self) -> str:
        """Generate ENV instructions."""
        if not self.config.environment:
            return ""
        lines = ["ENV \\"]
        for key, value in self.config.environment.items():
            lines.append(f'    {key}="{value}" \\')
        return "\n".join(lines).rstrip(" \\")


class DockerComposeGenerator:
    """Generate Docker Compose configuration."""

    def __init__(self):
        self.services: Dict[str, Dict[str, Any]] = {}
        self.networks: Dict[str, Dict[str, Any]] = {}
        self.volumes: Dict[str, Dict[str, Any]] = {}

    def add_service(
        self,
        name: str,
        image: str,
        ports: List[str] = None,
        environment: Dict[str, str] = None,
        volumes: List[str] = None,
        depends_on: List[str] = None,
        networks: List[str] = None,
        healthcheck: Dict[str, Any] = None,
        restart: str = "unless-stopped"
    ) -> "DockerComposeGenerator":
        """Add a service to compose file."""
        service = {
            "image": image,
            "restart": restart
        }

        if ports:
            service["ports"] = ports
        if environment:
            service["environment"] = environment
        if volumes:
            service["volumes"] = volumes
        if depends_on:
            service["depends_on"] = depends_on
        if networks:
            service["networks"] = networks
        if healthcheck:
            service["healthcheck"] = healthcheck

        self.services[name] = service
        return self

    def add_network(
        self,
        name: str,
        driver: str = "bridge"
    ) -> "DockerComposeGenerator":
        """Add a network."""
        self.networks[name] = {"driver": driver}
        return self

    def add_volume(
        self,
        name: str,
        driver: str = "local"
    ) -> "DockerComposeGenerator":
        """Add a volume."""
        self.volumes[name] = {"driver": driver}
        return self

    def generate(self) -> str:
        """Generate docker-compose.yml content."""
        compose = {
            "version": "3.8",
            "services": self.services
        }

        if self.networks:
            compose["networks"] = self.networks
        if self.volumes:
            compose["volumes"] = self.volumes

        # Convert to YAML-like format
        return self._to_yaml(compose)

    def _to_yaml(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Convert dict to YAML string."""
        lines = []
        prefix = "  " * indent

        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(self._to_yaml(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"{prefix}  -")
                        for k, v in item.items():
                            lines.append(f"{prefix}    {k}: {v}")
                    else:
                        lines.append(f"{prefix}  - {item}")
            else:
                lines.append(f"{prefix}{key}: {value}")

        return "\n".join(lines)


def create_trading_stack() -> DockerComposeGenerator:
    """Create Docker Compose for trading system."""
    compose = DockerComposeGenerator()

    # API Service
    compose.add_service(
        name="api",
        image="fokha-ml-api:latest",
        ports=["5050:5050"],
        environment={
            "FLASK_ENV": "production",
            "DB_PATH": "/data/trading.db"
        },
        volumes=[
            "api-data:/data",
            "./config:/app/config:ro"
        ],
        networks=["trading-net"],
        healthcheck={
            "test": ["CMD", "curl", "-f", "http://localhost:5050/health"],
            "interval": "30s",
            "timeout": "10s",
            "retries": 3
        }
    )

    # N8N Automation
    compose.add_service(
        name="n8n",
        image="n8nio/n8n:latest",
        ports=["5678:5678"],
        environment={
            "N8N_BASIC_AUTH_ACTIVE": "true",
            "N8N_BASIC_AUTH_USER": "${N8N_USER}",
            "N8N_BASIC_AUTH_PASSWORD": "${N8N_PASSWORD}"
        },
        volumes=["n8n-data:/home/node/.n8n"],
        depends_on=["api"],
        networks=["trading-net"]
    )

    # WebSocket Server
    compose.add_service(
        name="websocket",
        image="fokha-ws-server:latest",
        ports=["8765:8765"],
        depends_on=["api"],
        networks=["trading-net"]
    )

    # Redis Cache
    compose.add_service(
        name="redis",
        image="redis:7-alpine",
        ports=["6379:6379"],
        volumes=["redis-data:/data"],
        networks=["trading-net"]
    )

    # Add network and volumes
    compose.add_network("trading-net")
    compose.add_volume("api-data")
    compose.add_volume("n8n-data")
    compose.add_volume("redis-data")

    return compose


class DockerHealthChecker:
    """Check Docker container health."""

    def __init__(self, docker_client: Any = None):
        self.client = docker_client

    def check_container(self, container_name: str) -> Dict[str, Any]:
        """Check container health status."""
        # This would use docker SDK in real implementation
        return {
            "name": container_name,
            "status": "running",
            "health": "healthy",
            "uptime": "2d 5h 30m",
            "memory_usage": "256MB / 512MB",
            "cpu_usage": "5%"
        }

    def check_all_containers(self) -> List[Dict[str, Any]]:
        """Check all containers."""
        containers = ["api", "n8n", "websocket", "redis"]
        return [self.check_container(c) for c in containers]


# Example usage
if __name__ == "__main__":
    # Generate Dockerfile
    config = DockerConfig(
        image_name="fokha-ml-api",
        tag="1.0.0",
        base_image="python:3.11-slim",
        app_port=5050,
        environment={
            "FLASK_ENV": "production",
            "LOG_LEVEL": "INFO"
        },
        labels={
            "app": "fokha-trading",
            "component": "api"
        }
    )

    generator = DockerfileGenerator(config)
    dockerfile = generator.generate_python_app(
        requirements_file="requirements.txt",
        entry_point="gunicorn -w 4 -b 0.0.0.0:5050 api_server:app"
    )

    print("Generated Dockerfile:")
    print("=" * 50)
    print(dockerfile)

    # Generate Docker Compose
    print("\n\nGenerated docker-compose.yml:")
    print("=" * 50)
    compose = create_trading_stack()
    print(compose.generate())
