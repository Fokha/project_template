# Debugging

Tools and techniques for debugging issues.

## Quick Diagnostics

```bash
# Check service health
curl -s http://localhost:{{PORT}}/health | jq .

# Check logs
{{VIEW_LOGS_CMD}}

# Check running processes
ps aux | grep {{PROCESS_NAME}}

# Check port usage
lsof -i :{{PORT}}
```

## Log Locations

| Component | Log Location |
|-----------|--------------|
| {{SERVICE_1}} | `{{LOG_PATH_1}}` |
| {{SERVICE_2}} | `{{LOG_PATH_2}}` |
| Application | `{{APP_LOG_PATH}}` |

## Common Issues

### Issue: Service Not Starting

**Symptoms:** Service fails to start, port already in use

**Solution:**
```bash
# Find process using port
lsof -i :{{PORT}}

# Kill process
kill -9 <PID>

# Restart service
{{START_CMD}}
```

### Issue: Database Connection Failed

**Symptoms:** Connection refused, timeout errors

**Solution:**
```bash
# Check database is running
{{DB_CHECK_CMD}}

# Test connection
{{DB_TEST_CMD}}

# Restart database
{{DB_RESTART_CMD}}
```

### Issue: API Returning Errors

**Symptoms:** 500 errors, unexpected responses

**Solution:**
```bash
# Check API logs
{{VIEW_LOGS_CMD}}

# Test endpoint directly
curl -v http://localhost:{{PORT}}/{{ENDPOINT}}

# Check environment variables
env | grep {{ENV_PREFIX}}
```

## Debug Mode

Enable verbose logging:

```bash
# Set debug environment
export DEBUG=true
export LOG_LEVEL=debug

# Restart service
{{RESTART_CMD}}
```

## Profiling

```bash
# CPU profiling
{{PROFILE_CPU_CMD}}

# Memory profiling
{{PROFILE_MEMORY_CMD}}

# Request timing
time curl http://localhost:{{PORT}}/{{ENDPOINT}}
```

## Getting Help

1. Check logs first
2. Search existing issues: {{ISSUES_URL}}
3. Ask in team chat
4. Create detailed bug report with:
   - Steps to reproduce
   - Expected vs actual behavior
   - Relevant logs
   - Environment details
