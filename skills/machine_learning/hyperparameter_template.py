# ═══════════════════════════════════════════════════════════════
# HYPERPARAMETER TUNING TEMPLATE
# Grid search, random search, and Bayesian optimization
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Define parameter search space
# 3. Run optimization
#
# ═══════════════════════════════════════════════════════════════

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json
from pathlib import Path
from itertools import product

from sklearn.model_selection import cross_val_score, TimeSeriesSplit
from sklearn.metrics import accuracy_score, f1_score, make_scorer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════


@dataclass
class ParamSpace:
    """Define parameter search space."""
    name: str
    values: List[Any] = None          # For grid search
    low: float = None                  # For random/Bayesian
    high: float = None
    log_scale: bool = False
    param_type: str = "float"         # float, int, categorical

    def sample(self) -> Any:
        """Sample a random value from the space."""
        if self.values:
            return np.random.choice(self.values)
        elif self.log_scale:
            return np.exp(np.random.uniform(np.log(self.low), np.log(self.high)))
        elif self.param_type == "int":
            return np.random.randint(self.low, self.high + 1)
        else:
            return np.random.uniform(self.low, self.high)


@dataclass
class TuningResult:
    """Result of hyperparameter tuning."""
    best_params: Dict[str, Any]
    best_score: float
    all_results: List[Dict]
    search_method: str
    n_iterations: int
    total_time: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════
# HYPERPARAMETER TUNER
# ═══════════════════════════════════════════════════════════════


class HyperparameterTuner:
    """
    Hyperparameter optimization for ML models.

    Supports:
    - Grid Search (exhaustive)
    - Random Search (faster)
    - Custom optimization strategies
    """

    def __init__(
        self,
        model_factory: Callable,
        param_spaces: List[ParamSpace],
        scoring: str = "accuracy",
        cv: int = 5,
        n_jobs: int = -1
    ):
        """
        Initialize tuner.

        Args:
            model_factory: Function that creates model with given params
            param_spaces: List of ParamSpace definitions
            scoring: Scoring metric ('accuracy', 'f1', 'roc_auc')
            cv: Cross-validation folds
            n_jobs: Parallel jobs (-1 for all cores)
        """
        self.model_factory = model_factory
        self.param_spaces = {p.name: p for p in param_spaces}
        self.scoring = scoring
        self.cv = cv
        self.n_jobs = n_jobs
        self.results: List[Dict] = []

    def grid_search(
        self,
        X: np.ndarray,
        y: np.ndarray,
        time_series: bool = False
    ) -> TuningResult:
        """
        Exhaustive grid search over all parameter combinations.

        Args:
            X: Feature matrix
            y: Target vector
            time_series: Use TimeSeriesSplit for CV
        """
        start_time = datetime.now()
        logger.info("Starting Grid Search")

        # Generate all combinations
        param_names = list(self.param_spaces.keys())
        param_values = [self.param_spaces[name].values for name in param_names]
        combinations = list(product(*param_values))

        logger.info(f"Total combinations: {len(combinations)}")

        # Evaluate each combination
        self.results = []
        best_score = -np.inf
        best_params = None

        cv_splitter = TimeSeriesSplit(n_splits=self.cv) if time_series else self.cv

        for i, combo in enumerate(combinations):
            params = dict(zip(param_names, combo))

            try:
                score = self._evaluate_params(X, y, params, cv_splitter)
                self.results.append({'params': params, 'score': score})

                if score > best_score:
                    best_score = score
                    best_params = params

                if (i + 1) % 10 == 0:
                    logger.info(f"Progress: {i + 1}/{len(combinations)}, Best: {best_score:.4f}")

            except Exception as e:
                logger.warning(f"Failed for params {params}: {e}")

        total_time = (datetime.now() - start_time).total_seconds()

        return TuningResult(
            best_params=best_params,
            best_score=best_score,
            all_results=self.results,
            search_method="grid_search",
            n_iterations=len(combinations),
            total_time=total_time,
        )

    def random_search(
        self,
        X: np.ndarray,
        y: np.ndarray,
        n_iter: int = 100,
        time_series: bool = False
    ) -> TuningResult:
        """
        Random search over parameter space.

        More efficient than grid search for large spaces.
        """
        start_time = datetime.now()
        logger.info(f"Starting Random Search ({n_iter} iterations)")

        self.results = []
        best_score = -np.inf
        best_params = None

        cv_splitter = TimeSeriesSplit(n_splits=self.cv) if time_series else self.cv

        for i in range(n_iter):
            # Sample random params
            params = {name: space.sample() for name, space in self.param_spaces.items()}

            try:
                score = self._evaluate_params(X, y, params, cv_splitter)
                self.results.append({'params': params, 'score': score})

                if score > best_score:
                    best_score = score
                    best_params = params
                    logger.info(f"New best at iter {i + 1}: {best_score:.4f}")

            except Exception as e:
                logger.warning(f"Failed for params {params}: {e}")

            if (i + 1) % 20 == 0:
                logger.info(f"Progress: {i + 1}/{n_iter}")

        total_time = (datetime.now() - start_time).total_seconds()

        return TuningResult(
            best_params=best_params,
            best_score=best_score,
            all_results=self.results,
            search_method="random_search",
            n_iterations=n_iter,
            total_time=total_time,
        )

    def early_stopping_search(
        self,
        X: np.ndarray,
        y: np.ndarray,
        n_iter: int = 100,
        patience: int = 20,
        time_series: bool = False
    ) -> TuningResult:
        """
        Random search with early stopping.

        Stops if no improvement for 'patience' iterations.
        """
        start_time = datetime.now()
        logger.info(f"Starting Early Stopping Search (max {n_iter} iterations)")

        self.results = []
        best_score = -np.inf
        best_params = None
        no_improvement = 0

        cv_splitter = TimeSeriesSplit(n_splits=self.cv) if time_series else self.cv

        for i in range(n_iter):
            params = {name: space.sample() for name, space in self.param_spaces.items()}

            try:
                score = self._evaluate_params(X, y, params, cv_splitter)
                self.results.append({'params': params, 'score': score})

                if score > best_score:
                    best_score = score
                    best_params = params
                    no_improvement = 0
                    logger.info(f"New best at iter {i + 1}: {best_score:.4f}")
                else:
                    no_improvement += 1

                if no_improvement >= patience:
                    logger.info(f"Early stopping at iteration {i + 1}")
                    break

            except Exception as e:
                logger.warning(f"Failed for params {params}: {e}")

        total_time = (datetime.now() - start_time).total_seconds()

        return TuningResult(
            best_params=best_params,
            best_score=best_score,
            all_results=self.results,
            search_method="early_stopping_search",
            n_iterations=len(self.results),
            total_time=total_time,
        )

    def _evaluate_params(
        self,
        X: np.ndarray,
        y: np.ndarray,
        params: Dict,
        cv_splitter
    ) -> float:
        """Evaluate a single parameter combination."""
        # Create model with params
        model = self.model_factory(**params)

        # Cross-validate
        scores = cross_val_score(
            model, X, y,
            cv=cv_splitter,
            scoring=self.scoring,
            n_jobs=self.n_jobs
        )

        return scores.mean()

    def get_top_n(self, n: int = 10) -> List[Dict]:
        """Get top N parameter combinations."""
        sorted_results = sorted(self.results, key=lambda x: x['score'], reverse=True)
        return sorted_results[:n]

    def save_results(self, path: str):
        """Save results to JSON file."""
        output = {
            'results': self.results,
            'timestamp': datetime.now().isoformat(),
        }

        # Convert numpy types for JSON serialization
        def convert(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj

        with open(path, 'w') as f:
            json.dump(output, f, default=convert, indent=2)

        logger.info(f"Results saved to {path}")


# ═══════════════════════════════════════════════════════════════
# COMMON PARAMETER SPACES
# ═══════════════════════════════════════════════════════════════


def get_xgboost_param_space() -> List[ParamSpace]:
    """Common XGBoost parameter space."""
    return [
        ParamSpace("n_estimators", values=[50, 100, 200, 300]),
        ParamSpace("max_depth", values=[3, 4, 5, 6, 7, 8]),
        ParamSpace("learning_rate", values=[0.01, 0.05, 0.1, 0.2]),
        ParamSpace("subsample", values=[0.6, 0.7, 0.8, 0.9, 1.0]),
        ParamSpace("colsample_bytree", values=[0.6, 0.7, 0.8, 0.9, 1.0]),
        ParamSpace("min_child_weight", values=[1, 3, 5, 7]),
    ]


def get_lightgbm_param_space() -> List[ParamSpace]:
    """Common LightGBM parameter space."""
    return [
        ParamSpace("n_estimators", values=[50, 100, 200, 300]),
        ParamSpace("max_depth", values=[3, 5, 7, 9, -1]),
        ParamSpace("learning_rate", values=[0.01, 0.05, 0.1, 0.2]),
        ParamSpace("num_leaves", values=[15, 31, 63, 127]),
        ParamSpace("subsample", values=[0.6, 0.7, 0.8, 0.9, 1.0]),
        ParamSpace("colsample_bytree", values=[0.6, 0.7, 0.8, 0.9, 1.0]),
    ]


def get_random_forest_param_space() -> List[ParamSpace]:
    """Common Random Forest parameter space."""
    return [
        ParamSpace("n_estimators", values=[50, 100, 200, 300]),
        ParamSpace("max_depth", values=[5, 10, 15, 20, None]),
        ParamSpace("min_samples_split", values=[2, 5, 10]),
        ParamSpace("min_samples_leaf", values=[1, 2, 4]),
        ParamSpace("max_features", values=['sqrt', 'log2', None]),
    ]


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification

    # Create sample data
    X, y = make_classification(
        n_samples=1000,
        n_features=20,
        n_informative=10,
        n_redundant=5,
        random_state=42
    )

    # Define model factory
    def create_rf(**params):
        return RandomForestClassifier(random_state=42, **params)

    # Define parameter space
    param_spaces = [
        ParamSpace("n_estimators", values=[50, 100, 200]),
        ParamSpace("max_depth", values=[5, 10, 15]),
        ParamSpace("min_samples_split", values=[2, 5, 10]),
    ]

    # Create tuner
    tuner = HyperparameterTuner(
        model_factory=create_rf,
        param_spaces=param_spaces,
        scoring="accuracy",
        cv=5,
    )

    # Run random search (faster for demo)
    result = tuner.random_search(X, y, n_iter=30)

    # Print results
    print(f"\n{'='*60}")
    print("HYPERPARAMETER TUNING RESULTS")
    print(f"{'='*60}")
    print(f"Search Method: {result.search_method}")
    print(f"Iterations: {result.n_iterations}")
    print(f"Time: {result.total_time:.2f}s")
    print(f"\nBest Score: {result.best_score:.4f}")
    print(f"Best Params: {result.best_params}")

    print(f"\nTop 5 Configurations:")
    for i, r in enumerate(tuner.get_top_n(5)):
        print(f"  {i + 1}. Score: {r['score']:.4f} | {r['params']}")
