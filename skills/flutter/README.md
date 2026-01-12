# Flutter Skills

**Extracted from:** AI Studio Pro v2.3.7 (221 Dart files)

---

## Patterns in This Directory

| Pattern | Template | Purpose |
|---------|----------|---------|
| Provider | `provider_template.dart` | State management |
| Service | `service_template.dart` | Business logic |
| Model | `model_template.dart` | Data structures |
| API Client | `api_client_template.dart` | HTTP operations |
| WebSocket Client | `websocket_client_template.dart` | Real-time data |
| Widget Composition | `widget_composition_template.dart` | Reusable UI |
| Theme Constants | `theme_constants_template.dart` | Design system |
| Plugin Architecture | `plugin_template.dart` | Extensibility |
| **OAuth Authentication** | `oauth_template.dart` | Google/Apple/Microsoft/Email auth |

---

## Quick Start

```bash
# Copy a template
cp provider_template.dart ~/my_project/lib/providers/feature_provider.dart

# Replace placeholders
sed -i 's/{{FEATURE_NAME}}/MyFeature/g' ~/my_project/lib/providers/feature_provider.dart
```

---

## Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUTTER ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Widgets (UI) ──uses──► Providers (State)                   │
│        │                       │                             │
│        │                       ▼                             │
│        │               Services (Logic)                      │
│        │                       │                             │
│        │                       ▼                             │
│        │                Models (Data)                        │
│        │                       │                             │
│        └───────────────────────┼───► API Client              │
│                                │                             │
│                                ▼                             │
│                         External APIs                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Principles

1. **Providers** - Only state, no business logic
2. **Services** - All business logic, API calls
3. **Models** - Data only, JSON serialization
4. **Widgets** - UI only, read from providers
5. **Theme Constants** - All colors, fonts, spacing in ONE file

---

## Placeholder Reference

| Placeholder | Replace With |
|-------------|--------------|
| `{{FEATURE_NAME}}` | Feature name (e.g., Trading) |
| `{{MODEL_NAME}}` | Model name (e.g., Trade) |
| `{{API_BASE_URL}}` | API URL (e.g., http://localhost:5050) |
| `{{WS_URL}}` | WebSocket URL (e.g., ws://localhost:8765) |
