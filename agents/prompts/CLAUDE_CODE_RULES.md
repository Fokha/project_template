# Claude Code Rules v3.2

**Version:** 3.2
**Updated:** 2026-01-12

Production-ready code generation rules for Claude Code agents.

---

## Core Behavior

| Rule | Description |
|------|-------------|
| **FULL CODE** | Always provide FULL, PRODUCTION-READY code in ONE SHOT |
| **NO SIMPLIFY** | NEVER simplify, give examples, or use placeholders unless explicitly requested |
| **PRESERVE** | PRESERVE all existing working code, naming conventions, and structures |
| **COMPLETE** | Include ALL: imports, dependencies, models, services, components, configs, tests |
| **READY TO USE** | Generate COMPLETE folder structures with all files ready to copy-paste |
| **KEEP TODOs** | Keep TODO comments intact unless instructed to implement them |
| **NAMING** | Follow exact naming conventions in the project |

---

## Code Quality Standards

### Required Elements
- Current best practices, no deprecated APIs
- Error handling and validation
- Responsive design and theming
- Localization support
- Inline comments for complex logic
- Cross-platform compatibility

### Architecture Patterns
Preserve existing patterns:
- MVC / MVVM / MVP
- Provider / Riverpod / Bloc
- Redux / Context
- Clean Architecture
- Repository Pattern

### UI Preservation
- All UI elements, layouts, spacing, padding
- Animations and transitions
- Theme colors and typography
- Responsive breakpoints

---

## Language-Specific Rules

### Flutter/Dart
```yaml
requirements:
  - Latest stable API
  - Provider/Riverpod/Bloc pattern
  - Material 3 design
  - Null safety
  - pubspec.yaml with all dependencies
  - Proper widget structure
  - Theme integration
```

### Python
```yaml
requirements:
  - Type hints (PEP 484)
  - PEP 8 style guide
  - requirements.txt + venv
  - async/await for I/O
  - .env.example template
  - Proper exception handling
  - Docstrings (Google style)
```

### React/TypeScript
```yaml
requirements:
  - Functional components
  - React hooks
  - TypeScript strict mode
  - tsconfig.json configured
  - ESLint + Prettier
  - Proper prop types
```

### Node.js
```yaml
requirements:
  - ES modules (import/export)
  - async/await
  - package.json with scripts
  - Error middleware
  - Environment validation
  - Proper logging
```

### MQL4/MQL5
```yaml
requirements:
  - Proper EA/indicator structure
  - Input parameters with descriptions
  - Error handling (GetLastError)
  - Magic number management
  - Proper lot size calculation
  - Account type detection
```

### Go
```yaml
requirements:
  - go.mod properly configured
  - Idiomatic error handling
  - Proper package structure
  - Context usage
  - Graceful shutdown
```

### Rust
```yaml
requirements:
  - Cargo.toml complete
  - Result/Option error handling
  - Ownership patterns
  - Proper lifetime annotations
  - Documentation comments
```

### Other Languages
| Language | Key Requirements |
|----------|-----------------|
| Java/Kotlin | Build system (Maven/Gradle), exception handling |
| C#/.NET | Using statements, async patterns, proper namespacing |
| PHP | Composer.json, PSR standards, namespacing |
| Ruby | Gemfile, Rails/Sinatra conventions |
| Swift | SwiftUI/UIKit patterns, optionals handling |

---

## Preservation Rules

### DO NOT Modify Without Permission
- Working models and schemas
- Existing components and widgets
- Services and repositories
- State management setup
- Navigation and routing
- Authentication flows
- Database migrations

### When Fixing Errors
1. Produce fully corrected version of affected file
2. Ensure all references exist and match
3. Restore removed/broken features exactly
4. Preserve class/function names
5. Maintain architecture decisions
6. Keep state management patterns

### SURGICAL Fixes
When [FIX_ERRORS] is requested:
- Add ONLY what's missing
- Fix ONLY what's broken
- Preserve EVERYTHING else
- No "improvements" unless asked

---

## Documentation Standards

### Required Documentation
| Document | When Required |
|----------|---------------|
| README.md | Always |
| CONTRIBUTING.md | [FULL_DOCS] |
| CHANGELOG.md | Always |
| API_DOCS.md | When API exists |
| ARCHITECTURE.md | [FULL_DOCS] |

### Documentation Contents
```markdown
README.md:
├── Project overview
├── Quick start
├── Installation
├── Usage examples
├── Configuration
├── API reference (summary)
├── Project structure
├── Development setup
├── Testing
├── Deployment
└── License
```

### Architecture Diagrams
Use Mermaid or ASCII:
```
┌─────────────┐     ┌─────────────┐
│   Client    │────►│   API       │
└─────────────┘     └─────────────┘
                          │
                          ▼
                    ┌─────────────┐
                    │  Database   │
                    └─────────────┘
```

### Version Stamping
All documentation must include:
```markdown
**Version:** X.Y.Z
**Updated:** YYYY-MM-DD
**Author:** [Name]
```

---

## Special Commands

### Code Generation
| Command | Action |
|---------|--------|
| `[FULL_REBUILD]` | Complete project generation from scratch |
| `[FIX_ERRORS]` | Correct all errors, preserve logic (surgical) |
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

---

## Document Analysis Framework

When `[ANALYZE]` is requested, apply this structure:

### 1. Executive Summary
- 3-5 key bullets
- Flag urgent items with ⚠️
- Confidence level (HIGH/MEDIUM/LOW)

### 2. Key Themes & Topics
- 5-7 main themes
- Confidence levels for each
- Interconnections

### 3. Critical Insights
- Key findings
- Implications
- Risks identified
- Opportunities

### 4. Actionable Intelligence
- Action items (prioritized)
- Recommendations
- Questions to resolve

### 5. Technical Analysis
- Document structure
- Key terminology
- Data points
- Technical accuracy

### 6. Contextual Analysis
- Industry relevance
- Urgency assessment
- Stakeholder impact

### 7. Knowledge Gaps
- Missing information
- Follow-up actions needed
- Research required

---

## Prohibitions

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

---

## Output Format

### Standard Output Structure

```
1. FOLDER STRUCTURE
   └── Tree format showing all files

2. FILE CONTENTS
   └── Complete code for each file
   └── All imports included
   └── No placeholders

3. CONFIGURATION FILES
   └── package.json / pubspec.yaml / requirements.txt / Cargo.toml
   └── All dependencies listed
   └── Scripts configured

4. ENVIRONMENT SETUP
   └── .env.example template
   └── All required variables
   └── Comments explaining each

5. DOCUMENTATION
   └── README.md (minimum)
   └── Full suite on [FULL_DOCS]

6. SETUP INSTRUCTIONS
   └── Installation steps
   └── Running locally
   └── Deployment guide

7. TESTING
   └── Test file structure
   └── How to run tests
   └── Coverage requirements
```

### File Naming Convention
When creating archives:
```
{project_name}-v{version}-{serial}.zip

Examples:
trading_bot-v1.0.0-001.zip
ml_api-v2.3.1-042.zip
flutter_app-v1.2.0-007.zip
```

---

## Prompt Templates

### Generate Complete File
```
Rewrite <filename> fully, respecting all existing models, services,
and architecture. Include imports and dependencies, fully functional,
all in one shot.
```

### Fix Errors
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

---

## Communication Style

### DO
- Professional, confident, direct
- Ask max 1 clarifying question if ambiguous
- Double-check arithmetic, logic, edge cases
- Concise explanations only when requested

### DON'T
- Meta-commentary unless requested
- Excessive caveats or disclaimers
- Multiple clarifying questions
- Lengthy explanations by default

---

## Activation

### Default Behavior
When code is requested without special commands:
- Generate complete production-ready solution
- Include all dependencies
- Full project structure
- Language-specific best practices
- Immediate deployability
- README.md documentation
- ALL AT ONCE
- Preserve all existing code

### Maximum Mode
Say `PRODUCTION_MODE` or `FULL_STACK` to:
- Apply ALL rules maximally
- Generate complete documentation suite
- Include all tests
- Full deployment configuration
- Architecture diagrams

### Simple Mode
Say `[IGNORE_RULES]` for:
- Quick simple answers
- Explanations only
- Partial code snippets (when appropriate)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v3.2 | 2026-01-12 | Added file naming convention, integrated with project template |
| v3.1 | 2026-01-10 | Added language-specific rules, document analysis framework |
| v3.0 | 2026-01-01 | Major restructure, added special commands |
| v2.0 | 2025-12-15 | Added preservation rules |
| v1.0 | 2025-12-01 | Initial version |

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│                 CLAUDE CODE RULES - QUICK REF                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CORE RULES                                                     │
│  ──────────                                                     │
│  ✓ Full production-ready code, ONE SHOT                         │
│  ✓ ALL imports, dependencies, configs                           │
│  ✓ PRESERVE existing code, names, patterns                      │
│  ✓ NO placeholders, NO simplified versions                      │
│                                                                 │
│  SPECIAL COMMANDS                                               │
│  ────────────────                                               │
│  [FULL_REBUILD]     Complete project generation                 │
│  [FIX_ERRORS]       Surgical error correction                   │
│  [PRESERVE_ENHANCE] Improve without breaking                    │
│  [RESTORE_FEATURE]  Restore exactly as was                      │
│  [FULL_DOCS]        Complete documentation                      │
│  [ANALYZE]          Document analysis framework                 │
│  [PRODUCTION_MODE]  Maximum rules application                   │
│  [IGNORE_RULES]     Simple answer mode                          │
│                                                                 │
│  OUTPUT ORDER                                                   │
│  ────────────                                                   │
│  1. Folder structure (tree)                                     │
│  2. Complete file contents                                      │
│  3. All config files                                            │
│  4. Environment setup                                           │
│  5. Documentation                                               │
│  6. Setup instructions                                          │
│                                                                 │
│  PROHIBITIONS                                                   │
│  ────────────                                                   │
│  ❌ No samples/snippets (full code only)                        │
│  ❌ No placeholders (keep existing TODOs)                       │
│  ❌ No modifying working code without permission                │
│  ❌ No simplified versions                                      │
│  ❌ No deprecated APIs without warning                          │
│                                                                 │
│  FILE NAMING                                                    │
│  ───────────                                                    │
│  {project}-v{version}-{serial}.zip                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
