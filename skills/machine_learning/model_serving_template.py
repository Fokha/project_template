# ═══════════════════════════════════════════════════════════════
# MODEL SERVING TEMPLATE
# Serve ML predictions via Flask API
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Update model path
# 3. Run: python model_serving_template.py
#
# ═══════════════════════════════════════════════════════════════

from flask import Flask, request, jsonify
from datetime import datetime
from typing import Dict, Any, Optional, List
import numpy as np
import pandas as pd
import joblib
import logging
from pathlib import Path
from functools import lru_cache
import threading
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# MODEL MANAGER
# ═══════════════════════════════════════════════════════════════


class ModelManager:
    """
    Manages loading and serving ML models.

    Features:
    - Lazy loading
    - Model caching
    - Hot reloading
    - Health monitoring
    """

    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.models: Dict[str, Dict] = {}
        self.load_times: Dict[str, datetime] = {}
        self._lock = threading.Lock()

    def load_model(self, model_name: str) -> Dict:
        """Load a model by name."""
        with self._lock:
            if model_name in self.models:
                return self.models[model_name]

            model_path = self.model_dir / f"{model_name}.pkl"

            if not model_path.exists():
                raise FileNotFoundError(f"Model not found: {model_path}")

            logger.info(f"Loading model: {model_name}")
            data = joblib.load(model_path)

            self.models[model_name] = data
            self.load_times[model_name] = datetime.now()

            return data

    def get_model(self, model_name: str):
        """Get a loaded model."""
        if model_name not in self.models:
            self.load_model(model_name)
        return self.models[model_name]

    def reload_model(self, model_name: str) -> bool:
        """Reload a model from disk."""
        with self._lock:
            if model_name in self.models:
                del self.models[model_name]
            self.load_model(model_name)
            return True

    def list_models(self) -> List[str]:
        """List available models."""
        return [p.stem for p in self.model_dir.glob("*.pkl")]

    def get_model_info(self, model_name: str) -> Dict:
        """Get model metadata."""
        model_data = self.get_model(model_name)
        return {
            'name': model_name,
            'loaded_at': self.load_times.get(model_name, datetime.now()).isoformat(),
            'features': model_data.get('feature_columns', []),
            'config': str(model_data.get('config', {})),
        }


# ═══════════════════════════════════════════════════════════════
# PREDICTION SERVICE
# ═══════════════════════════════════════════════════════════════


class PredictionService:
    """
    Handle prediction requests.
    """

    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager

    def predict(
        self,
        model_name: str,
        features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make a prediction.

        Args:
            model_name: Name of the model to use
            features: Dictionary of feature values

        Returns:
            Prediction result with confidence
        """
        start_time = time.time()

        try:
            # Get model
            model_data = self.model_manager.get_model(model_name)
            model = model_data['model']
            scaler = model_data['scaler']
            feature_columns = model_data['feature_columns']

            # Prepare input
            X = self._prepare_input(features, feature_columns, scaler)

            # Predict
            prediction = model.predict(X)[0]

            # Get probabilities if available
            confidence = None
            probabilities = None
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(X)[0]
                confidence = float(max(proba))
                probabilities = {str(i): float(p) for i, p in enumerate(proba)}

            inference_time = time.time() - start_time

            return {
                'success': True,
                'prediction': int(prediction) if isinstance(prediction, (np.integer, np.int64)) else prediction,
                'confidence': confidence,
                'probabilities': probabilities,
                'model': model_name,
                'inference_time_ms': round(inference_time * 1000, 2),
            }

        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                'success': False,
                'error': str(e),
                'model': model_name,
            }

    def _prepare_input(
        self,
        features: Dict[str, Any],
        feature_columns: List[str],
        scaler
    ) -> np.ndarray:
        """Prepare input features for prediction."""
        # Create feature array in correct order
        X = np.array([[features.get(col, 0) for col in feature_columns]])

        # Scale
        X = scaler.transform(X)

        return X

    def batch_predict(
        self,
        model_name: str,
        data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Make batch predictions."""
        return [self.predict(model_name, row) for row in data]


# ═══════════════════════════════════════════════════════════════
# FLASK API
# ═══════════════════════════════════════════════════════════════


app = Flask(__name__)
model_manager = ModelManager()
prediction_service = PredictionService(model_manager)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'models_loaded': len(model_manager.models),
    })


@app.route('/models', methods=['GET'])
def list_models():
    """List available models."""
    try:
        models = model_manager.list_models()
        return jsonify({
            'success': True,
            'models': models,
            'count': len(models),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/models/<model_name>', methods=['GET'])
def get_model_info(model_name: str):
    """Get model information."""
    try:
        info = model_manager.get_model_info(model_name)
        return jsonify({'success': True, 'data': info})
    except FileNotFoundError:
        return jsonify({'success': False, 'error': 'Model not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/predict/<model_name>', methods=['POST'])
def predict(model_name: str):
    """
    Make a prediction.

    POST /predict/<model_name>

    Request Body:
    {
        "features": {
            "feature1": 0.5,
            "feature2": 1.2,
            ...
        }
    }

    Response:
    {
        "success": true,
        "prediction": 1,
        "confidence": 0.85,
        "probabilities": {"0": 0.15, "1": 0.85}
    }
    """
    try:
        data = request.get_json()
        if not data or 'features' not in data:
            return jsonify({
                'success': False,
                'error': 'Request must include "features" object'
            }), 400

        result = prediction_service.predict(model_name, data['features'])

        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Prediction endpoint error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/predict/<model_name>/batch', methods=['POST'])
def batch_predict(model_name: str):
    """
    Make batch predictions.

    POST /predict/<model_name>/batch

    Request Body:
    {
        "data": [
            {"feature1": 0.5, "feature2": 1.2},
            {"feature1": 0.8, "feature2": 0.9}
        ]
    }
    """
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({
                'success': False,
                'error': 'Request must include "data" array'
            }), 400

        results = prediction_service.batch_predict(model_name, data['data'])

        return jsonify({
            'success': True,
            'predictions': results,
            'count': len(results),
        })

    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/models/<model_name>/reload', methods=['POST'])
def reload_model(model_name: str):
    """Reload a model from disk."""
    try:
        model_manager.reload_model(model_name)
        return jsonify({
            'success': True,
            'message': f'Model {model_name} reloaded',
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='ML Model Serving API')
    parser.add_argument('--port', type=int, default=5050, help='Port to run on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--model-dir', default='models', help='Model directory')
    parser.add_argument('--preload', nargs='+', help='Models to preload')

    args = parser.parse_args()

    # Update model directory
    model_manager.model_dir = Path(args.model_dir)

    # Preload models if specified
    if args.preload:
        for model in args.preload:
            try:
                model_manager.load_model(model)
                logger.info(f"Preloaded: {model}")
            except Exception as e:
                logger.warning(f"Failed to preload {model}: {e}")

    # Run server
    logger.info(f"Starting ML serving API on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=False)
