# Code Formatting and Linting

This project uses automated code formatting and linting to ensure consistent code quality.

## Tools Used

### Backend (Python)
- **Black**: Code formatter with --check in CI
- **Ruff**: Fast linter with auto-fix capabilities
- **MyPy**: Static type checking

### Frontend (TypeScript/React)
- **Prettier**: Code formatter with --check in CI
- **ESLint**: Linter with Next.js configuration

## Setup

### 1. Install Pre-commit Hooks (Recommended)

```bash
# From project root
bash apps/api/scripts/setup-pre-commit.sh

# Or on Windows
apps\api\scripts\setup-pre-commit.bat
```

### 2. Manual Setup

```bash
# Install pre-commit globally
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files (optional)
pre-commit run --all-files
```

## Usage

### Local Development (Auto-fix)

```bash
# Python (Backend)
cd apps/api
black .                    # Format code
ruff check . --fix        # Lint and auto-fix
mypy app --ignore-missing-imports

# Frontend
cd apps/web
npm run format             # Format with Prettier
npm run lint               # Lint with ESLint (auto-fix where possible)
```

### CI/CD (Check-only)

The GitHub Actions workflow runs these commands that FAIL on formatting issues:

```bash
# Python
black --check .            # Fails if code needs formatting
ruff check .               # Fails on lint issues

# Frontend  
npm run format:check       # Fails if code needs formatting
npm run lint:check         # Fails on lint issues (max 0 warnings)
```

## Pre-commit Hooks

When you commit, the following hooks automatically run:

1. **Black** - Formats Python code
2. **Ruff** - Lints and fixes Python code
3. **Prettier** - Formats frontend files
4. **General** - Removes trailing whitespace, fixes end-of-file, checks YAML/JSON

## Configuration Files

- `.pre-commit-config.yaml` - Pre-commit hook configuration
- `apps/api/requirements-dev.txt` - Development dependencies
- `apps/web/package.json` - Frontend formatting scripts

## GitHub Actions Integration

The CI pipeline enforces formatting rules:

1. **Development**: Pre-commit hooks auto-fix locally
2. **CI/CD**: `--check` flags ensure code is properly formatted
3. **Deployment**: Only properly formatted code gets deployed

## Troubleshooting

### Pre-commit Hook Fails
```bash
# Run manually to see issues
pre-commit run --all-files

# Skip hooks temporarily (not recommended)
git commit --no-verify
```

### CI Formatting Failures
```bash
# Fix locally then push
cd apps/api && black .
cd apps/web && npm run format
git add -A && git commit -m "Fix formatting"
```