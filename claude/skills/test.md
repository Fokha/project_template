# Run Tests

Execute test suites for the project.

## Quick Test Commands

```bash
# Run all tests
{{TEST_ALL_CMD}}

# Run fast/smoke tests
{{TEST_SMOKE_CMD}}

# Run with coverage
{{TEST_COVERAGE_CMD}}

# Run specific test file
{{TEST_SPECIFIC_CMD}}
```

## Test Categories

| Category | Description | Command |
|----------|-------------|---------|
| Unit | Individual functions/classes | `{{TEST_UNIT_CMD}}` |
| Integration | Component interaction | `{{TEST_INTEGRATION_CMD}}` |
| E2E | Full user flows | `{{TEST_E2E_CMD}}` |
| Smoke | Quick validation | `{{TEST_SMOKE_CMD}}` |

## Test Structure

```
tests/
├── unit/                 # Unit tests
│   ├── {{FOLDER_1}}/
│   └── {{FOLDER_2}}/
├── integration/          # Integration tests
├── e2e/                  # End-to-end tests
└── fixtures/             # Test data
```

## Coverage Requirements

| Type | Minimum Coverage |
|------|------------------|
| Unit Tests | 80% |
| Integration | 60% |
| Overall | 75% |

## Before Committing

Always run tests before committing:

```bash
# Quick validation
{{TEST_SMOKE_CMD}}

# If changing critical code
{{TEST_ALL_CMD}}
```

## Debugging Failed Tests

```bash
# Run single test with verbose output
{{TEST_VERBOSE_CMD}}

# Run with debugger
{{TEST_DEBUG_CMD}}
```

## CI/CD Integration

Tests run automatically on:
- Pull request creation
- Push to main/develop
- Scheduled (nightly)
