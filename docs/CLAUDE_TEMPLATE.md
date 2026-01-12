# ═══════════════════════════════════════════════════════════════════════════════
# {{PROJECT_NAME}} - AI AGENT MASTER DOCUMENTATION
# ═══════════════════════════════════════════════════════════════════════════════
#
# Author: {{AUTHOR}}
# Last Updated: {{DATE}}
#
# SYSTEM VERSIONS:
# ├── {{COMPONENT_1}}:  v{{VERSION_1}} ({{COMPONENT_1_DESC}})
# ├── {{COMPONENT_2}}:  v{{VERSION_2}} ({{COMPONENT_2_DESC}})
# └── {{COMPONENT_3}}:  v{{VERSION_3}} ({{COMPONENT_3_DESC}})
#
# ═══════════════════════════════════════════════════════════════════════════════

# ┌─────────────────────────────────────────────────────────────────────────────┐
# │                        TABLE OF CONTENTS                                     │
# ├─────────────────────────────────────────────────────────────────────────────┤
# │  SECTION 1: PROJECT OVERVIEW                                                │
# │  SECTION 2: ARCHITECTURE & COMPONENTS                                       │
# │  SECTION 3: API REFERENCE                                                   │
# │  SECTION 4: DATABASE SCHEMA                                                 │
# │  SECTION 5: WORKFLOWS & AUTOMATION                                          │
# │  SECTION 6: DEPLOYMENT & INFRASTRUCTURE                                     │
# │  SECTION 7: AGENT INSTRUCTIONS                                              │
# │  SECTION 8: COMMANDS & SHORTCUTS                                            │
# │  SECTION 9: CLAUDE CODE RULES (PRODUCTION MODE) ★                           │
# └─────────────────────────────────────────────────────────────────────────────┘


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: PROJECT OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
#
# {{PROJECT_DESCRIPTION}}
#
# ═══════════════════════════════════════════════════════════════════════════════

## 1.1 PROJECT SUMMARY
─────────────────────────────────────────────────────────────────────────────────

| Aspect | Details |
|--------|---------|
| **Project Name** | {{PROJECT_NAME}} |
| **Description** | {{PROJECT_DESCRIPTION}} |
| **Primary Language** | {{PRIMARY_LANGUAGE}} |
| **Framework** | {{FRAMEWORK}} |
| **Repository** | {{REPO_URL}} |

## 1.2 DIRECTORY STRUCTURE
─────────────────────────────────────────────────────────────────────────────────

```
{{PROJECT_ROOT}}/
├── {{FOLDER_1}}/           # {{FOLDER_1_DESC}}
│   ├── {{SUBFOLDER_1A}}/   # {{SUBFOLDER_1A_DESC}}
│   ├── {{SUBFOLDER_1B}}/   # {{SUBFOLDER_1B_DESC}}
│   └── {{SUBFOLDER_1C}}/   # {{SUBFOLDER_1C_DESC}}
├── {{FOLDER_2}}/           # {{FOLDER_2_DESC}}
├── {{FOLDER_3}}/           # {{FOLDER_3_DESC}}
├── docs/                   # Documentation
├── tests/                  # Test files
├── scripts/                # Automation scripts
└── config/                 # Configuration
```

## 1.3 KEY FILES
─────────────────────────────────────────────────────────────────────────────────

| File | Purpose |
|------|---------|
| `{{ENTRY_POINT}}` | Application entry point |
| `{{CONFIG_FILE}}` | Project configuration |
| `CLAUDE.md` | AI agent instructions (this file) |
| `VERSION` | Version tracking |
| `.env` | Environment variables |


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: ARCHITECTURE & COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════
#
# Path: {{PROJECT_PATH}}
# Framework: {{FRAMEWORK}}
# Total Files: {{TOTAL_FILES}}
#
# ═══════════════════════════════════════════════════════════════════════════════

## 2.1 ARCHITECTURE OVERVIEW
─────────────────────────────────────────────────────────────────────────────────

```
┌─────────────────────────────────────────────────────────────────────┐
│                       {{PROJECT_NAME}}                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐   │
│   │  {{LAYER_1}}│────────►│  {{LAYER_2}}│────────►│  {{LAYER_3}}│   │
│   │             │◄────────│             │◄────────│             │   │
│   └─────────────┘         └─────────────┘         └─────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 2.2 {{COMPONENT_1}} ({{COMPONENT_1_TECH}})
─────────────────────────────────────────────────────────────────────────────────

### Directory Structure
```
{{COMPONENT_1_PATH}}/
├── {{COMP1_FOLDER_1}}/     # {{COMP1_FOLDER_1_DESC}}
├── {{COMP1_FOLDER_2}}/     # {{COMP1_FOLDER_2_DESC}}
├── {{COMP1_FOLDER_3}}/     # {{COMP1_FOLDER_3_DESC}}
└── {{COMP1_FOLDER_4}}/     # {{COMP1_FOLDER_4_DESC}}
```

### Key Classes/Modules
- [ ] `{{CLASS_1}}` - {{CLASS_1_DESC}}
- [ ] `{{CLASS_2}}` - {{CLASS_2_DESC}}
- [ ] `{{CLASS_3}}` - {{CLASS_3_DESC}}
- [ ] `{{CLASS_4}}` - {{CLASS_4_DESC}}

### Features Checklist
- [ ] {{FEATURE_1}}
- [ ] {{FEATURE_2}}
- [ ] {{FEATURE_3}}
- [x] {{COMPLETED_FEATURE}} (v{{VERSION}})

## 2.3 {{COMPONENT_2}} ({{COMPONENT_2_TECH}})
─────────────────────────────────────────────────────────────────────────────────

### Directory Structure
```
{{COMPONENT_2_PATH}}/
├── {{COMP2_FOLDER_1}}/     # {{COMP2_FOLDER_1_DESC}}
├── {{COMP2_FOLDER_2}}/     # {{COMP2_FOLDER_2_DESC}}
└── {{COMP2_FOLDER_3}}/     # {{COMP2_FOLDER_3_DESC}}
```

### Key Services
| Service | Purpose | Status |
|---------|---------|--------|
| `{{SERVICE_1}}` | {{SERVICE_1_DESC}} | Active |
| `{{SERVICE_2}}` | {{SERVICE_2_DESC}} | Active |
| `{{SERVICE_3}}` | {{SERVICE_3_DESC}} | Planned |


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: API REFERENCE
# ═══════════════════════════════════════════════════════════════════════════════
#
# Base URL: http://localhost:{{PORT}}
# Total Endpoints: {{TOTAL_ENDPOINTS}}
#
# ═══════════════════════════════════════════════════════════════════════════════

## 3.1 API OVERVIEW
─────────────────────────────────────────────────────────────────────────────────

### Base URLs
| Environment | URL |
|-------------|-----|
| Development | `http://localhost:{{PORT}}` |
| Production | `https://{{PROD_DOMAIN}}` |

### Authentication
```
Authorization: Bearer <token>
```

## 3.2 CORE ENDPOINTS
─────────────────────────────────────────────────────────────────────────────────

### Health & Status
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/version` | API version |
| GET | `/status` | System status |

### {{RESOURCE_1}} Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{{RESOURCE_1}}` | List all |
| GET | `/api/{{RESOURCE_1}}/:id` | Get by ID |
| POST | `/api/{{RESOURCE_1}}` | Create |
| PUT | `/api/{{RESOURCE_1}}/:id` | Update |
| DELETE | `/api/{{RESOURCE_1}}/:id` | Delete |

### {{RESOURCE_2}} Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{{RESOURCE_2}}` | List all |
| POST | `/api/{{RESOURCE_2}}/{{ACTION_1}}` | {{ACTION_1_DESC}} |
| POST | `/api/{{RESOURCE_2}}/{{ACTION_2}}` | {{ACTION_2_DESC}} |

## 3.3 RESPONSE FORMAT
─────────────────────────────────────────────────────────────────────────────────

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

### Error Response
```json
{
  "success": false,
  "data": null,
  "error": "Error message"
}
```


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: DATABASE SCHEMA
# ═══════════════════════════════════════════════════════════════════════════════
#
# Database: {{DATABASE_TYPE}}
# Location: {{DATABASE_PATH}}
#
# ═══════════════════════════════════════════════════════════════════════════════

## 4.1 TABLES OVERVIEW
─────────────────────────────────────────────────────────────────────────────────

| Table | Purpose | Records |
|-------|---------|---------|
| `{{TABLE_1}}` | {{TABLE_1_DESC}} | ~{{TABLE_1_RECORDS}} |
| `{{TABLE_2}}` | {{TABLE_2_DESC}} | ~{{TABLE_2_RECORDS}} |
| `{{TABLE_3}}` | {{TABLE_3_DESC}} | ~{{TABLE_3_RECORDS}} |

## 4.2 TABLE SCHEMAS
─────────────────────────────────────────────────────────────────────────────────

### {{TABLE_1}}
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique ID |
| `{{COL_1}}` | {{TYPE_1}} | {{CONSTRAINT_1}} | {{COL_1_DESC}} |
| `{{COL_2}}` | {{TYPE_2}} | {{CONSTRAINT_2}} | {{COL_2_DESC}} |
| `created_at` | TIMESTAMP | NOT NULL | Creation time |
| `updated_at` | TIMESTAMP | NOT NULL | Last update |

### {{TABLE_2}}
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique ID |
| `{{COL_3}}` | {{TYPE_3}} | {{CONSTRAINT_3}} | {{COL_3_DESC}} |
| `{{COL_4}}` | {{TYPE_4}} | FOREIGN KEY | Links to {{TABLE_1}} |


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: WORKFLOWS & AUTOMATION
# ═══════════════════════════════════════════════════════════════════════════════
#
# Automation: {{AUTOMATION_TOOL}}
# Scripts: {{SCRIPTS_PATH}}
#
# ═══════════════════════════════════════════════════════════════════════════════

## 5.1 AUTOMATED WORKFLOWS
─────────────────────────────────────────────────────────────────────────────────

| Workflow | Schedule | Description |
|----------|----------|-------------|
| `{{WORKFLOW_1}}` | {{SCHEDULE_1}} | {{WORKFLOW_1_DESC}} |
| `{{WORKFLOW_2}}` | {{SCHEDULE_2}} | {{WORKFLOW_2_DESC}} |
| `{{WORKFLOW_3}}` | On trigger | {{WORKFLOW_3_DESC}} |

## 5.2 SCRIPTS
─────────────────────────────────────────────────────────────────────────────────

| Script | Purpose | Usage |
|--------|---------|-------|
| `dev-start.sh` | Start dev environment | `./scripts/dev-start.sh` |
| `dev-stop.sh` | Stop dev environment | `./scripts/dev-stop.sh` |
| `run_tests.sh` | Run test suite | `./scripts/run_tests.sh` |
| `deploy.sh` | Deploy to production | `./scripts/deploy.sh` |
| `backup.sh` | Backup data | `./scripts/backup.sh` |


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: DEPLOYMENT & INFRASTRUCTURE
# ═══════════════════════════════════════════════════════════════════════════════
#
# Provider: {{CLOUD_PROVIDER}}
# Server: {{SERVER_IP}}
#
# ═══════════════════════════════════════════════════════════════════════════════

## 6.1 ENVIRONMENTS
─────────────────────────────────────────────────────────────────────────────────

| Environment | URL | Branch |
|-------------|-----|--------|
| Development | `localhost:{{PORT}}` | `develop` |
| Staging | `{{STAGING_URL}}` | `staging` |
| Production | `{{PROD_URL}}` | `main` |

## 6.2 SERVICES
─────────────────────────────────────────────────────────────────────────────────

| Service | Port | Health Check |
|---------|------|--------------|
| {{SERVICE_1}} | {{PORT_1}} | `http://localhost:{{PORT_1}}/health` |
| {{SERVICE_2}} | {{PORT_2}} | `http://localhost:{{PORT_2}}/health` |
| {{SERVICE_3}} | {{PORT_3}} | `http://localhost:{{PORT_3}}/health` |

## 6.3 HEALTH CHECKS
─────────────────────────────────────────────────────────────────────────────────

```bash
# Check all services
curl http://localhost:{{PORT_1}}/health
curl http://localhost:{{PORT_2}}/health

# Check cloud
curl http://{{SERVER_IP}}:{{PORT}}/health
```


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: AGENT INSTRUCTIONS
# ═══════════════════════════════════════════════════════════════════════════════
#
# IMPORTANT: All AI agents working on this project MUST follow these rules
#
# ═══════════════════════════════════════════════════════════════════════════════

## 7.1 MANDATORY DOCUMENTATION UPDATES
─────────────────────────────────────────────────────────────────────────────────

When you make code changes, you MUST update documentation:

### For ANY Release/Version Change:
1. `VERSION` file → Update APP_VERSION, BUILD_NUMBER
2. `{{CONFIG_FILE}}` → Update version
3. `CHANGELOG.md` → Add new version section with changes

### For New API Endpoints:
4. `docs/API_REFERENCE.md` → Add endpoint documentation
5. This file (CLAUDE.md) → Update Section 3

### For New Features:
6. `CLAUDE.md` → Update relevant section
7. `docs/USER_MANUAL.md` → Update user documentation

### For Database Changes:
8. `docs/DATABASE_SCHEMA.md` → Update schema docs
9. Create migration if needed

## 7.2 VERSION NUMBERING
─────────────────────────────────────────────────────────────────────────────────

Use Semantic Versioning: MAJOR.MINOR.PATCH

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Breaking changes | MAJOR | 1.0.0 → 2.0.0 |
| New features | MINOR | 1.0.0 → 1.1.0 |
| Bug fixes | PATCH | 1.0.0 → 1.0.1 |

Current Version: v{{CURRENT_VERSION}}

## 7.3 CHANGELOG FORMAT
─────────────────────────────────────────────────────────────────────────────────

```markdown
## [X.X.X] - YYYY-MM-DD

### {{Feature Name}}

#### New Features
- **ServiceName** (`path/to/file`) - Description

#### New API Endpoints
- `METHOD /endpoint` - Description

#### Files Created
- `path/to/file` (~XXX lines)

#### Files Modified
- `path/to/file` - What changed

#### Bug Fixes
- Fixed issue with X
```

## 7.4 CODE STYLE RULES
─────────────────────────────────────────────────────────────────────────────────

### General Rules
- Follow existing patterns in the codebase
- Use meaningful variable/function names
- Add comments for complex logic
- No hardcoded secrets or credentials
- Handle errors appropriately

### {{LANGUAGE_1}} Style
- {{STYLE_RULE_1}}
- {{STYLE_RULE_2}}
- {{STYLE_RULE_3}}

### {{LANGUAGE_2}} Style
- {{STYLE_RULE_4}}
- {{STYLE_RULE_5}}
- {{STYLE_RULE_6}}

## 7.5 TESTING REQUIREMENTS
─────────────────────────────────────────────────────────────────────────────────

Before committing changes:
- [ ] Run existing tests: `{{TEST_CMD}}`
- [ ] Add tests for new functionality
- [ ] Ensure no regressions
- [ ] Update test documentation if needed

## 7.6 FILES TO ALWAYS CHECK
─────────────────────────────────────────────────────────────────────────────────

| File | When to Update |
|------|----------------|
| `VERSION` | Every release |
| `{{CONFIG_FILE}}` | Every release |
| `CHANGELOG.md` | Every feature/fix |
| `CLAUDE.md` | Significant changes |
| `docs/API_REFERENCE.md` | New endpoints |


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8: COMMANDS & SHORTCUTS
# ═══════════════════════════════════════════════════════════════════════════════
#
# Quick commands for common tasks
#
# ═══════════════════════════════════════════════════════════════════════════════

## 8.1 DEVELOPMENT COMMANDS
─────────────────────────────────────────────────────────────────────────────────

```bash
# Start development
{{DEV_START_CMD}}

# Stop development
{{DEV_STOP_CMD}}

# Run tests
{{TEST_CMD}}

# Check code style
{{LINT_CMD}}

# Build project
{{BUILD_CMD}}
```

## 8.2 GIT WORKFLOW
─────────────────────────────────────────────────────────────────────────────────

```bash
# Create feature branch
git checkout -b feature/{{feature-name}}

# Commit with conventional format
git commit -m "feat(scope): description"
git commit -m "fix(scope): description"
git commit -m "docs(scope): description"

# Push and create PR
git push origin feature/{{feature-name}}
```

## 8.3 AGENT SLASH COMMANDS
─────────────────────────────────────────────────────────────────────────────────

| Command | Description |
|---------|-------------|
| `/status` | Check system status |
| `/help` | Show available commands |
| `/update-docs` | Documentation update checklist |
| `/{{CUSTOM_CMD_1}}` | {{CUSTOM_CMD_1_DESC}} |
| `/{{CUSTOM_CMD_2}}` | {{CUSTOM_CMD_2_DESC}} |

## 8.4 USEFUL PATHS
─────────────────────────────────────────────────────────────────────────────────

| Purpose | Path |
|---------|------|
| Project Root | `{{PROJECT_ROOT}}` |
| Source Code | `{{SOURCE_PATH}}` |
| Tests | `{{TESTS_PATH}}` |
| Documentation | `{{DOCS_PATH}}` |
| Configuration | `{{CONFIG_PATH}}` |
| Logs | `{{LOGS_PATH}}` |


# ═══════════════════════════════════════════════════════════════════════════════
# QUICK REFERENCE CARD
# ═══════════════════════════════════════════════════════════════════════════════

## Status Checks
```bash
curl http://localhost:{{PORT}}/health        # API health
{{TEST_CMD}}                                  # Run tests
```

## Common Tasks
| Task | Command |
|------|---------|
| Start dev | `{{DEV_START_CMD}}` |
| Run tests | `{{TEST_CMD}}` |
| Deploy | `{{DEPLOY_CMD}}` |
| View logs | `{{LOGS_CMD}}` |

## Key Contacts
| Role | Contact |
|------|---------|
| Tech Lead | {{TECH_LEAD_CONTACT}} |
| DevOps | {{DEVOPS_CONTACT}} |


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9: CLAUDE CODE RULES (PRODUCTION MODE)
# ═══════════════════════════════════════════════════════════════════════════════
#
# CRITICAL: All AI agents MUST follow these rules for code generation
# Version: 3.2
#
# ═══════════════════════════════════════════════════════════════════════════════

## 9.1 CORE BEHAVIOR
─────────────────────────────────────────────────────────────────────────────────

| Rule | Description |
|------|-------------|
| **FULL CODE** | Always provide FULL, PRODUCTION-READY code in ONE SHOT |
| **NO SIMPLIFY** | NEVER simplify, give examples, or use placeholders |
| **PRESERVE** | PRESERVE all existing working code, naming, structures |
| **COMPLETE** | Include ALL: imports, dependencies, models, services, configs |
| **READY TO USE** | Generate COMPLETE folder structures with all files |
| **KEEP TODOs** | Keep existing TODO comments unless instructed to implement |
| **NAMING** | Follow exact naming conventions in the project |

## 9.2 CODE QUALITY STANDARDS
─────────────────────────────────────────────────────────────────────────────────

### Required Elements
- Current best practices, no deprecated APIs
- Error handling and validation
- Responsive design and theming
- Inline comments for complex logic
- Cross-platform compatibility when applicable

### Preserve Existing
- Architecture patterns (MVC, MVVM, Provider, Clean Architecture)
- State management setup
- Navigation and routing
- UI elements, layouts, spacing, padding, animations
- Class/function names and conventions

## 9.3 SPECIAL COMMANDS
─────────────────────────────────────────────────────────────────────────────────

### Code Generation
| Command | Action |
|---------|--------|
| `[FULL_REBUILD]` | Complete project generation from scratch |
| `[FIX_ERRORS]` | Correct all errors, preserve logic (surgical fixes only) |
| `[PRESERVE_ENHANCE]` | Improve without breaking existing code |
| `[RESTORE_FEATURE]` | Restore removed/broken feature exactly |
| `[ALL_AT_ONCE]` | Force single full-file output |

### Documentation
| Command | Action |
|---------|--------|
| `[FULL_DOCS]` | Generate complete documentation suite |
| `[ANALYZE]` | Apply document analysis framework |

### Mode Commands
| Command | Action |
|---------|--------|
| `[PRODUCTION_MODE]` | Apply all rules maximally |
| `[FULL_STACK]` | Same as PRODUCTION_MODE |
| `[IGNORE_RULES]` | Temporarily disable for simple answer |

## 9.4 PROHIBITIONS
─────────────────────────────────────────────────────────────────────────────────

### ❌ NEVER DO
| Prohibition | Reason |
|-------------|--------|
| Samples/examples/snippets | Provide full code only |
| Placeholders (except existing TODOs) | Code must be complete |
| Modify working code without permission | Preserve stability |
| Split outputs unnecessarily | One-shot delivery |
| Assume defaults | Verify everything |
| Use deprecated APIs without warning | Maintain compatibility |
| Introduce undefined variables | Prevent runtime errors |
| Change identifiers arbitrarily | Preserve conventions |
| Implement features without instruction | Stay focused |
| Rewrite comprehensive files | Preserve work |
| Give simplified versions | Production-ready only |

## 9.5 OUTPUT FORMAT
─────────────────────────────────────────────────────────────────────────────────

### Standard Output Structure
```
1. FOLDER STRUCTURE (tree format)
2. FILE CONTENTS (complete, all imports)
3. CONFIGURATION FILES (package.json, requirements.txt, etc.)
4. ENVIRONMENT SETUP (.env.example)
5. DOCUMENTATION (README.md minimum)
6. SETUP INSTRUCTIONS
7. TESTING INSTRUCTIONS
```

### File Naming for Archives
```
{project_name}-v{version}-{serial}.zip

Examples:
trading_bot-v1.0.0-001.zip
ml_api-v2.3.1-042.zip
```

## 9.6 PROMPT TEMPLATES
─────────────────────────────────────────────────────────────────────────────────

### Generate Complete File
```
Rewrite <filename> fully, respecting all existing models, services,
and architecture. Include imports and dependencies, fully functional,
all in one shot.
```

### Fix Errors (Surgical)
```
Correct <filename> fully so reported errors are fixed, preserving
all functionality and project structure. SURGICAL fixes only -
adding ONLY what's missing.
```

### Restore Feature
```
Restore the <feature> exactly as it was, do not change models,
architecture, or layout.
```

### New Feature
```
Add <feature> to <file/module> following existing patterns.
Include all necessary imports, types, and error handling.
Do not modify other working code.
```

## 9.7 LANGUAGE-SPECIFIC RULES
─────────────────────────────────────────────────────────────────────────────────

| Language | Key Requirements |
|----------|-----------------|
| **Flutter/Dart** | Latest stable API, Provider/Riverpod/Bloc, Material 3, null safety |
| **Python** | Type hints, PEP 8, requirements.txt, async/await, .env.example |
| **React/TypeScript** | Functional components, hooks, TypeScript strict mode |
| **Node.js** | ES modules, async/await, package.json with scripts |
| **MQL4/MQL5** | Proper EA structure, input parameters, error handling |
| **Go** | go.mod, idiomatic error handling, proper package structure |
| **Rust** | Cargo.toml, Result/Option patterns, ownership |

## 9.8 QUICK REFERENCE
─────────────────────────────────────────────────────────────────────────────────

```
┌─────────────────────────────────────────────────────────────────┐
│                 CLAUDE CODE RULES - QUICK REF                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CORE: Full production code, ONE SHOT, ALL imports              │
│        PRESERVE existing code, NO placeholders                  │
│                                                                 │
│  COMMANDS:                                                      │
│  [FULL_REBUILD]     Complete project generation                 │
│  [FIX_ERRORS]       Surgical error correction                   │
│  [PRESERVE_ENHANCE] Improve without breaking                    │
│  [PRODUCTION_MODE]  Maximum rules application                   │
│  [IGNORE_RULES]     Simple answer mode                          │
│                                                                 │
│  OUTPUT: Structure → Files → Config → Env → Docs → Setup        │
│                                                                 │
│  NEVER: Samples, Placeholders, Modify working code,             │
│         Simplified versions, Split outputs                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

See `agents/prompts/CLAUDE_CODE_RULES.md` for complete rules documentation.


# ═══════════════════════════════════════════════════════════════════════════════
# MASTER DOCUMENTATION COMPLETE
# ═══════════════════════════════════════════════════════════════════════════════
#
# This document covers:
# ✓ SECTION 1: Project Overview
# ✓ SECTION 2: Architecture & Components
# ✓ SECTION 3: API Reference
# ✓ SECTION 4: Database Schema
# ✓ SECTION 5: Workflows & Automation
# ✓ SECTION 6: Deployment & Infrastructure
# ✓ SECTION 7: Agent Instructions
# ✓ SECTION 8: Commands & Shortcuts
# ✓ SECTION 9: Claude Code Rules (PRODUCTION MODE)
#
# IMPORTANT FOR AI AGENTS:
# - See Section 7 for mandatory documentation rules!
# - See Section 9 for code generation rules!
#
# Last Updated: {{DATE}}
# Template Version: 2.0
# Claude Code Rules Version: 3.2
# ═══════════════════════════════════════════════════════════════════════════════
