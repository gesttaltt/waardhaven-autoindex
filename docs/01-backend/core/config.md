# Configuration Module

## Overview
The config module manages application settings and environment variables for the backend API.

## Location
`apps/api/app/core/config.py`

## Purpose
Centralizes configuration management using Pydantic settings for type safety and validation.

## Key Components

### Settings Class
Manages all application configuration:
- Database connection strings
- API keys and secrets
- JWT configuration
- Application metadata

### Environment Variables
- **DATABASE_URL**: PostgreSQL connection string
- **SECRET_KEY**: JWT signing key
- **TWELVEDATA_API_KEY**: Market data API key
- **NODE_ENV**: Environment (development/production)
- **ALLOWED_ORIGINS**: CORS allowed origins

## Configuration Loading
- Automatically loads from environment
- Supports .env files
- Type validation
- Default values

## Usage
```python
from app.core.config import settings

api_key = settings.TWELVEDATA_API_KEY
db_url = settings.DATABASE_URL
```

## Security Considerations
- Never commit secrets to version control
- Use environment variables
- Rotate keys regularly
- Different keys for each environment

## Dependencies
- pydantic: Settings management
- python-dotenv: .env file support

## Related Modules
- database.py: Uses DATABASE_URL
- security.py: Uses SECRET_KEY
- twelvedata.py: Uses TWELVEDATA_API_KEY