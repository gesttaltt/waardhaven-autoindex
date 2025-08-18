# Backend Development Tools

**Last Updated**: 2025-01-18  
**Status**: ✅ Active

## Overview

This document outlines the development tools and practices for the Waardhaven AutoIndex backend (FastAPI/Python).

## Code Quality Tools

### Formatting

**Black** - The uncompromising Python code formatter
- Version: 24.3.0
- Configuration: Default (88 char line length)
- Usage:
  ```bash
  # Format all files
  black .
  
  # Check formatting (CI mode)
  black --check .
  
  # Format specific file
  black app/main.py
  ```

### Linting

**Ruff** - An extremely fast Python linter
- Version: 0.3.4
- Features: 500+ lint rules, 10-100x faster than alternatives
- Usage:
  ```bash
  # Check for issues
  ruff check .
  
  # Auto-fix issues
  ruff check . --fix
  
  # Check specific file
  ruff check app/main.py
  ```

### Type Checking

**MyPy** - Static type checker for Python
- Version: 1.9.0
- Configuration: `--ignore-missing-imports`
- Usage:
  ```bash
  # Type check entire app
  mypy app --ignore-missing-imports
  
  # Strict mode
  mypy app --strict
  ```

## Testing Tools

### Test Framework

**Pytest** - Full-featured Python testing tool
- Version: 8.1.1
- Plugins:
  - pytest-cov (4.1.0) - Coverage reporting
  - pytest-asyncio (0.23.5) - Async test support
- Usage:
  ```bash
  # Run all tests
  pytest
  
  # Run with coverage
  pytest --cov=app --cov-report=html
  
  # Run specific test
  pytest tests/test_api.py::test_health_check
  
  # Run with verbose output
  pytest -v
  ```

### Running Tests

```bash
# Using npm scripts (recommended)
npm run test:api
npm run test:api:coverage
npm run test:api:unit
npm run test:api:integration

# Direct pytest
cd apps/api
pytest tests/ -v --cov=app
```

## Development Dependencies

### Installation

```bash
# Production dependencies only
pip install -r requirements.txt

# Development dependencies
pip install -r requirements-dev.txt

# All test dependencies
pip install -r requirements-test.txt
```

### Files

**requirements.txt** - Production dependencies
- FastAPI, SQLAlchemy, PostgreSQL drivers
- Authentication (passlib, python-jose)
- Market data (twelvedata)
- Background tasks (celery, redis)
- **Black** (for production formatting checks)

**requirements-dev.txt** - Development tools
```
pre-commit==3.6.2
pytest==8.1.1
pytest-cov==4.1.0
pytest-asyncio==0.23.5
ruff==0.3.4
mypy==1.9.0
```

**requirements-test.txt** - Testing dependencies
```
pytest==8.1.1
pytest-cov==4.1.0
pytest-asyncio==0.23.5
httpx==0.27.0
```

## Pre-commit Hooks

### Setup

```bash
# Automated setup (recommended)
bash apps/api/scripts/setup-pre-commit.sh

# Manual setup
pip install pre-commit
pre-commit install
```

### Configuration

Pre-commit runs automatically on `git commit`:
1. Black - Formats Python code
2. Ruff - Lints and fixes issues
3. General checks - Trailing whitespace, YAML/JSON validation

### Manual Run

```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
```

## IDE Configuration

### VS Code

**.vscode/settings.json**
```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.linting.mypyEnabled": true
}
```

### PyCharm

1. Settings → Tools → Black
   - Configure path to Black
   - Enable "On Save"

2. Settings → Tools → External Tools
   - Add Ruff as external tool
   - Add MyPy as external tool

## Scripts

### Setup Scripts

Located in `apps/api/scripts/`:

**setup-pre-commit.sh** (Unix/Linux/macOS)
```bash
#!/bin/bash
# Installs pre-commit hooks
bash apps/api/scripts/setup-pre-commit.sh
```

**setup-pre-commit.bat** (Windows)
```batch
@echo off
REM Installs pre-commit hooks
apps\api\scripts\setup-pre-commit.bat
```

### Utility Scripts

**run_tests.sh** / **run_tests.bat**
- Runs full test suite with coverage
- Generates HTML coverage report

**startup.sh**
- Database initialization
- Migrations
- Asset seeding

## CI/CD Integration

### GitHub Actions

The CI pipeline enforces all quality checks:

```yaml
# From .github/workflows/ci-cd.yml
- name: Lint Python (API)
  run: |
    pip install -r requirements.txt
    pip install ruff mypy
    ruff check .
    black --check .  # Fails if not formatted
    mypy app --ignore-missing-imports
```

### Local CI Simulation

Check if your code will pass CI:

```bash
# Run all checks
black --check .
ruff check .
mypy app --ignore-missing-imports
pytest tests/ -v

# Or use pre-commit
pre-commit run --all-files
```

## Database Tools

### Alembic (Planned)

Database migration tool for SQLAlchemy
```bash
# Initialize migrations
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add user table"

# Apply migrations
alembic upgrade head
```

### Database Scripts

**db_init.py**
- Creates tables
- Runs migrations
- Seeds initial data

**seed_assets.py**
- Populates asset data
- Market data initialization

## Background Task Tools

### Celery

Distributed task queue
```bash
# Start worker
celery -A app.core.celery_app worker --loglevel=info

# Start beat scheduler
celery -A app.core.celery_app beat --loglevel=info

# Monitor with Flower
celery -A app.core.celery_app flower --port=5555
```

### Redis

In-memory data store for caching and queues
```bash
# Check Redis connection
redis-cli ping

# Monitor Redis
redis-cli monitor

# Clear cache
redis-cli FLUSHDB
```

## Debugging Tools

### IPython/IPdb

Interactive debugging
```python
# Add breakpoint
import ipdb; ipdb.set_trace()

# Or in Python 3.7+
breakpoint()
```

### Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### FastAPI Debugging

```bash
# Run with reload and debug
uvicorn app.main:app --reload --log-level debug

# With custom host/port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Performance Tools

### Profiling

```python
# cProfile
python -m cProfile -o profile.stats app/main.py

# View results
python -m pstats profile.stats
```

### Load Testing

**Locust** - Load testing tool
```python
# locustfile.py
from locust import HttpUser, task

class APIUser(HttpUser):
    @task
    def get_index(self):
        self.client.get("/api/v1/index")
```

```bash
# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

## Security Tools

### Bandit

Security linter for Python
```bash
# Install
pip install bandit

# Run security scan
bandit -r app/
```

### Safety

Check dependencies for vulnerabilities
```bash
# Install
pip install safety

# Check dependencies
safety check -r requirements.txt
```

## Documentation Tools

### Swagger/OpenAPI

FastAPI automatically generates OpenAPI documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### Docstrings

Use Google-style docstrings:
```python
def calculate_return(initial: float, final: float) -> float:
    """Calculate investment return percentage.
    
    Args:
        initial: Initial investment value
        final: Final investment value
        
    Returns:
        Return percentage as decimal
        
    Raises:
        ValueError: If initial value is zero
    """
```

## Best Practices

1. **Always Format Before Commit**: Use pre-commit hooks
2. **Run Tests Locally**: Don't rely on CI to catch errors
3. **Type Hints**: Use type hints for better IDE support
4. **Document Code**: Write clear docstrings
5. **Keep Dependencies Updated**: Regular security updates
6. **Use Virtual Environments**: Isolate project dependencies
7. **Follow PEP 8**: Python style guide (enforced by Black)
8. **Write Tests First**: TDD when possible
9. **Profile Before Optimizing**: Measure performance
10. **Security First**: Regular vulnerability scans

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure PYTHONPATH includes project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Database Connection Issues**
```bash
# Check PostgreSQL is running
pg_isready

# Check connection string
echo $DATABASE_URL
```

**Redis Connection Issues**
```bash
# Check Redis is running
redis-cli ping

# Check Redis URL
echo $REDIS_URL
```

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)