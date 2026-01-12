# {{PROJECT_NAME}} - Project Structure

**Version:** {{VERSION}} | **Last Updated:** {{DATE}}

---

## Overview

{{PROJECT_DESCRIPTION}}

```
{{PROJECT_NAME}}/
├── {{FOLDER_1}}/           # {{FOLDER_1_DESC}}
├── {{FOLDER_2}}/           # {{FOLDER_2_DESC}}
├── {{FOLDER_3}}/           # {{FOLDER_3_DESC}}
├── docs/                   # Documentation
├── tests/                  # Test files
├── scripts/                # Automation scripts
├── config/                 # Configuration files
└── [platform folders]      # Platform-specific code
```

---

## Directory Details

### {{FOLDER_1}}/ ({{FOLDER_1_LANGUAGE}})

{{FOLDER_1_DESCRIPTION}}

```
{{FOLDER_1}}/
├── {{ENTRY_POINT}}         # Application entry point
├── {{SUBFOLDER_1A}}/       # {{SUBFOLDER_1A_DESC}}
├── {{SUBFOLDER_1B}}/       # {{SUBFOLDER_1B_DESC}}
├── {{SUBFOLDER_1C}}/       # {{SUBFOLDER_1C_DESC}}
├── {{SUBFOLDER_1D}}/       # {{SUBFOLDER_1D_DESC}}
└── {{SUBFOLDER_1E}}/       # {{SUBFOLDER_1E_DESC}}
```

#### {{SUBFOLDER_1A}}/ ({{COUNT_1A}} files)

| File | Purpose |
|------|---------|
| `{{FILE_1A_1}}` | {{PURPOSE_1A_1}} |
| `{{FILE_1A_2}}` | {{PURPOSE_1A_2}} |
| `{{FILE_1A_3}}` | {{PURPOSE_1A_3}} |

#### {{SUBFOLDER_1B}}/ ({{COUNT_1B}} files)

| File | Purpose |
|------|---------|
| `{{FILE_1B_1}}` | {{PURPOSE_1B_1}} |
| `{{FILE_1B_2}}` | {{PURPOSE_1B_2}} |
| `{{FILE_1B_3}}` | {{PURPOSE_1B_3}} |

#### {{SUBFOLDER_1C}}/ ({{COUNT_1C}} files)

| Category | Files |
|----------|-------|
| **{{CATEGORY_1}}** | `{{CAT_1_FILES}}` |
| **{{CATEGORY_2}}** | `{{CAT_2_FILES}}` |
| **{{CATEGORY_3}}** | `{{CAT_3_FILES}}` |

---

### {{FOLDER_2}}/ ({{FOLDER_2_LANGUAGE}})

{{FOLDER_2_DESCRIPTION}}

```
{{FOLDER_2}}/
├── {{ENTRY_POINT_2}}       # Entry point / Main server
├── requirements.txt        # Dependencies
├── {{SUBFOLDER_2A}}/       # {{SUBFOLDER_2A_DESC}}
├── {{SUBFOLDER_2B}}/       # {{SUBFOLDER_2B_DESC}}
├── {{SUBFOLDER_2C}}/       # {{SUBFOLDER_2C_DESC}}
├── {{SUBFOLDER_2D}}/       # {{SUBFOLDER_2D_DESC}}
└── {{SUBFOLDER_2E}}/       # {{SUBFOLDER_2E_DESC}}
```

#### Key Files

| File | Lines | Description |
|------|-------|-------------|
| `{{KEY_FILE_1}}` | ~{{LINES_1}} | {{KEY_DESC_1}} |
| `{{KEY_FILE_2}}` | ~{{LINES_2}} | {{KEY_DESC_2}} |
| `{{KEY_FILE_3}}` | ~{{LINES_3}} | {{KEY_DESC_3}} |

---

### docs/

Project documentation.

| File | Purpose |
|------|---------|
| `README.md` | Project overview |
| `CHANGELOG.md` | Version history |
| `PRD.md` | Product requirements |
| `DEV_GUIDE.md` | Developer documentation |
| `API_REFERENCE.md` | API documentation |
| `DEPLOYMENT.md` | Deployment guide |

---

### tests/

Test files organized by type.

```
tests/
├── unit/                   # Unit tests
│   ├── {{UNIT_FOLDER_1}}/
│   └── {{UNIT_FOLDER_2}}/
├── integration/            # Integration tests
│   ├── api/
│   └── database/
├── e2e/                    # End-to-end tests
└── fixtures/               # Test data
```

| Test Category | Count | Coverage |
|---------------|-------|----------|
| Unit | {{UNIT_COUNT}} | {{UNIT_COV}}% |
| Integration | {{INT_COUNT}} | {{INT_COV}}% |
| E2E | {{E2E_COUNT}} | {{E2E_COV}}% |
| **Total** | **{{TOTAL_COUNT}}** | **{{TOTAL_COV}}%** |

---

### scripts/

Automation and utility scripts.

| Script | Purpose | Usage |
|--------|---------|-------|
| `dev-start.sh` | Start development environment | `./scripts/dev-start.sh` |
| `dev-stop.sh` | Stop development environment | `./scripts/dev-stop.sh` |
| `run_tests.sh` | Run test suite | `./scripts/run_tests.sh [smoke\|all]` |
| `deploy.sh` | Deploy to environment | `./scripts/deploy.sh [staging\|prod]` |
| `backup.sh` | Backup data | `./scripts/backup.sh` |

---

### config/

Configuration files.

| File | Purpose | Environment |
|------|---------|-------------|
| `{{CONFIG_1}}` | {{CONFIG_1_PURPOSE}} | All |
| `{{CONFIG_2}}` | {{CONFIG_2_PURPOSE}} | Development |
| `{{CONFIG_3}}` | {{CONFIG_3_PURPOSE}} | Production |

---

## Configuration Files (Root)

| File | Purpose |
|------|---------|
| `{{PACKAGE_FILE}}` | Dependencies and metadata |
| `.env.example` | Environment variables template |
| `.gitignore` | Git ignore patterns |
| `{{LINT_CONFIG}}` | Linting rules |
| `{{BUILD_CONFIG}}` | Build configuration |
| `CLAUDE.md` | AI assistant instructions |
| `VERSION` | Version tracking |

---

## File Counts Summary

| Folder | Files | Lines (approx) |
|--------|-------|----------------|
| {{FOLDER_1}}/ | {{COUNT_F1}} | {{LINES_F1}} |
| {{FOLDER_2}}/ | {{COUNT_F2}} | {{LINES_F2}} |
| tests/ | {{COUNT_TESTS}} | {{LINES_TESTS}} |
| docs/ | {{COUNT_DOCS}} | {{LINES_DOCS}} |
| scripts/ | {{COUNT_SCRIPTS}} | {{LINES_SCRIPTS}} |
| **Total** | **{{TOTAL_FILES}}** | **{{TOTAL_LINES}}** |

---

## Dependency Graph

```
                    ┌─────────────────┐
                    │   Entry Point   │
                    │  {{MAIN_FILE}}  │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
    ┌───────────┐    ┌───────────┐    ┌───────────┐
    │  Config   │    │  Routes/  │    │  Providers│
    │           │    │  Screens  │    │  /State   │
    └─────┬─────┘    └─────┬─────┘    └─────┬─────┘
          │                │                │
          │                ▼                │
          │        ┌───────────┐           │
          │        │  Services │           │
          │        └─────┬─────┘           │
          │              │                 │
          └──────────────┼─────────────────┘
                         │
                         ▼
                 ┌───────────┐
                 │  Models/  │
                 │  Database │
                 └───────────┘
```

---

## Module Dependencies

| Module | Depends On | Used By |
|--------|------------|---------|
| `{{MODULE_1}}` | {{DEPS_1}} | {{USED_BY_1}} |
| `{{MODULE_2}}` | {{DEPS_2}} | {{USED_BY_2}} |
| `{{MODULE_3}}` | {{DEPS_3}} | {{USED_BY_3}} |

---

## External Dependencies

### {{LANGUAGE_1}} Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| {{PKG_1}} | {{VER_1}} | {{PKG_PURPOSE_1}} |
| {{PKG_2}} | {{VER_2}} | {{PKG_PURPOSE_2}} |
| {{PKG_3}} | {{VER_3}} | {{PKG_PURPOSE_3}} |

### {{LANGUAGE_2}} Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| {{PKG_4}} | {{VER_4}} | {{PKG_PURPOSE_4}} |
| {{PKG_5}} | {{VER_5}} | {{PKG_PURPOSE_5}} |
| {{PKG_6}} | {{VER_6}} | {{PKG_PURPOSE_6}} |

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                      Presentation Layer                      │
│  (UI Components, Screens, Widgets)                          │
├─────────────────────────────────────────────────────────────┤
│                      Application Layer                       │
│  (Providers, State Management, Use Cases)                   │
├─────────────────────────────────────────────────────────────┤
│                       Service Layer                          │
│  (Business Logic, API Clients, Utilities)                   │
├─────────────────────────────────────────────────────────────┤
│                        Data Layer                            │
│  (Models, Repositories, Database, Cache)                    │
├─────────────────────────────────────────────────────────────┤
│                     Infrastructure Layer                     │
│  (External APIs, File System, Network)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Folders | snake_case | `user_management/` |
| Files | snake_case | `user_service.dart` |
| Classes | PascalCase | `UserService` |
| Variables | camelCase | `currentUser` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` |
| Database Tables | snake_case | `user_sessions` |
| API Endpoints | kebab-case | `/api/user-profiles` |

---

## Quick Navigation

### Finding Code

| Looking For | Location |
|-------------|----------|
| API handlers | `{{API_LOCATION}}` |
| Business logic | `{{SERVICE_LOCATION}}` |
| Data models | `{{MODEL_LOCATION}}` |
| UI components | `{{UI_LOCATION}}` |
| Configuration | `{{CONFIG_LOCATION}}` |
| Tests | `tests/` |
| Documentation | `docs/` |

### Common Tasks

| Task | File(s) to Edit |
|------|-----------------|
| Add new API endpoint | `{{ADD_ENDPOINT_FILES}}` |
| Add new model | `{{ADD_MODEL_FILES}}` |
| Add new UI screen | `{{ADD_SCREEN_FILES}}` |
| Update configuration | `{{UPDATE_CONFIG_FILES}}` |
| Add database migration | `{{ADD_MIGRATION_FILES}}` |

---

*Template Version: 1.0*
*Based on: Fokha AI Studio Pro Project Structure*
