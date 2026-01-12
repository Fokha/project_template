# Update Documentation

Ensure all documentation is updated after code changes.

## Documentation Checklist

### For ANY Release/Version Change:
- [ ] `VERSION` file - Update APP_VERSION, BUILD_NUMBER
- [ ] `{{CONFIG_FILE}}` - Update version number
- [ ] `CHANGELOG.md` - Add new version section

### For New API Endpoints:
- [ ] `docs/API_REFERENCE.md` - Add endpoint documentation
- [ ] `CLAUDE.md` - Update API section

### For New Features:
- [ ] `CLAUDE.md` - Update relevant section
- [ ] `docs/USER_MANUAL.md` - Update user documentation
- [ ] `README.md` - Update if user-facing

### For Database Changes:
- [ ] `docs/DATABASE_SCHEMA.md` - Update schema docs
- [ ] Create migration file if needed

### For Configuration Changes:
- [ ] `.env.example` - Update with new variables
- [ ] `docs/DEV_GUIDE.md` - Update configuration section

## Quick Commands

```bash
# Check current version
cat VERSION

# View recent changelog
head -50 CHANGELOG.md

# Check what files changed
git diff --name-only

# Check git status
git status
```

## Changelog Format

```markdown
## [X.X.X] - YYYY-MM-DD

### Feature Name

#### New Features
- **Component** (`path/to/file`) - Description

#### Bug Fixes
- Fixed issue with X

#### Files Modified
- `path/to/file` - What changed
```
