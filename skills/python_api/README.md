# Python API Skills

**Extracted from:** US_PY Engine v4.3.21 (17,963 lines, 242+ endpoints)

---

## Patterns in This Directory

| Pattern | Template | Purpose |
|---------|----------|---------|
| Flask Blueprint | `blueprint_template.py` | Modular API organization |
| Endpoint Pattern | `endpoint_template.py` | Standard request/response |
| Error Handler | `error_handler_template.py` | Consistent error responses |
| Database Operations | `database_template.py` | SQLite CRUD |
| Background Tasks | `background_task_template.py` | Async execution |
| Caching | `cache_template.py` | Response caching |
| Validation | `validation_template.py` | Input validation |
| Logging | `logging_template.py` | Structured logging |
| Health Check | `health_check_template.py` | Service monitoring |
| Deduplication | `dedup_template.py` | Prevent duplicates |

---

## Standard Response Format

**All endpoints must return:**

```python
# Success
{
    "success": True,
    "data": {...},
    "error": None,
    "timestamp": "2026-01-11T10:00:00Z"
}

# Error
{
    "success": False,
    "data": None,
    "error": "Error message here",
    "timestamp": "2026-01-11T10:00:00Z"
}
```

---

## Quick Start

```bash
# Copy blueprint template
cp blueprint_template.py ~/my_project/api/my_feature.py

# Replace placeholders
sed -i 's/{{FEATURE_NAME}}/my_feature/g' ~/my_project/api/my_feature.py

# Register in main app
# app.register_blueprint(my_feature_bp)
```

---

## Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    FLASK API ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   api_server.py (main)                                       │
│         │                                                    │
│         ├── blueprints/                                      │
│         │   ├── kb_api.py (Knowledge Base)                   │
│         │   ├── ml_api.py (Machine Learning)                 │
│         │   ├── trading_api.py (Trading)                     │
│         │   └── ...                                          │
│         │                                                    │
│         ├── services/                                        │
│         │   ├── signal_service.py                            │
│         │   ├── backtest_service.py                          │
│         │   └── ...                                          │
│         │                                                    │
│         ├── models/                                          │
│         │   ├── signal_model.pkl                             │
│         │   └── ...                                          │
│         │                                                    │
│         └── database/                                        │
│             └── trading.db                                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Placeholder Reference

| Placeholder | Replace With |
|-------------|--------------|
| `{{FEATURE_NAME}}` | Feature name (lowercase) |
| `{{DB_PATH}}` | Database file path |
| `{{PORT}}` | API port (default: 5050) |
| `{{LOG_PATH}}` | Log file path |
