# Integration Skills

**Extracted from:** Fokha Trading System (multi-system architecture)

---

## Patterns in This Directory

| # | Pattern | Template | Purpose |
|---|---------|----------|---------|
| 1 | WebSocket Server | `websocket_server.py` | Real-time price streaming |
| 2 | WebSocket Client | `websocket_client.dart` | Flutter WebSocket client |
| 3 | File Bridge | `file_bridge.py` | Cross-process communication |
| 4 | Signal Queue | `signal_queue.py` | Signal deduplication |
| 5 | API Client | `api_client.dart` | REST API client with retry |
| 6 | Health Monitor | `health_monitor.py` | Multi-service health checks |
| 7 | Sync Service | `sync_service.py` | Data synchronization |
| 8 | Dedup Cache | `dedup_cache.py` | Message deduplication |

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 CROSS-SYSTEM INTEGRATION                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────┐  REST   ┌──────────┐  WebSocket ┌──────────┐│
│   │  Flutter │ ◄─────► │  Python  │ ◄────────► │   N8N    ││
│   │   App    │         │   API    │            │ Workflows││
│   └──────────┘         └──────────┘            └──────────┘│
│        │                    │                       │       │
│        │                    │ File Bridge           │       │
│        │                    ▼                       │       │
│        │              ┌──────────┐                  │       │
│        └──────────────│   MQL5   │──────────────────┘       │
│                       │    EA    │                          │
│                       └──────────┘                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Communication Methods

| Method | Use Case | Latency | Reliability |
|--------|----------|---------|-------------|
| REST API | CRUD operations | 50-200ms | High |
| WebSocket | Real-time data | <50ms | Medium |
| File Bridge | Cross-process | 100-500ms | High |
| Message Queue | Async tasks | Variable | Very High |

---

## Signal Flow Pattern

```
1. Signal Generated (Python ML)
        │
        ▼
2. Signal Queued (dedup check)
        │
        ├──► 3a. WebSocket → Flutter (display)
        │
        ├──► 3b. File Bridge → MQL5 (execute)
        │
        └──► 3c. Webhook → N8N → Telegram (notify)
```

---

## Deduplication Strategy

Prevent duplicate signals across multiple systems:

```python
# Signal deduplication key
dedup_key = f"{symbol}_{direction}_{timestamp_minute}"

# TTL by type
DEDUP_TTL = {
    'signal': 300,      # 5 minutes
    'notification': 60, # 1 minute
    'webhook': 30       # 30 seconds
}
```

---

## Best Practices

### 1. Idempotent Operations
Design endpoints to handle duplicate requests safely.

### 2. Health Checks
Monitor all integrated services continuously.

### 3. Graceful Degradation
Continue operation when some services are down.

### 4. Retry with Backoff
Use exponential backoff for failed requests.

### 5. Circuit Breaker
Stop calling failing services temporarily.

---

## Dependencies

```txt
websockets>=10.0
aiohttp>=3.8
redis>=4.0 (optional)
python-socketio>=5.0
```
