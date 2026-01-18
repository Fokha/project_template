# Release Command

Complete release workflow: test, save, update docs, commit, sync, and version.

## Usage

```
/release [version_bump]
```

Where `version_bump` is optional: `patch` (default), `minor`, or `major`.

## Workflow Steps

Execute these steps in order:

### 1. Test
- Run project tests (dart test, python -m pytest, flutter test, npm test, etc.)
- Verify all tests pass before proceeding
- Report test results

### 2. Save
- Ensure all files are saved
- Stage changed files for commit

### 3. Update Documentation
- Update CHANGELOG.md with new version section
- Update VERSION file (if exists)
- Update README.md version badge (if applicable)
- Update pubspec.yaml / package.json / pyproject.toml version

### 4. Commit
- Create descriptive commit message summarizing changes
- Include version number in commit
- Add Co-Authored-By footer

### 5. Sync
- Push to remote repository
- Verify push succeeded

### 6. Version
- Determine new version based on:
  - `patch`: Bug fixes, minor changes (1.0.0 → 1.0.1)
  - `minor`: New features, backwards compatible (1.0.0 → 1.1.0)
  - `major`: Breaking changes (1.0.0 → 2.0.0)
- Update all version references

## Version File Locations

Check and update these files:
- `VERSION` - Version tracking file
- `pubspec.yaml` - Flutter/Dart projects
- `package.json` - Node.js projects
- `pyproject.toml` - Python projects
- `CHANGELOG.md` - Release notes
- `README.md` - Version badges

## Commit Message Format

```
<type>: <description>

<body with details>

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `style`

## CHANGELOG Format

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing features

### Fixed
- Bug fixes
```

## Example Execution

```
User: /release minor

Claude:
1. Running tests... 30/30 passed
2. Files saved
3. Updated CHANGELOG.md (v1.2.0 → v1.3.0)
4. Updated VERSION file
5. Committed: "feat: Add new feature (v1.3.0)"
6. Pushed to origin/main
7. Version: 1.2.0 → 1.3.0

Release complete!
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `/release` | Patch release (1.0.0 → 1.0.1) |
| `/release patch` | Same as above |
| `/release minor` | Minor release (1.0.0 → 1.1.0) |
| `/release major` | Major release (1.0.0 → 2.0.0) |

## Notes

- Always run tests before releasing
- Review changes before committing
- Ensure you're on the correct branch
- Check remote is configured correctly