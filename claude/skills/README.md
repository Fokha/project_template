# Claude Code Skills Templates

Reusable skill templates for Claude Code projects.

## What are Skills?

Skills are markdown files that provide context and commands for common workflows. They appear in Claude Code's `/skills` menu and can be invoked to guide the AI through specific tasks.

## Setup

1. Copy the `skills/` directory to your project's `.claude/` folder:
   ```bash
   cp -r project_template/claude/skills/ .claude/skills/
   ```

2. Customize placeholders (`{{PLACEHOLDER}}`) in each file

3. Run `/skills` in Claude Code to see available skills

## Available Templates

| Skill | Purpose | Key Placeholders |
|-------|---------|------------------|
| `status.md` | System health checks | `{{PORT_1}}`, `{{SERVICE_1}}` |
| `preflight.md` | Pre-task verification | `{{PORT}}` |
| `done.md` | Task completion checklist | `{{TEST_CMD}}`, `{{BUILD_CMD}}` |
| `update-docs.md` | Documentation updates | `{{CONFIG_FILE}}` |
| `commit.md` | Git commit helper | `{{SCOPE_1}}`, `{{TEST_CMD}}` |
| `test.md` | Test execution guide | `{{TEST_*_CMD}}` placeholders |
| `deploy.md` | Deployment procedures | `{{DEPLOY_*_CMD}}`, `{{STAGING_URL}}` |
| `debug.md` | Debugging guide | `{{LOG_PATH}}`, `{{VIEW_LOGS_CMD}}` |

## Customization Guide

### Common Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PORT}}` | Main service port | `3000`, `5050`, `8080` |
| `{{SERVICE_1}}` | Primary service name | `API`, `Backend`, `Server` |
| `{{TEST_CMD}}` | Test command | `npm test`, `pytest`, `flutter test` |
| `{{BUILD_CMD}}` | Build command | `npm run build`, `flutter build` |
| `{{START_CMD}}` | Start command | `npm start`, `python app.py` |
| `{{STAGING_URL}}` | Staging URL | `https://staging.example.com` |
| `{{PROD_URL}}` | Production URL | `https://example.com` |

### Example Customization

**Before (template):**
```bash
curl -s http://localhost:{{PORT}}/health
```

**After (customized):**
```bash
curl -s http://localhost:3000/health
```

## Creating Custom Skills

1. Create a new `.md` file in `.claude/skills/`
2. Use this structure:

```markdown
# Skill Name

Brief description of what this skill does.

## Quick Commands

\`\`\`bash
# Command 1
your-command-here

# Command 2
another-command
\`\`\`

## Checklist

- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Additional Context

Any other helpful information...
```

## Best Practices

1. **Keep skills focused** - One skill per workflow
2. **Include runnable commands** - Copy-paste ready
3. **Add checklists** - Easy verification
4. **Use tables** - For reference information
5. **Update regularly** - Keep commands current

## File Structure

```
.claude/
├── skills/
│   ├── status.md
│   ├── preflight.md
│   ├── done.md
│   ├── update-docs.md
│   ├── commit.md
│   ├── test.md
│   ├── deploy.md
│   ├── debug.md
│   └── README.md (this file)
├── commands/         # Slash commands (different from skills)
└── settings.json     # Claude Code settings
```
