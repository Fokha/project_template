# Machine Learning Skills

**Extracted from:** US_PY ML Engine v4.3.21 (8 models, 577 tests)

---

## Patterns in This Directory

| # | Pattern | Template | Purpose |
|---|---------|----------|---------|
| 1 | Model Training | `training_template.py` | Complete training pipeline |
| 2 | Feature Engineering | `feature_engineering_template.py` | Feature extraction |
| 3 | Model Serving | `model_serving_template.py` | Prediction endpoint |
| 4 | Ensemble Methods | `ensemble_template.py` | XGBoost + LightGBM |
| 5 | Walk-Forward Validation | `walkforward_template.py` | Time-series validation |
| 6 | Hyperparameter Tuning | `hyperparameter_template.py` | Grid/Random search |
| 7 | Model Persistence | `persistence_template.py` | Save/load models |
| 8 | Confidence Calibration | `calibration_template.py` | Confidence scoring |
| 9 | Multi-Timeframe | `mtf_template.py` | Multi-timeframe analysis |
| 10 | Sentiment Analysis | `sentiment_template.py` | NLP for finance |
| 11 | Anomaly Detection | `anomaly_template.py` | Isolation Forest |
| 12 | Scheduled Retraining | `retrain_template.py` | Automated updates |

---

## ML Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ML PIPELINE PATTERN                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Raw Data → Feature Engineering → Training → Validation     │
│                                        │                     │
│                                        ▼                     │
│                                   Model File (.pkl)          │
│                                        │                     │
│                                        ▼                     │
│                               Model Serving API              │
│                                        │                     │
│                                        ▼                     │
│                                   Predictions                │
│                                        │                     │
│                                        ▼                     │
│                               Feedback → Retrain             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Model Accuracy Targets

| Asset Class | Target Accuracy | Notes |
|-------------|-----------------|-------|
| Metals (XAUUSD) | 80-90% | Most predictable |
| Indices (US30) | 65-75% | Session-dependent |
| Forex | 60-70% | High noise |
| Crypto | 50-65% | Very volatile |

---

## Key Techniques

### 1. Ensemble Learning
Combine XGBoost + LightGBM for robust predictions:
```python
ensemble_prediction = (xgb_pred * 0.5) + (lgb_pred * 0.5)
```

### 2. Walk-Forward Validation
Never train on future data:
```python
for train_end in date_range:
    train_data = data[data.date <= train_end]
    test_data = data[data.date > train_end][:test_window]
```

### 3. Feature Importance
Always track which features matter:
```python
importance = model.feature_importances_
top_features = sorted(zip(features, importance), key=lambda x: x[1], reverse=True)
```

---

## Dependencies

```txt
scikit-learn>=1.0.0
xgboost>=1.7.0
lightgbm>=3.3.0
pandas>=1.5.0
numpy>=1.23.0
joblib>=1.2.0
```
