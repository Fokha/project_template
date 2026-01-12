# {{PROJECT_NAME}} - Developer Guide

**Version:** {{VERSION}} | **Last Updated:** {{DATE}}

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Project Structure](#project-structure)
3. [Development Environment](#development-environment)
4. [Coding Standards](#coding-standards)
5. [Architecture Overview](#architecture-overview)
6. [API Reference](#api-reference)
7. [Database Schema](#database-schema)
8. [Testing Guide](#testing-guide)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)
11. [Contributing](#contributing)

---

## Quick Start

### Prerequisites

| Requirement | Version | Installation |
|-------------|---------|--------------|
| {{PREREQ_1}} | {{VERSION_1}} | `{{INSTALL_CMD_1}}` |
| {{PREREQ_2}} | {{VERSION_2}} | `{{INSTALL_CMD_2}}` |
| {{PREREQ_3}} | {{VERSION_3}} | `{{INSTALL_CMD_3}}` |

### Clone & Setup

```bash
# Clone repository
git clone {{REPO_URL}}
cd {{PROJECT_NAME}}

# Install dependencies
{{INSTALL_DEPS_CMD}}

# Copy environment config
cp .env.example .env

# Start development server
{{DEV_START_CMD}}
```

### Verify Installation

```bash
# Health check
curl http://localhost:{{PORT}}/health

# Run tests
{{TEST_CMD}}
```

---

## Project Structure

```
{{PROJECT_NAME}}/
├── {{FOLDER_1}}/                 # {{FOLDER_1_DESC}}
│   ├── {{SUBFOLDER_1A}}/         # {{SUBFOLDER_1A_DESC}}
│   ├── {{SUBFOLDER_1B}}/         # {{SUBFOLDER_1B_DESC}}
│   └── {{SUBFOLDER_1C}}/         # {{SUBFOLDER_1C_DESC}}
├── {{FOLDER_2}}/                 # {{FOLDER_2_DESC}}
│   ├── {{SUBFOLDER_2A}}/         # {{SUBFOLDER_2A_DESC}}
│   └── {{SUBFOLDER_2B}}/         # {{SUBFOLDER_2B_DESC}}
├── {{FOLDER_3}}/                 # {{FOLDER_3_DESC}}
├── docs/                         # Documentation
├── tests/                        # Test files
├── scripts/                      # Automation scripts
├── config/                       # Configuration files
├── .env.example                  # Environment template
├── {{CONFIG_FILE}}               # Project configuration
└── README.md                     # Project overview
```

### Key Files

| File | Purpose |
|------|---------|
| `{{MAIN_FILE}}` | Application entry point |
| `{{CONFIG_FILE}}` | Dependencies and project config |
| `.env` | Environment variables (not committed) |
| `{{BUILD_FILE}}` | Build configuration |

---

## Development Environment

### Using Dev Scripts

```bash
# Start all services
./scripts/dev-start.sh

# Stop all services
./scripts/dev-stop.sh

# View logs
./scripts/dev-logs.sh
```

### Service Ports

| Service | Port | URL |
|---------|------|-----|
| {{SERVICE_1}} | {{PORT_1}} | http://localhost:{{PORT_1}} |
| {{SERVICE_2}} | {{PORT_2}} | http://localhost:{{PORT_2}} |
| {{SERVICE_3}} | {{PORT_3}} | http://localhost:{{PORT_3}} |

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `{{ENV_1}}` | {{ENV_1_DESC}} | {{ENV_1_DEFAULT}} | Yes/No |
| `{{ENV_2}}` | {{ENV_2_DESC}} | {{ENV_2_DEFAULT}} | Yes/No |
| `{{ENV_3}}` | {{ENV_3_DESC}} | {{ENV_3_DEFAULT}} | Yes/No |

### IDE Setup

#### VS Code

Recommended extensions:
- {{EXTENSION_1}}
- {{EXTENSION_2}}
- {{EXTENSION_3}}

Settings (`.vscode/settings.json`):
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "{{FORMATTER}}",
  "{{SETTING_1}}": {{VALUE_1}},
  "{{SETTING_2}}": {{VALUE_2}}
}
```

---

## Coding Standards

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Files | {{FILE_CONVENTION}} | `{{FILE_EXAMPLE}}` |
| Classes | PascalCase | `UserService` |
| Functions | camelCase / snake_case | `getUserById` / `get_user_by_id` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Variables | camelCase / snake_case | `userName` / `user_name` |

### Code Style

#### {{LANGUAGE_1}} Style Guide

```{{LANG_1_EXT}}
// Good
{{GOOD_EXAMPLE_1}}

// Bad
{{BAD_EXAMPLE_1}}
```

#### {{LANGUAGE_2}} Style Guide

```{{LANG_2_EXT}}
# Good
{{GOOD_EXAMPLE_2}}

# Bad
{{BAD_EXAMPLE_2}}
```

### Commit Messages

Format: `type(scope): description`

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code restructuring |
| `test` | Adding tests |
| `chore` | Maintenance tasks |

Examples:
```
feat(auth): add OAuth2 login support
fix(api): handle null response in user endpoint
docs(readme): update installation instructions
```

### Code Review Checklist

- [ ] Code follows naming conventions
- [ ] Functions are small and focused
- [ ] No hardcoded values (use config/constants)
- [ ] Error handling is appropriate
- [ ] Tests cover new functionality
- [ ] Documentation is updated
- [ ] No console.log / print statements in production
- [ ] Security best practices followed

---

## Architecture Overview

### System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          {{PROJECT_NAME}}                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐   │
│   │   Client    │────────►│   API       │────────►│  Database   │   │
│   │  {{CLIENT}} │◄────────│  {{SERVER}} │◄────────│  {{DB}}     │   │
│   └─────────────┘         └──────┬──────┘         └─────────────┘   │
│                                  │                                  │
│                          ┌───────▼───────┐                          │
│                          │   Services    │                          │
│                          │  (Business    │                          │
│                          │   Logic)      │                          │
│                          └───────────────┘                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Responsibility | Key Files |
|-------|----------------|-----------|
| **Presentation** | UI, User interaction | `{{PRES_FILES}}` |
| **API** | HTTP handlers, routing | `{{API_FILES}}` |
| **Service** | Business logic | `{{SERVICE_FILES}}` |
| **Repository** | Data access | `{{REPO_FILES}}` |
| **Model** | Data structures | `{{MODEL_FILES}}` |

### Design Patterns Used

| Pattern | Where Used | Purpose |
|---------|------------|---------|
| {{PATTERN_1}} | {{WHERE_1}} | {{PURPOSE_1}} |
| {{PATTERN_2}} | {{WHERE_2}} | {{PURPOSE_2}} |
| {{PATTERN_3}} | {{WHERE_3}} | {{PURPOSE_3}} |

---

## API Reference

### Base URL

- Development: `http://localhost:{{PORT}}/api`
- Production: `https://{{PROD_DOMAIN}}/api`

### Authentication

```
Authorization: Bearer <token>
```

### Common Headers

| Header | Value | Required |
|--------|-------|----------|
| `Content-Type` | `application/json` | Yes |
| `Authorization` | `Bearer <token>` | Yes* |
| `X-Request-ID` | UUID | Optional |

### Endpoints

#### {{RESOURCE_1}} Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/{{RESOURCE_1}}` | List all | Yes |
| GET | `/{{RESOURCE_1}}/:id` | Get by ID | Yes |
| POST | `/{{RESOURCE_1}}` | Create new | Yes |
| PUT | `/{{RESOURCE_1}}/:id` | Update | Yes |
| DELETE | `/{{RESOURCE_1}}/:id` | Delete | Yes |

**Request Example:**
```json
POST /api/{{RESOURCE_1}}
{
  "{{FIELD_1}}": "{{VALUE_1}}",
  "{{FIELD_2}}": "{{VALUE_2}}"
}
```

**Response Example:**
```json
{
  "success": true,
  "data": {
    "id": "{{ID}}",
    "{{FIELD_1}}": "{{VALUE_1}}",
    "{{FIELD_2}}": "{{VALUE_2}}",
    "created_at": "2026-01-12T00:00:00Z"
  }
}
```

### Error Responses

| Code | Meaning | Response Body |
|------|---------|---------------|
| 400 | Bad Request | `{"error": "Validation failed", "details": [...]}` |
| 401 | Unauthorized | `{"error": "Invalid or missing token"}` |
| 403 | Forbidden | `{"error": "Insufficient permissions"}` |
| 404 | Not Found | `{"error": "Resource not found"}` |
| 500 | Server Error | `{"error": "Internal server error"}` |

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  {{TABLE_1}}│       │  {{TABLE_2}}│       │  {{TABLE_3}}│
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │───┐   │ id (PK)     │   ┌───│ id (PK)     │
│ {{COL_1}}   │   │   │ {{COL_2}}   │   │   │ {{COL_3}}   │
│ {{COL_2}}   │   └──►│ {{FK_1}}(FK)│   │   │ {{COL_4}}   │
│ created_at  │       │ created_at  │◄──┘   │ created_at  │
└─────────────┘       └─────────────┘       └─────────────┘
```

### Tables

#### {{TABLE_1}}

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID/INT | PRIMARY KEY | Unique identifier |
| `{{COL_1}}` | {{TYPE_1}} | {{CONSTRAINT_1}} | {{DESC_1}} |
| `{{COL_2}}` | {{TYPE_2}} | {{CONSTRAINT_2}} | {{DESC_2}} |
| `created_at` | TIMESTAMP | NOT NULL DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |

### Migrations

```bash
# Create new migration
{{MIGRATION_CREATE_CMD}}

# Run migrations
{{MIGRATION_RUN_CMD}}

# Rollback last migration
{{MIGRATION_ROLLBACK_CMD}}
```

---

## Testing Guide

### Test Structure

```
tests/
├── unit/                 # Unit tests
│   ├── {{SERVICE}}/
│   └── {{MODEL}}/
├── integration/          # Integration tests
│   ├── api/
│   └── database/
├── e2e/                  # End-to-end tests
├── fixtures/             # Test data
└── conftest.{{EXT}}      # Test configuration
```

### Running Tests

```bash
# Run all tests
{{TEST_ALL_CMD}}

# Run unit tests only
{{TEST_UNIT_CMD}}

# Run with coverage
{{TEST_COVERAGE_CMD}}

# Run specific test file
{{TEST_SPECIFIC_CMD}}
```

### Test Coverage Requirements

| Type | Minimum Coverage |
|------|------------------|
| Unit Tests | 80% |
| Integration Tests | 60% |
| Critical Paths | 100% |

### Writing Tests

#### Unit Test Example

```{{LANG_EXT}}
{{UNIT_TEST_EXAMPLE}}
```

#### Integration Test Example

```{{LANG_EXT}}
{{INTEGRATION_TEST_EXAMPLE}}
```

---

## Deployment

### Environments

| Environment | URL | Branch | Auto-Deploy |
|-------------|-----|--------|-------------|
| Development | `{{DEV_URL}}` | `develop` | Yes |
| Staging | `{{STAGING_URL}}` | `staging` | Yes |
| Production | `{{PROD_URL}}` | `main` | Manual |

### Deployment Commands

```bash
# Deploy to staging
{{DEPLOY_STAGING_CMD}}

# Deploy to production
{{DEPLOY_PROD_CMD}}

# Rollback
{{ROLLBACK_CMD}}
```

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml or equivalent
Pipeline Stages:
1. Lint & Format Check
2. Unit Tests
3. Build
4. Integration Tests
5. Deploy to Staging
6. E2E Tests
7. Deploy to Production (manual approval)
```

### Health Checks

| Endpoint | Expected Response |
|----------|-------------------|
| `/health` | `{"status": "healthy"}` |
| `/ready` | `{"status": "ready"}` |
| `/metrics` | Prometheus metrics |

---

## Troubleshooting

### Common Issues

#### Issue: {{ISSUE_1}}

**Symptoms:** {{SYMPTOMS_1}}

**Cause:** {{CAUSE_1}}

**Solution:**
```bash
{{SOLUTION_1}}
```

#### Issue: {{ISSUE_2}}

**Symptoms:** {{SYMPTOMS_2}}

**Cause:** {{CAUSE_2}}

**Solution:**
```bash
{{SOLUTION_2}}
```

### Debug Mode

```bash
# Enable debug logging
{{DEBUG_ENABLE_CMD}}

# View logs
{{VIEW_LOGS_CMD}}
```

### Useful Commands

| Command | Description |
|---------|-------------|
| `{{CMD_1}}` | {{CMD_1_DESC}} |
| `{{CMD_2}}` | {{CMD_2_DESC}} |
| `{{CMD_3}}` | {{CMD_3_DESC}} |

### Getting Help

1. Check this guide and inline documentation
2. Search existing issues: {{ISSUES_URL}}
3. Ask in team chat: {{CHAT_CHANNEL}}
4. Create new issue with reproduction steps

---

## Contributing

### Workflow

1. Create feature branch from `develop`
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/{{FEATURE_NAME}}
   ```

2. Make changes and commit
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

3. Push and create PR
   ```bash
   git push origin feature/{{FEATURE_NAME}}
   ```

4. Request review from team

5. Address feedback and merge

### Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/{{description}}` | `feature/user-auth` |
| Bug Fix | `fix/{{description}}` | `fix/login-error` |
| Hotfix | `hotfix/{{description}}` | `hotfix/security-patch` |
| Release | `release/{{version}}` | `release/v1.2.0` |

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guide
- [ ] Self-reviewed
- [ ] Documentation updated
- [ ] No hardcoded secrets
```

---

## Appendix

### Glossary

| Term | Definition |
|------|------------|
| {{TERM_1}} | {{DEF_1}} |
| {{TERM_2}} | {{DEF_2}} |

### External Resources

- {{RESOURCE_1_NAME}}: {{RESOURCE_1_URL}}
- {{RESOURCE_2_NAME}}: {{RESOURCE_2_URL}}
- {{RESOURCE_3_NAME}}: {{RESOURCE_3_URL}}

### Contact

| Role | Name | Contact |
|------|------|---------|
| Tech Lead | {{TECH_LEAD}} | {{TECH_LEAD_EMAIL}} |
| DevOps | {{DEVOPS}} | {{DEVOPS_EMAIL}} |
| Product | {{PRODUCT}} | {{PRODUCT_EMAIL}} |

---

*Template Version: 1.0*
*Based on: Fokha AI Studio Pro Development Patterns*
