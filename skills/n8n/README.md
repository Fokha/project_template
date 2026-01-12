# N8N Workflow Skills

**Extracted from:** Fokha Trading System (45 workflows, active-active architecture)

---

## Patterns in This Directory

| # | Pattern | Template | Purpose |
|---|---------|----------|---------|
| 1 | Cron Workflow | `cron_workflow.json` | Scheduled automation |
| 2 | Webhook Handler | `webhook_handler.json` | HTTP endpoint handler |
| 3 | API Poller | `api_poller.json` | Periodic API calls |
| 4 | Notification Hub | `notification_hub.json` | Multi-channel alerts |
| 5 | Error Handler | `error_handler.json` | Retry and escalation |
| 6 | Data Pipeline | `data_pipeline.json` | ETL workflow |

---

## N8N Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                   N8N WORKFLOW PATTERN                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌────────────┐     ┌────────────┐     ┌────────────┐     │
│   │  TRIGGER   │ ──► │  PROCESS   │ ──► │   OUTPUT   │     │
│   │            │     │            │     │            │     │
│   │ • Cron     │     │ • HTTP     │     │ • Telegram │     │
│   │ • Webhook  │     │ • Code     │     │ • Email    │     │
│   │ • Manual   │     │ • Switch   │     │ • Webhook  │     │
│   │ • Other WF │     │ • Set      │     │ • DB Write │     │
│   └────────────┘     └────────────┘     └────────────┘     │
│                            │                                 │
│                            ▼                                 │
│                     ┌────────────┐                          │
│                     │   ERROR    │                          │
│                     │  HANDLER   │                          │
│                     └────────────┘                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Best Practices

### 1. Always Add Error Handling
Use "On Error" option → Continue with error output.

### 2. Use Environment Variables
Store secrets in N8N credentials, not workflow.

### 3. Add Rate Limiting
Prevent API abuse with Wait nodes.

### 4. Use Sub-Workflows
Break complex flows into reusable pieces.

### 5. Log Important Events
Send logs to external system for debugging.

---

## Workflow Naming Convention

```
{project}_{function}_{version}.json

Examples:
- fokha_ml_predictions_v2.json
- fokha_telegram_commands_v1.json
- fokha_daily_report_v1.json
```

---

## Common Node Patterns

### HTTP Request Pattern
```json
{
  "method": "POST",
  "url": "={{$env.API_URL}}/endpoint",
  "authentication": "genericCredentialType",
  "options": {
    "timeout": 30000
  }
}
```

### Telegram Send Pattern
```json
{
  "chatId": "={{$env.TELEGRAM_CHAT_ID}}",
  "text": "={{$node.previous.json.message}}",
  "parseMode": "Markdown"
}
```

### Cron Schedule Pattern
```json
{
  "rule": {
    "interval": [{"field": "minutes", "minutesInterval": 15}]
  }
}
```

---

## Active-Active Architecture

Run N8N on multiple instances with deduplication:

```
┌─────────────┐         ┌─────────────┐
│  LOCAL N8N  │ ───┬─── │  CLOUD N8N  │
│ localhost   │    │    │ cloud:5678  │
└─────────────┘    │    └─────────────┘
                   │
                   ▼
           ┌─────────────┐
           │ DEDUP CACHE │
           │  (SQLite)   │
           └─────────────┘
```

Both instances run simultaneously. API-level deduplication prevents duplicate notifications.
