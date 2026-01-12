# Definition of Done

Checklist to verify task completion.

## Code Quality

- [ ] Code compiles/runs without errors
- [ ] No linting warnings
- [ ] Follows project coding standards
- [ ] No hardcoded values (use config/constants)
- [ ] Error handling is appropriate
- [ ] No console.log/print statements in production code

## Testing

- [ ] Existing tests pass
- [ ] New tests added for new functionality
- [ ] Edge cases considered
- [ ] Manual testing completed

## Documentation

- [ ] Code comments for complex logic
- [ ] CHANGELOG.md updated (if releasing)
- [ ] API docs updated (if endpoints changed)
- [ ] README updated (if user-facing changes)
- [ ] CLAUDE.md updated (if significant changes)

## Git

- [ ] Changes committed with descriptive message
- [ ] Commit message follows convention: `type(scope): description`
- [ ] Pushed to remote (if ready)

## Verification Commands

```bash
# Run tests
{{TEST_CMD}}

# Check for uncommitted changes
git status

# Verify build
{{BUILD_CMD}}

# Verify service health
curl http://localhost:{{PORT}}/health
```

## Final Questions

1. Would I be confident deploying this?
2. Can another developer understand the changes?
3. Are there any TODOs left unaddressed?
4. Have I updated all necessary documentation?
