# Deployment

Deploy the application to different environments.

## Environments

| Environment | URL | Branch |
|-------------|-----|--------|
| Development | `localhost:{{PORT}}` | `develop` |
| Staging | `{{STAGING_URL}}` | `staging` |
| Production | `{{PROD_URL}}` | `main` |

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] CHANGELOG updated
- [ ] VERSION bumped
- [ ] No console.log/debug statements
- [ ] Environment variables configured
- [ ] Database migrations ready (if any)

## Deploy Commands

```bash
# Deploy to staging
{{DEPLOY_STAGING_CMD}}

# Deploy to production
{{DEPLOY_PROD_CMD}}

# Rollback if needed
{{ROLLBACK_CMD}}
```

## Docker Deployment

```bash
# Build image
docker build -t {{PROJECT_NAME}}:latest .

# Run container
docker run -d -p {{PORT}}:{{PORT}} {{PROJECT_NAME}}:latest

# Using docker-compose
docker-compose up -d

# View logs
docker-compose logs -f
```

## Health Check After Deploy

```bash
# Check staging
curl -s {{STAGING_URL}}/health | jq .

# Check production
curl -s {{PROD_URL}}/health | jq .
```

## Rollback Procedure

If issues are detected after deployment:

1. **Immediate**: Rollback to previous version
   ```bash
   {{ROLLBACK_CMD}}
   ```

2. **Verify**: Check health endpoints
   ```bash
   curl {{PROD_URL}}/health
   ```

3. **Investigate**: Check logs for errors
   ```bash
   {{VIEW_LOGS_CMD}}
   ```

4. **Fix**: Create hotfix branch and deploy

## Deployment Notifications

Notify team after deployment:
- Slack/Discord: #deployments
- Update status page if applicable
