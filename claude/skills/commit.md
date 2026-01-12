# Git Commit Helper

Create well-formatted git commits.

## Commit Convention

Format: `type(scope): description`

### Types

| Type | When to Use |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code restructuring |
| `test` | Adding tests |
| `chore` | Maintenance, dependencies |
| `perf` | Performance improvement |
| `ci` | CI/CD changes |

### Scopes (Project-Specific)

| Scope | Description |
|-------|-------------|
| `{{SCOPE_1}}` | {{SCOPE_1_DESC}} |
| `{{SCOPE_2}}` | {{SCOPE_2_DESC}} |
| `{{SCOPE_3}}` | {{SCOPE_3_DESC}} |

### Examples

```bash
git commit -m "feat(api): add user authentication endpoint"
git commit -m "fix({{SCOPE_1}}): correct calculation logic"
git commit -m "docs(readme): update installation steps"
git commit -m "refactor(services): extract common HTTP logic"
git commit -m "test({{SCOPE_2}}): add unit tests for validation"
```

## Pre-Commit Checklist

```bash
# Check what's staged
git status

# Review changes
git diff --staged

# Run tests before committing
{{TEST_CMD}}

# Check for linting issues
{{LINT_CMD}}
```

## Multi-line Commit

```bash
git commit -m "$(cat <<'EOF'
feat(component): short description

- Detailed point 1
- Detailed point 2
- Detailed point 3

Closes #123
EOF
)"
```

## After Commit

```bash
# Push to remote
git push

# Or push with upstream tracking
git push -u origin $(git branch --show-current)
```

## Undo Last Commit (if needed)

```bash
# Undo commit but keep changes staged
git reset --soft HEAD~1

# Undo commit and unstage changes
git reset HEAD~1
```
