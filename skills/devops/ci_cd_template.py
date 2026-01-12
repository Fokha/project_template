"""
CI/CD Pipeline Template
=======================
Patterns for continuous integration and deployment.

Use when:
- Automated testing needed
- Continuous deployment required
- Multi-environment deployments
- Quality gates enforcement

Placeholders:
- {{REPO_NAME}}: Repository name
- {{DEPLOY_ENV}}: Deployment environment
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    BUILD = "build"
    TEST = "test"
    SECURITY_SCAN = "security_scan"
    DEPLOY_STAGING = "deploy_staging"
    INTEGRATION_TEST = "integration_test"
    DEPLOY_PRODUCTION = "deploy_production"


@dataclass
class PipelineConfig:
    """CI/CD Pipeline configuration."""
    name: str
    repo: str
    branch_patterns: List[str] = field(default_factory=lambda: ["main", "develop"])
    environments: List[str] = field(default_factory=lambda: ["staging", "production"])
    enable_cache: bool = True
    parallel_jobs: int = 4
    timeout_minutes: int = 30


class GitHubActionsGenerator:
    """Generate GitHub Actions workflow."""

    def __init__(self, config: PipelineConfig):
        self.config = config

    def generate_python_ci(self) -> str:
        """Generate Python CI workflow."""
        return f'''name: {self.config.name} CI/CD

on:
  push:
    branches: [{', '.join(self.config.branch_patterns)}]
  pull_request:
    branches: [{', '.join(self.config.branch_patterns)}]

env:
  PYTHON_VERSION: "3.11"
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{{{ github.repository }}}}

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: {self.config.timeout_minutes}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{{{ env.PYTHON_VERSION }}}}
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint with ruff
        run: |
          pip install ruff
          ruff check .

      - name: Type check with mypy
        run: |
          pip install mypy
          mypy . --ignore-missing-imports

      - name: Run tests
        run: |
          pytest tests/ -v --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          fail_ci_if_error: true

  security-scan:
    runs-on: ubuntu-latest
    needs: test

    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'

      - name: Run Bandit security linter
        run: |
          pip install bandit
          bandit -r . -ll

  build:
    runs-on: ubuntu-latest
    needs: [test, security-scan]
    if: github.event_name == 'push'

    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{{{ env.REGISTRY }}}}
          username: ${{{{ github.actor }}}}
          password: ${{{{ secrets.GITHUB_TOKEN }}}}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{{{ env.REGISTRY }}}}/${{{{ env.IMAGE_NAME }}}}
          tags: |
            type=sha
            type=ref,event=branch

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{{{ steps.meta.outputs.tags }}}}
          labels: ${{{{ steps.meta.outputs.labels }}}}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/develop'
    environment: staging

    steps:
      - name: Deploy to staging
        run: |
          echo "Deploying to staging..."
          # Add deployment commands

  deploy-production:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
      - name: Deploy to production
        run: |
          echo "Deploying to production..."
          # Add deployment commands
'''

    def generate_release_workflow(self) -> str:
        """Generate release workflow."""
        return f'''name: Release

on:
  release:
    types: [published]

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install build tools
        run: |
          pip install build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{{{ secrets.PYPI_TOKEN }}}}
        run: twine upload dist/*
'''


class GitLabCIGenerator:
    """Generate GitLab CI configuration."""

    def __init__(self, config: PipelineConfig):
        self.config = config

    def generate(self) -> str:
        """Generate .gitlab-ci.yml content."""
        return f'''stages:
  - test
  - build
  - deploy

variables:
  PYTHON_VERSION: "3.11"
  DOCKER_DRIVER: overlay2

default:
  image: python:$PYTHON_VERSION
  cache:
    paths:
      - .cache/pip
      - venv/

.test-template: &test-template
  stage: test
  before_script:
    - python -m venv venv
    - source venv/bin/activate
    - pip install --upgrade pip
    - pip install -r requirements.txt -r requirements-dev.txt

test:
  <<: *test-template
  script:
    - pytest tests/ -v --cov=. --cov-report=xml
  coverage: '/TOTAL.*\\s+(\\d+%)/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

lint:
  <<: *test-template
  script:
    - pip install ruff
    - ruff check .

security:
  stage: test
  image: python:$PYTHON_VERSION
  script:
    - pip install bandit safety
    - bandit -r . -ll
    - safety check

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  only:
    - main
    - develop

deploy-staging:
  stage: deploy
  script:
    - echo "Deploying to staging"
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - develop

deploy-production:
  stage: deploy
  script:
    - echo "Deploying to production"
  environment:
    name: production
    url: https://example.com
  when: manual
  only:
    - main
'''


@dataclass
class QualityGate:
    """Quality gate definition."""
    name: str
    metric: str
    operator: str  # >, <, >=, <=, ==
    threshold: float
    blocking: bool = True


class QualityGateChecker:
    """Check quality gates."""

    def __init__(self):
        self.gates: List[QualityGate] = []

    def add_gate(self, gate: QualityGate) -> "QualityGateChecker":
        """Add a quality gate."""
        self.gates.append(gate)
        return self

    def check(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Check all quality gates."""
        results = []
        all_passed = True

        for gate in self.gates:
            value = metrics.get(gate.metric)
            if value is None:
                results.append({
                    "gate": gate.name,
                    "status": "skipped",
                    "reason": f"Metric {gate.metric} not found"
                })
                continue

            passed = self._evaluate(value, gate.operator, gate.threshold)

            if not passed and gate.blocking:
                all_passed = False

            results.append({
                "gate": gate.name,
                "metric": gate.metric,
                "value": value,
                "threshold": gate.threshold,
                "operator": gate.operator,
                "passed": passed,
                "blocking": gate.blocking
            })

        return {
            "passed": all_passed,
            "gates": results
        }

    def _evaluate(self, value: float, operator: str, threshold: float) -> bool:
        """Evaluate a single gate."""
        if operator == ">":
            return value > threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<":
            return value < threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "==":
            return value == threshold
        return False


def create_standard_quality_gates() -> QualityGateChecker:
    """Create standard quality gates for trading system."""
    checker = QualityGateChecker()

    checker.add_gate(QualityGate(
        name="Code Coverage",
        metric="coverage_percent",
        operator=">=",
        threshold=80,
        blocking=True
    ))

    checker.add_gate(QualityGate(
        name="Test Pass Rate",
        metric="test_pass_rate",
        operator=">=",
        threshold=100,
        blocking=True
    ))

    checker.add_gate(QualityGate(
        name="Security Issues",
        metric="security_issues_high",
        operator="==",
        threshold=0,
        blocking=True
    ))

    checker.add_gate(QualityGate(
        name="Code Duplication",
        metric="duplication_percent",
        operator="<",
        threshold=5,
        blocking=False
    ))

    checker.add_gate(QualityGate(
        name="Complexity",
        metric="avg_complexity",
        operator="<",
        threshold=10,
        blocking=False
    ))

    return checker


# Example usage
if __name__ == "__main__":
    # Generate GitHub Actions
    config = PipelineConfig(
        name="Trading System",
        repo="fokha/trading-system",
        branch_patterns=["main", "develop"],
        environments=["staging", "production"]
    )

    github_gen = GitHubActionsGenerator(config)
    print("GitHub Actions Workflow:")
    print("=" * 50)
    print(github_gen.generate_python_ci())

    # Check quality gates
    print("\n\nQuality Gate Check:")
    print("=" * 50)
    checker = create_standard_quality_gates()
    metrics = {
        "coverage_percent": 85,
        "test_pass_rate": 100,
        "security_issues_high": 0,
        "duplication_percent": 3,
        "avg_complexity": 8
    }
    result = checker.check(metrics)
    print(f"Overall: {'PASSED' if result['passed'] else 'FAILED'}")
    for gate in result['gates']:
        status = "✓" if gate.get('passed') else "✗"
        print(f"  {status} {gate['gate']}: {gate.get('value', 'N/A')}")
