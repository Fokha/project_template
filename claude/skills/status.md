# System Status Check

Check the status of all system components.

## Check Commands

```bash
# {{SERVICE_1}} Health
curl -s http://localhost:{{PORT_1}}/health | jq .

# {{SERVICE_2}} Health
curl -s http://localhost:{{PORT_2}}/health

# Git status
git status --short

# Current version
cat VERSION
```

## Expected Output

- {{SERVICE_1}}: `{"status": "healthy"}`
- {{SERVICE_2}}: `{"status": "ok"}`

## Quick Status Report Format

```
STATUS REPORT - [Date/Time]
━━━━━━━━━━━━━━━━━━━━━━━━━━━

SYSTEMS:
├── {{SERVICE_1}}:  [🟢/🔴]
├── {{SERVICE_2}}:  [🟢/🔴]
└── Git:            [clean/dirty]

VERSION: vX.X.X
```

## Troubleshooting

If service is down:
```bash
# Start services
./scripts/dev-start.sh

# Check logs
{{VIEW_LOGS_CMD}}
```
