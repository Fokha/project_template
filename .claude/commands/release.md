# Release Command

Complete release workflow: test, save, update ALL relevant docs, commit, sync, and version.

## Usage

```
/release [version_bump]
```

Where `version_bump` is optional: `patch` (default), `minor`, or `major`.

## Workflow Steps

### 1. Test
- Run project tests (dart test, python -m pytest, flutter test, npm test)
- Verify all tests pass before proceeding
- Report test results

### 2. Save
- Ensure all files are saved
- Stage changed files for commit

### 3. Update Documentation (CRITICAL - Update ALL Relevant Docs!)

**ALWAYS analyze what was changed and update the appropriate docs:**

#### Core Version Files (Always Check)
| File | When to Update |
|------|----------------|
| `VERSION` | Every release |
| `CHANGELOG.md` | Every release - detailed release notes |
| `pubspec.yaml` | Flutter/Dart version |
| `package.json` | Node.js version |
| `pyproject.toml` | Python version |

#### Project Documentation (Based on Changes)
| File | When to Update |
|------|----------------|
| `README.md` | New features, usage changes, badges |
| `PROJECT_STRUCTURE.md` | New files, folders, modules added |
| `ARCHITECTURE.md` | System design changes |
| `CLAUDE.md` | AI agent instructions, system changes |

#### API Documentation (For API Changes)
| File | When to Update |
|------|----------------|
| `API_REFERENCE.md` | New endpoints, changed endpoints |
| `API_DOCUMENTATION.md` | Detailed API docs |
| `docs/api/*.md` | Endpoint-specific docs |
| OpenAPI/Swagger specs | API schema changes |

#### User Documentation (For User-Facing Changes)
| File | When to Update |
|------|----------------|
| `USER_MANUAL.md` | New features users interact with |
| `GETTING_STARTED.md` | Setup/install changes |
| `TUTORIAL.md` | New workflows |
| `FAQ.md` | Common questions |
| `docs/guides/*.md` | Feature guides |

#### Developer Documentation (For Dev Changes)
| File | When to Update |
|------|----------------|
| `DEV_GUIDE.md` | Development workflow changes |
| `CONTRIBUTING.md` | Contribution process changes |
| `TESTING.md` | Test strategy changes |
| `DEPLOYMENT.md` | Deploy process changes |
| `docs/dev/*.md` | Dev-specific docs |

#### Code Documentation (For Code Changes)
| Location | When to Update |
|----------|----------------|
| Docstrings | New/changed functions, classes |
| README in subfolders | New packages, modules |
| Inline comments | Complex logic |
| Type annotations | Public APIs |

#### Skills & Commands (For Automation Changes)
| File | When to Update |
|------|----------------|
| `.claude/commands/*.md` | New or changed skills |
| `SKILLS_INDEX.md` | New skills added |
| `scripts/README.md` | New scripts |

#### Index Files (For New Components)
| File | When to Update |
|------|----------------|
| `SKILLS_INDEX.md` | New skill templates |
| `TOOLS_INDEX.md` | New tools |
| `AGENTS_INDEX.md` | New agents |
| `docs/INDEX.md` | New documentation |

### 4. Commit
- Create descriptive commit message
- Include version number
- Add Co-Authored-By footer

### 5. Sync
- Push to remote repository
- Verify push succeeded

### 6. Version
- Bump version based on change type:
  - `patch`: Bug fixes (1.0.0 → 1.0.1)
  - `minor`: New features (1.0.0 → 1.1.0)
  - `major`: Breaking changes (1.0.0 → 2.0.0)

## Documentation Checklist

Before completing release, verify:

```
[ ] CHANGELOG.md - Added version section with all changes
[ ] VERSION - Updated version number
[ ] Config files - pubspec.yaml/package.json/pyproject.toml updated

For NEW FEATURES:
[ ] README.md - Feature documented
[ ] USER_MANUAL.md - Usage instructions added
[ ] PROJECT_STRUCTURE.md - New files/folders listed

For NEW APIs:
[ ] API_REFERENCE.md - Endpoint documented
[ ] API_DOCUMENTATION.md - Detailed docs added
[ ] Examples added

For NEW CODE:
[ ] Docstrings - All public functions documented
[ ] Type hints - Parameters and returns typed
[ ] README in module - If new package/module

For NEW SKILLS/TOOLS:
[ ] SKILLS_INDEX.md - Skill listed
[ ] Skill file created - .claude/commands/*.md
[ ] Usage examples - Included in docs

For ARCHITECTURE CHANGES:
[ ] ARCHITECTURE.md - Design documented
[ ] CLAUDE.md - Agent instructions updated
[ ] Diagrams updated - If applicable
```

## Example: Adding a New Package

When adding `fokha_data` package, update:

1. `CHANGELOG.md` - New version section with package details
2. `VERSION` - Bump minor version
3. `README.md` - Add to packages list
4. `PROJECT_STRUCTURE.md` - Add package structure
5. `packages/fokha_data/README.md` - Package documentation
6. `packages/fokha_data/CHANGELOG.md` - Package changelog
7. `SKILLS_INDEX.md` - If includes skill templates
8. `pubspec.yaml` - Version bump

## Example: Adding New API Endpoint

When adding `/api/signals` endpoint, update:

1. `CHANGELOG.md` - Document new endpoint
2. `API_REFERENCE.md` - Add endpoint to reference
3. `API_DOCUMENTATION.md` - Full endpoint documentation
4. `USER_MANUAL.md` - If user-facing
5. Docstrings in code - Function documentation
6. `VERSION` - Bump version

## Commit Message Format

```
<type>(<scope>): <description>

<body with details>

Docs updated:
- CHANGELOG.md
- README.md
- [other docs...]

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `/release` | Patch release (1.0.0 → 1.0.1) |
| `/release patch` | Same as above |
| `/release minor` | Minor release (1.0.0 → 1.1.0) |
| `/release major` | Major release (1.0.0 → 2.0.0) |

## Important Rules

1. **NEVER skip documentation** - Every change needs appropriate docs
2. **Match docs to changes** - API change = API docs, UI change = user docs
3. **Update indexes** - Add new items to relevant index files
4. **Include examples** - Code examples in documentation
5. **Keep consistent** - Follow existing doc formats in project
