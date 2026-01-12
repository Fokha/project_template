# Prompt Style Guide

## Unified Theme for Project Template Prompts

This guide ensures consistency across all agent prompts, documentation, and system messages.

---

## 1. Document Structure Theme

### Standard Document Header

```markdown
# [Title in Title Case]

**Version:** X.Y (Optional)
**Updated:** YYYY-MM-DD (Optional)

## Overview

[2-3 sentence summary of what this document covers]

---
```

### Section Hierarchy

```markdown
# Main Title (H1) - One per document
## Major Section (H2) - Main topics
### Subsection (H3) - Details
#### Detail (H4) - Rarely needed

---  ← Horizontal rule between major sections
```

---

## 2. Visual Language

### ASCII Diagrams

Use box-drawing for flows and architecture:

```
┌─────────────┐         ┌─────────────┐
│   Input     │ ──────► │  Process    │
└─────────────┘         └─────────────┘
       │                       │
       ▼                       ▼
┌─────────────┐         ┌─────────────┐
│   Output    │ ◄────── │   Result    │
└─────────────┘         └─────────────┘

Characters to use:
┌ ┐ └ ┘ ─ │ ┬ ┴ ├ ┤ ┼
► ◄ ▲ ▼ (arrows)
```

### Tables

Use tables for comparisons, references, status:

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data     | Data     | Data     |

Use emojis sparingly for status:
✅ Done/Yes
❌ No/Failed
🔄 In Progress
📋 Backlog
⚠️ Warning
```

### Code Blocks

Always specify language:

```python
# Python example
def example():
    pass
```

```bash
# Shell commands
curl -X POST http://example.com
```

```json
{
  "key": "value"
}
```

---

## 3. Agent Prompt Structure

### Required Sections

Every agent prompt MUST have:

```markdown
# AGENT: [NAME]
# Role: [PRIMARY ROLE]
# Language: [TECH STACK]

## Your Responsibilities
- [Responsibility 1]
- [Responsibility 2]
- [Responsibility 3]

## You Communicate With
- [Agent]: [Relationship]

## Knowledge Base Access
[KB connection details]

## Session Protocol
### On Start
[Steps to load context]

### During Work
[How to track progress]

### On End
[How to save state]

## Your Tools
[Available tools/endpoints]

## Error Handling
[What to do when things fail]
```

### Voice & Tone

- **Direct**: "Run this command" not "You might want to run"
- **Imperative**: "Check the status" not "The status should be checked"
- **Specific**: "Call GET /kb/resume" not "Access the knowledge base"
- **Consistent**: Use same terminology throughout

---

## 4. Standard Terminology

### Agents

| Use This | Not This |
|----------|----------|
| Agent | Bot, AI, Assistant |
| Knowledge Base (KB) | Database, Storage |
| Session | Conversation, Chat |
| Signal | Notification, Alert |
| Resume | Continue, Restore |

### Actions

| Use This | Not This |
|----------|----------|
| Create | Add, Make, Build |
| Update | Modify, Change, Edit |
| Delete | Remove, Clear |
| Get/Fetch | Read, Retrieve, Load |
| Send | Post, Push, Transmit |

### Status

| Use This | Meaning |
|----------|---------|
| backlog | Not started |
| in_progress | Currently working |
| done | Completed |
| cancelled | Abandoned |
| blocked | Waiting on dependency |

### Priority

| Use This | Meaning |
|----------|---------|
| critical | Immediate action |
| high | Important, do soon |
| medium | Normal priority |
| low | When time permits |

---

## 5. Common Patterns

### API Endpoint Documentation

```markdown
### Endpoint Name

**Method:** GET/POST/PUT/DELETE
**URL:** /path/to/endpoint
**Purpose:** What it does

**Request:**
```json
{
  "param": "value"
}
```

**Response:**
```json
{
  "success": true,
  "data": {}
}
```

**Example:**
```bash
curl -X POST http://localhost:5050/endpoint \
  -H "Content-Type: application/json" \
  -d '{"param":"value"}'
```
```

### Step-by-Step Instructions

```markdown
### Task Name

1. **First Step**
   - Detail about the step
   - Another detail
   ```bash
   command to run
   ```

2. **Second Step**
   - Detail
   ```bash
   another command
   ```

3. **Verify**
   ```bash
   verification command
   ```
```

### Comparison Tables

```markdown
| Feature | Option A | Option B |
|---------|----------|----------|
| Speed | Fast | Slow |
| Cost | $10 | $5 |
| **Recommendation** | ✅ Use this | - |
```

---

## 6. Template Blocks

### Identity Block

```markdown
# AGENT: {AGENT_NAME}

You are {AGENT_NAME}, responsible for {PRIMARY_FUNCTION} in the {PROJECT_NAME} system.

## Core Identity
- **Role:** {ROLE_DESCRIPTION}
- **Language:** {PRIMARY_LANGUAGE}
- **Reports to:** {ORCHESTRATOR_OR_NONE}
- **Manages:** {SUBORDINATES_OR_NONE}
```

### KB Access Block

```markdown
## Knowledge Base Access

Base URL: `{KB_URL}`

### Startup
1. `GET /kb/resume` → Load context
2. `GET /kb/messages?to_agent={AGENT_NAME}` → Check inbox
3. `GET /kb/tasks?assigned_to={AGENT_NAME}` → My tasks

### During Work
- `POST /kb/activity` → Log actions
- `PUT /kb/tasks/{id}` → Update progress

### Shutdown
- `POST /kb/context` → Save focus
- `POST /kb/conversations` → Save key points
```

### Communication Block

```markdown
## Communication

### To Send Message
```json
POST /kb/messages
{
  "from_agent": "{AGENT_NAME}",
  "to_agent": "{TARGET}",
  "message_type": "request|response|update|notification",
  "content": "Message content"
}
```

### Message Types
- `request` → Asking for something
- `response` → Replying
- `update` → Status update
- `notification` → FYI
- `announcement` → Broadcast (to_agent: null)
```

### Error Block

```markdown
## Error Handling

When you encounter an error:

1. **Log it**
   ```json
   POST /kb/activity
   {"action": "error", "details": "description"}
   ```

2. **If blocking** → Update task, create sub-task

3. **If needs help** → Send message to appropriate agent

4. **Document** → Add to decisions if significant
```

---

## 7. File Naming Conventions

### Prompt Files

```
agents/prompts/
├── PROMPT_STYLE_GUIDE.md      # This file
├── AGENT_SYSTEM_PROMPT_TEMPLATE.md
├── orchestrator.md            # Role-specific prompts
├── developer.md
├── researcher.md
└── reviewer.md
```

### Documentation Files

```
docs/
├── README.md                  # Project overview
├── SETUP.md                   # Setup instructions
├── ARCHITECTURE.md            # System design
├── API_REFERENCE.md           # Endpoint docs
├── AGENT_KB_ACCESS.md         # Unified KB guide
└── LESSONS_LEARNED.md         # Project insights
```

### Naming Rules

- Use UPPERCASE for important docs: `README.md`, `SETUP.md`
- Use lowercase for role prompts: `developer.md`
- Use underscores for multi-word: `AGENT_KB_ACCESS.md`
- Always use `.md` extension

---

## 8. Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                    PROMPT QUICK REFERENCE                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STRUCTURE                                                  │
│  ─────────                                                  │
│  # Title (one per doc)                                      │
│  ## Section (major topics)                                  │
│  ### Subsection (details)                                   │
│  --- (horizontal rule between sections)                     │
│                                                             │
│  VOICE                                                      │
│  ─────                                                      │
│  ✓ Direct: "Run this"                                       │
│  ✓ Specific: "GET /kb/resume"                               │
│  ✗ Vague: "You might want to..."                            │
│                                                             │
│  STATUS EMOJIS                                              │
│  ─────────────                                              │
│  ✅ Done    ❌ Failed    🔄 Progress    📋 Backlog          │
│                                                             │
│  CODE BLOCKS                                                │
│  ───────────                                                │
│  ```python  ```bash  ```json  ```sql                        │
│                                                             │
│  DIAGRAMS                                                   │
│  ────────                                                   │
│  ┌───┐  ───►  │  ▼  ◄───                                   │
│                                                             │
│  REQUIRED PROMPT SECTIONS                                   │
│  ────────────────────────                                   │
│  1. Identity (name, role, language)                         │
│  2. Responsibilities (3-5 bullets)                          │
│  3. Communication (who talks to who)                        │
│  4. KB Access (startup, during, shutdown)                   │
│  5. Error Handling (what to do when stuck)                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Examples

### Good Prompt Opening

```markdown
# AGENT: DATA_ANALYST

You are DATA_ANALYST, responsible for market data analysis and reporting in the Trading System.

## Your Responsibilities
- Analyze market data for trends and patterns
- Generate daily/weekly performance reports
- Monitor data quality and flag anomalies
- Provide insights to trading agents

## You Communicate With
- ML_ENGINE: Request predictions, send data
- ORCHESTRATOR: Receive tasks, report completion
- NOTIFIER: Send alerts and reports
```

### Good API Documentation

```markdown
### Create Task

**Method:** POST
**URL:** `/kb/tasks`

**Request:**
```json
{
  "title": "Implement feature X",
  "description": "Details here",
  "priority": "high",
  "assigned_to": "DEVELOPER"
}
```

**Response:**
```json
{
  "success": true,
  "task_id": "T001"
}
```
```

### Good Step Instructions

```markdown
## Setup Database

1. **Create directory**
   ```bash
   mkdir -p knowledge_base
   ```

2. **Initialize schema**
   ```bash
   sqlite3 knowledge_base/agent_kb.db < schema.sql
   ```

3. **Verify**
   ```bash
   sqlite3 knowledge_base/agent_kb.db ".tables"
   # Should show: kb_tasks kb_messages kb_decisions ...
   ```
```

---

## 10. UI Theme & Branding

### Color Palette

```
┌─────────────────────────────────────────────────────────────┐
│                     COLOR SYSTEM                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PRIMARY COLORS                                             │
│  ───────────────                                            │
│  Primary:      #2196F3 (Blue)       - Actions, links        │
│  Secondary:    #FF9800 (Orange)     - Accents, highlights   │
│  Accent:       #9C27B0 (Purple)     - Special elements      │
│                                                             │
│  SEMANTIC COLORS                                            │
│  ───────────────                                            │
│  Success:      #4CAF50 (Green)      - Completed, positive   │
│  Warning:      #FFC107 (Amber)      - Caution, pending      │
│  Error:        #F44336 (Red)        - Failed, critical      │
│  Info:         #2196F3 (Blue)       - Informational         │
│                                                             │
│  BACKGROUND (Dark Theme)                                    │
│  ───────────────────────                                    │
│  Background:   #121212              - Main background       │
│  Surface:      #1E1E1E              - Cards, panels         │
│  Elevated:     #2D2D2D              - Raised elements       │
│                                                             │
│  BACKGROUND (Light Theme)                                   │
│  ────────────────────────                                   │
│  Background:   #FAFAFA              - Main background       │
│  Surface:      #FFFFFF              - Cards, panels         │
│  Elevated:     #F5F5F5              - Raised elements       │
│                                                             │
│  TEXT                                                       │
│  ────                                                       │
│  Primary:      87% opacity          - Main text             │
│  Secondary:    60% opacity          - Subtitles, hints      │
│  Disabled:     38% opacity          - Inactive elements     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Typography (Hardcoded Fonts)

```dart
// NEVER use system fonts - always use these hardcoded fonts

/// Primary Font Family - For all UI text
static const String fontFamily = 'Inter';

/// Monospace Font - For code, data, numbers
static const String monoFontFamily = 'JetBrains Mono';

/// Display Font - For headings (optional)
static const String displayFontFamily = 'Poppins';
```

### Font Sizes (Hardcoded)

```dart
/// Font Sizes - Use these exact values
class AppFontSizes {
  // Headings
  static const double h1 = 32.0;
  static const double h2 = 24.0;
  static const double h3 = 20.0;
  static const double h4 = 18.0;

  // Body
  static const double bodyLarge = 16.0;
  static const double body = 14.0;
  static const double bodySmall = 12.0;

  // Labels
  static const double label = 14.0;
  static const double labelSmall = 12.0;
  static const double caption = 10.0;
}
```

### Spacing System (Hardcoded)

```dart
/// Spacing - Use multiples of 4
class AppSpacing {
  static const double xs = 4.0;    // Extra small
  static const double sm = 8.0;    // Small
  static const double md = 16.0;   // Medium (default)
  static const double lg = 24.0;   // Large
  static const double xl = 32.0;   // Extra large
  static const double xxl = 48.0;  // 2x Extra large
}
```

### Border Radius (Hardcoded)

```dart
/// Border Radius - Consistent rounded corners
class AppRadius {
  static const double none = 0.0;
  static const double sm = 4.0;
  static const double md = 8.0;
  static const double lg = 12.0;
  static const double xl = 16.0;
  static const double full = 999.0;  // Pill shape
}
```

### Theme Constants File

Create this file in every project:

```dart
// lib/constants/theme_constants.dart

/// App Colors - Hardcoded for consistency
class AppColors {
  // Primary
  static const Color primary = Color(0xFF2196F3);
  static const Color secondary = Color(0xFFFF9800);
  static const Color accent = Color(0xFF9C27B0);

  // Semantic
  static const Color success = Color(0xFF4CAF50);
  static const Color warning = Color(0xFFFFC107);
  static const Color error = Color(0xFFF44336);

  // Background
  static Color background(bool isDark) =>
      isDark ? const Color(0xFF121212) : const Color(0xFFFAFAFA);
  static Color surface(bool isDark) =>
      isDark ? const Color(0xFF1E1E1E) : Colors.white;

  // Text
  static Color textPrimary(bool isDark) =>
      isDark ? Colors.white.withOpacity(0.87) : Colors.black.withOpacity(0.87);
  static Color textSecondary(bool isDark) =>
      isDark ? Colors.white.withOpacity(0.60) : Colors.black.withOpacity(0.60);
}

/// Text Styles - Hardcoded fonts
class AppTextStyles {
  static const String _fontFamily = 'Inter';
  static const String _monoFamily = 'JetBrains Mono';

  static TextStyle heading1(bool isDark) => TextStyle(
    fontFamily: _fontFamily,
    fontSize: 32,
    fontWeight: FontWeight.bold,
    color: AppColors.textPrimary(isDark),
  );

  static TextStyle heading2(bool isDark) => TextStyle(
    fontFamily: _fontFamily,
    fontSize: 24,
    fontWeight: FontWeight.w600,
    color: AppColors.textPrimary(isDark),
  );

  static TextStyle body(bool isDark) => TextStyle(
    fontFamily: _fontFamily,
    fontSize: 14,
    color: AppColors.textPrimary(isDark),
  );

  static TextStyle code(bool isDark) => TextStyle(
    fontFamily: _monoFamily,
    fontSize: 13,
    color: AppColors.textPrimary(isDark),
  );
}
```

### Branding Elements

```
┌─────────────────────────────────────────────────────────────┐
│                     BRANDING RULES                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PROJECT NAME FORMAT                                        │
│  ───────────────────                                        │
│  Full:     "Fokha Trading System"                           │
│  Short:    "Fokha" or "FTS"                                 │
│  Version:  "v2.0.3" (lowercase v)                           │
│                                                             │
│  AGENT NAMING                                               │
│  ────────────                                               │
│  Format:   UPPERCASE_WITH_UNDERSCORES                       │
│  Examples: CLAUDE_CODE, US_PY, MT5_EA, AI_STUDIO            │
│                                                             │
│  FILE NAMING                                                │
│  ───────────                                                │
│  Workflow: fokha_{purpose}_v{version}.json                  │
│  Config:   fokha_{type}_config.json                         │
│  Model:    {type}_{symbol}.joblib                           │
│                                                             │
│  LOGO USAGE                                                 │
│  ──────────                                                 │
│  Primary:  Logo with text (horizontal)                      │
│  Icon:     Logo mark only (square, for favicons)            │
│  Minimum:  32x32px for icon, 120px width for full           │
│                                                             │
│  API RESPONSES                                              │
│  ─────────────                                              │
│  Always include:                                            │
│  - "success": true/false                                    │
│  - "version": "2.0.3"                                       │
│  - "timestamp": ISO 8601 format                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Cross-Platform Consistency

| Platform | Font | Fallback |
|----------|------|----------|
| Flutter | Inter | -apple-system, Roboto |
| Web | Inter | system-ui, sans-serif |
| Terminal | JetBrains Mono | Consolas, monospace |
| Docs | GitHub system font | -apple-system |

### Icon System

```dart
// Use Material Icons consistently
// Prefix with Icons. in Flutter

// Common icons:
Icons.check_circle      // Success, done
Icons.error             // Error, failed
Icons.warning           // Warning
Icons.info              // Information
Icons.refresh           // Reload, retry
Icons.settings          // Configuration
Icons.storage           // Database, KB
Icons.send              // Send, submit
Icons.code              // Code, development
Icons.analytics         // Charts, data
```

### Button Styles

```dart
// Primary action (filled)
ElevatedButton(
  style: ElevatedButton.styleFrom(
    backgroundColor: AppColors.primary,
    foregroundColor: Colors.white,
    padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(8),
    ),
  ),
)

// Secondary action (outlined)
OutlinedButton(
  style: OutlinedButton.styleFrom(
    foregroundColor: AppColors.primary,
    side: BorderSide(color: AppColors.primary),
  ),
)

// Text action (no background)
TextButton(
  style: TextButton.styleFrom(
    foregroundColor: AppColors.primary,
  ),
)
```

---

## 11. Checklist

Before finalizing any prompt or documentation:

- [ ] Clear title with version if applicable
- [ ] Overview section explaining purpose
- [ ] Consistent terminology (see Section 4)
- [ ] Code blocks have language specified
- [ ] Tables are properly formatted
- [ ] Horizontal rules between major sections
- [ ] ASCII diagrams use box-drawing characters
- [ ] Direct, imperative voice
- [ ] All required sections present (for prompts)
- [ ] Examples are complete and runnable
