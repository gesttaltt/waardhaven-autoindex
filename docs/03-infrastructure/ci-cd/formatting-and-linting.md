# Code Formatting and Linting Guide

**Last Updated**: 2025-01-18  
**Status**: ✅ Fully Implemented

## Overview

Waardhaven AutoIndex uses automated code formatting and linting to ensure consistent code quality across the entire codebase. The system enforces strict formatting rules in CI/CD while providing auto-fix capabilities for local development.

## Tools and Technologies

### Backend (Python)

| Tool | Purpose | CI Behavior | Local Behavior |
|------|---------|-------------|----------------|
| **Black** | Code formatter | `--check` (fails on issues) | Auto-formats code |
| **Ruff** | Fast linter | `check` (fails on issues) | `--fix` for auto-fix |
| **MyPy** | Type checker | Reports type errors | Same as CI |

### Frontend (TypeScript/React)

| Tool | Purpose | CI Behavior | Local Behavior |
|------|---------|-------------|----------------|
| **Prettier** | Code formatter | `--check` (fails on issues) | Auto-formats code |
| **ESLint** | Linter | `--max-warnings 0` | Auto-fix where possible |
| **TypeScript** | Type checker | `tsc --noEmit` | Same as CI |

## Configuration Files

```
waardhaven-autoindex/
├── .pre-commit-config.yaml      # Pre-commit hook configuration
├── FORMATTING.md                 # User-facing formatting guide
├── apps/
│   ├── api/
│   │   ├── requirements.txt     # Includes Black
│   │   ├── requirements-dev.txt # Development tools
│   │   └── scripts/
│   │       ├── setup-pre-commit.sh  # Unix setup script
│   │       └── setup-pre-commit.bat # Windows setup script
│   └── web/
│       └── package.json         # Includes Prettier and scripts
```

## GitHub Actions Integration

### CI/CD Workflow Changes

The `lint-and-format` job in `.github/workflows/ci-cd.yml`:

```yaml
- name: Lint Python (API)
  if: matrix.component == 'api'
  working-directory: ./apps/api
  run: |
    pip install -r requirements.txt
    pip install ruff mypy
    ruff check .
    black --check .  # Fails if formatting needed
    mypy app --ignore-missing-imports

- name: Lint TypeScript (Web)
  if: matrix.component == 'web'
  working-directory: ./apps/web
  run: |
    npm ci
    npm run lint:check      # ESLint with 0 warnings
    npm run format:check    # Prettier check
    npm run type-check
```

## Pre-commit Hooks

### Installation

**Unix/Linux/macOS:**
```bash
bash apps/api/scripts/setup-pre-commit.sh
```

**Windows:**
```cmd
apps\api\scripts\setup-pre-commit.bat
```

### Hook Configuration

The `.pre-commit-config.yaml` includes:

1. **Python Hooks**
   - Black: Formats Python files
   - Ruff: Lints and fixes Python issues

2. **Frontend Hooks**
   - Prettier: Formats JS/TS/JSON/CSS/MD files

3. **General Hooks**
   - Remove trailing whitespace
   - Fix end-of-file
   - Check YAML/JSON syntax
   - Check for merge conflicts
   - Prevent large files (>1MB)

## Development Workflow

### 1. Initial Setup (One-time)

```bash
# Install pre-commit hooks
cd waardhaven-autoindex
bash apps/api/scripts/setup-pre-commit.sh

# Or manually
pip install pre-commit
pre-commit install
```

### 2. Daily Development

**Automatic (Recommended):**
- Pre-commit hooks auto-format on `git commit`
- No manual intervention needed

**Manual Formatting:**
```bash
# Python
cd apps/api
black .                    # Format all Python files
ruff check . --fix        # Fix linting issues

# Frontend
cd apps/web
npm run format            # Format with Prettier
npm run lint              # Lint with ESLint
```

### 3. Before Pushing

**Check CI Will Pass:**
```bash
# Python
cd apps/api
black --check .
ruff check .

# Frontend
cd apps/web
npm run format:check
npm run lint:check
```

## NPM Scripts (Frontend)

Added to `apps/web/package.json`:

```json
{
  "scripts": {
    "lint": "next lint --max-warnings 50",
    "lint:check": "next lint --max-warnings 0",
    "format": "prettier --write \"**/*.{js,jsx,ts,tsx,json,css,md}\"",
    "format:check": "prettier --check \"**/*.{js,jsx,ts,tsx,json,css,md}\"",
    "type-check": "tsc --noEmit"
  }
}
```

## Python Dependencies

Added to `apps/api/requirements.txt`:
- `black==24.3.0` - Code formatter

Created `apps/api/requirements-dev.txt`:
- `pre-commit==3.6.2` - Git hook framework
- `pytest==8.1.1` - Testing framework
- `pytest-cov==4.1.0` - Coverage plugin
- `pytest-asyncio==0.23.5` - Async test support
- `ruff==0.3.4` - Fast Python linter
- `mypy==1.9.0` - Static type checker

## CI/CD Behavior

### Success Criteria

The CI pipeline will **PASS** only when:
1. ✅ All Python code is Black-formatted
2. ✅ No Ruff linting errors
3. ✅ No MyPy type errors (ignoring missing imports)
4. ✅ All frontend code is Prettier-formatted
5. ✅ Zero ESLint warnings or errors
6. ✅ No TypeScript compilation errors

### Failure Examples

The CI pipeline will **FAIL** when:
1. ❌ Python code needs Black formatting
2. ❌ Ruff finds linting issues
3. ❌ Frontend code needs Prettier formatting
4. ❌ ESLint reports any warnings
5. ❌ TypeScript type errors exist

## Troubleshooting

### Pre-commit Hook Failures

**Problem**: Commit is blocked by formatting issues
```bash
# See what's wrong
pre-commit run --all-files

# Skip hooks temporarily (not recommended)
git commit --no-verify
```

### CI Pipeline Failures

**Problem**: GitHub Actions fails on formatting
```bash
# Fix locally
cd apps/api && black .
cd apps/web && npm run format

# Commit fixes
git add -A
git commit -m "Fix formatting"
git push
```

### Black Configuration

Black uses default settings:
- Line length: 88 characters
- Python 3.6+ syntax
- String normalization enabled

To customize, create `pyproject.toml`:
```toml
[tool.black]
line-length = 88
target-version = ['py311']
```

### Prettier Configuration

Prettier uses default settings. To customize, create `.prettierrc`:
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```

## Best Practices

1. **Always Use Pre-commit Hooks**: Set up once, format automatically
2. **Run Checks Before Pushing**: Avoid CI failures
3. **Don't Skip Hooks**: Fix issues instead of bypassing
4. **Keep Tools Updated**: Regular updates for bug fixes
5. **Team Consistency**: Everyone uses same formatter versions

## Benefits

1. **Consistent Code Style**: No more style debates
2. **Automatic Formatting**: Save time on manual formatting
3. **Early Error Detection**: Catch issues before CI
4. **Clean Git History**: No formatting-only commits
5. **Focus on Logic**: Spend time on code, not formatting

## Migration Guide

For existing code with formatting issues:

```bash
# Format entire codebase
cd apps/api
black .
ruff check . --fix

cd ../web
npm run format
npm run lint

# Commit all changes
git add -A
git commit -m "Apply formatting standards to entire codebase"
```

## Future Enhancements

1. **Additional Linters**
   - pylint for deeper Python analysis
   - stylelint for CSS/SCSS
   - commitlint for commit messages

2. **IDE Integration**
   - VS Code settings.json
   - PyCharm configuration
   - Format on save setup

3. **Performance**
   - Incremental formatting
   - Parallel linting
   - Cache optimization

## References

- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Prettier Documentation](https://prettier.io/docs/)
- [ESLint Documentation](https://eslint.org/docs/)
- [Pre-commit Documentation](https://pre-commit.com/)