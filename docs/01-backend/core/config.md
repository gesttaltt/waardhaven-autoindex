# Configuration Management

## Overview
The configuration module (`app/core/config.py`) manages all application settings using Pydantic's BaseSettings for type validation and environment variable loading.

## Location
`apps/api/app/core/config.py`

## Configuration Class Structure

### Core Settings
```python
class Settings(BaseSettings):
    # Authentication
    SECRET_KEY: str  # JWT signing key (required)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Database
    DATABASE_URL: str  # PostgreSQL connection (required)
    
    # Server
    PORT: int = 10000  # Default for Render
    
    # Admin Security
    ADMIN_TOKEN: str = ""  # Required in production (min 32 chars)
```

### Market Data Configuration
- `ASSET_DEFAULT_START`: "2018-01-01" - Default historical data start
- `SP500_TICKER`: "^GSPC" - S&P 500 benchmark symbol
- `DAILY_DROP_THRESHOLD`: -0.01 - Alert threshold for daily drops

### TwelveData API Settings
- `TWELVEDATA_API_KEY`: API key for market data
- `TWELVEDATA_PLAN`: Plan type (free/grow/pro)
- `TWELVEDATA_RATE_LIMIT`: API credits per minute
- `ENABLE_MARKET_DATA_CACHE`: Cache market data flag
- `REFRESH_MODE`: Data refresh strategy (auto/full/minimal/cached)

### Redis & Caching
- `REDIS_URL`: Redis connection string
- `CACHE_TTL_SECONDS`: 300 (5 minutes)
- `CACHE_TTL_LONG_SECONDS`: 3600 (1 hour)

### Additional Settings
- `DEBUG`: Debug mode flag
- `FRONTEND_URL`: Frontend URL for CORS
- `SKIP_STARTUP_REFRESH`: Skip initial data refresh

## Environment Variables

### Required in Production
| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key | 32+ character random string |
| `DATABASE_URL` | PostgreSQL URL | postgresql://user:pass@host/db |
| `ADMIN_TOKEN` | Admin auth token | 32+ character random string |
| `TWELVEDATA_API_KEY` | Market data API | Your API key |

### Optional Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 10000 | Server port |
| `DEBUG` | False | Debug mode |
| `REDIS_URL` | "" | Redis connection |
| `REFRESH_MODE` | "auto" | Refresh strategy |
| `CACHE_TTL_SECONDS` | 300 | Short cache TTL |
| `FRONTEND_URL` | "" | Frontend URL |

## Security Features

### Production Validation
```python
if os.getenv("RENDER") or os.getenv("PRODUCTION"):
    if not settings.ADMIN_TOKEN or len(settings.ADMIN_TOKEN) < 32:
        warnings.warn("ADMIN_TOKEN is not secure!")
```

### Security Requirements
1. SECRET_KEY minimum 32 characters
2. ADMIN_TOKEN minimum 32 characters in production
3. DEBUG must be False in production
4. Use strong passwords for database

## Configuration Loading

### Priority Order
1. Environment variables (highest)
2. `.env` file values
3. Default values in class

### Extra Field Handling
```python
class Config:
    env_file = ".env"
    extra = "ignore"  # Ignore unknown fields
```

## Usage Examples

### Basic Usage
```python
from app.core.config import settings

# Access settings
api_key = settings.TWELVEDATA_API_KEY
debug = settings.DEBUG
cache_ttl = settings.CACHE_TTL_SECONDS
```

### Conditional Logic
```python
if settings.DEBUG:
    # Development only code
    logger.setLevel(logging.DEBUG)

if settings.REDIS_URL:
    # Redis is available
    enable_caching()
```

## Refresh Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `auto` | Smart refresh with rate limiting | Production default |
| `full` | Complete data refresh | Initial setup |
| `minimal` | Only essential updates | Low API credits |
| `cached` | Prefer cached data | Development/testing |

## Cache Configuration

### TTL Strategy
- Short TTL (5 min): Frequently changing data
- Long TTL (1 hour): Stable data like historical prices
- User-specific caching with isolation

### Redis Features
- Connection pooling
- Graceful fallback
- Used for caching and Celery tasks

## TwelveData Plans

| Plan | Credits/min | Use Case |
|------|-------------|----------|
| free | 8 | Development |
| grow | 120 | Small production |
| pro | 1200 | Large production |
| enterprise | Custom | High volume |

## Best Practices

### Security
1. Generate strong random keys: `openssl rand -hex 32`
2. Use different keys per environment
3. Rotate keys regularly
4. Never commit `.env` files

### Performance
1. Enable Redis in production
2. Choose appropriate refresh mode
3. Configure database pooling
4. Monitor API credit usage

### Development
1. Copy `.env.example` to `.env`
2. Use minimal refresh mode for testing
3. Enable DEBUG for detailed logs
4. Use SQLite for unit tests

## Error Handling

### Validation Errors
- Missing required fields raise errors
- Invalid types are caught by Pydantic
- Clear error messages provided

### Warnings
- Insecure production configs
- Missing optional services
- Deprecation notices

## Dependencies
- `pydantic-settings`: Configuration management
- `python-dotenv`: Environment file loading
- `pydantic`: Type validation

## Related Modules
- `database.py`: Uses DATABASE_URL
- `redis_client.py`: Uses REDIS_URL
- `celery_app.py`: Uses Redis configuration
- All routers: Use various settings