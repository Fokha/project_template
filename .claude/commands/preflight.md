# Agent Preflight Check

Run the preflight check to verify implementation status and sync with KB API.

```bash
./scripts/agent-preflight.sh
```

After running, review the output and:
1. Note any in-progress tasks from KB
2. Check which files are ✅ DONE vs ❌ MISSING
3. Follow the current focus from KB

If KB API is offline, start it with:
```bash
cd python_ml && python api_server.py
```
