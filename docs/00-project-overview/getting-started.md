# Getting Started with Waardhaven AutoIndex

## Prerequisites

### Required Software
- Node.js 20+ and npm
- Python 3.11+
- PostgreSQL 14+
- Redis 6+ (optional, for caching and background tasks)
- Docker (optional, for containerized deployment)

### Required API Keys
- **TwelveData**: Market data integration (https://twelvedata.com)
- **MarketAux**: Financial news (optional, https://marketaux.com)
- **Google OAuth**: For social authentication (optional)

## Local Development Setup

### 1. Clone the Repository
```bash
git clone [repository-url]
cd waardhaven-autoindex
```

### 2. Install Dependencies

#### Backend Setup
```bash
cd apps/api

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt  # For testing
```

#### Frontend Setup
```bash
cd apps/web
npm install
```

#### Setup Code Formatting (Recommended)
```bash
# From project root - sets up pre-commit hooks
bash apps/api/scripts/setup-pre-commit.sh  # Unix/Mac
# OR
apps\api\scripts\setup-pre-commit.bat     # Windows
```

### 3. Environment Configuration

#### Backend (.env in apps/api)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost/waardhaven

# Authentication
SECRET_KEY=your-secret-key-min-32-chars
ADMIN_TOKEN=your-admin-token

# External APIs
TWELVEDATA_API_KEY=your-twelvedata-api-key
MARKETAUX_API_KEY=your-marketaux-api-key  # Optional

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Frontend URL for CORS
FRONTEND_URL=http://localhost:3000

# Development
SKIP_STARTUP_REFRESH=true  # Skip data refresh on startup
```

#### Frontend (.env.local in apps/web)
```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Optional: Google OAuth
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
```

### 4. Database Setup

#### Create Database
```sql
CREATE DATABASE waardhaven;
```

#### Initialize Database
```bash
cd apps/api

# Initialize database schema
python -m app.db_init

# Optional: Seed initial assets
python -m app.seed_assets

# Optional: Run initial data refresh
python -m app.tasks_refresh
```

### 5. Start Development Servers

#### Backend API Server
```bash
cd apps/api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Optional: Background Workers
```bash
# In separate terminals:

# Celery Worker
celery -A app.core.celery_app worker --loglevel=info

# Celery Beat (for periodic tasks)
celery -A app.core.celery_app beat --loglevel=info

# Flower Monitoring (http://localhost:5555)
celery -A app.core.celery_app flower
```

#### Frontend Development Server
```bash
cd apps/web
npm run dev
```

### 6. Access the Application
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc
- **Flower Dashboard**: http://localhost:5555 (if running)

### 7. Default Credentials
Register a new account or use:
- Email: user@example.com
- Password: Test123!@#

## Testing

### Backend Tests
```bash
cd apps/api

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

### Type Checking
```bash
# Frontend
cd apps/web
npx tsc --noEmit

# Backend
cd apps/api
mypy app/
```

### Linting
```bash
# Backend
cd apps/api
ruff check .

# Frontend
cd apps/web
npm run lint
```

## Docker Development

### Using Docker Compose
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d
```

### Individual Containers

#### Build Backend
```bash
cd apps/api
docker build -t waardhaven-api .
```

#### Build Frontend
```bash
cd apps/web
docker build -t waardhaven-web .
```

## Production Deployment

### Render.com Deployment

The project includes a `render.yaml` configuration for easy deployment:

1. Connect your GitHub repository to Render
2. Create a new Blueprint instance
3. Configure environment variables
4. Deploy

### Environment Variables (Production)

#### API Service
- DATABASE_URL (managed by Render)
- SECRET_KEY
- TWELVEDATA_API_KEY
- NODE_ENV=production
- ALLOWED_ORIGINS

#### Web Service
- NEXT_PUBLIC_API_URL

## Project Commands

### Backend Commands
```bash
# Run tests
python test_twelvedata.py
python test_rate_limits.py

# Database initialization
python app/db_init.py
python app/seed_assets.py

# Start server
uvicorn app.main:app --reload
```

### Frontend Commands
```bash
# Development
npm run dev

# Build
npm run build

# Production
npm start
```

### Monorepo Commands
```bash
# Install all dependencies
npm install

# Run all dev servers
npm run dev

# Build all apps
npm run build
```

## Startup Scripts

The project includes several startup scripts for different scenarios:

1. **startup.sh** - Basic startup
2. **startup_debug.sh** - With debug output
3. **startup_improved.sh** - Enhanced error handling
4. **startup_smart.sh** - Intelligent startup with checks

## Common Issues

### Database Connection
- Ensure PostgreSQL is running
- Check DATABASE_URL format
- Verify database exists

### API Key Issues
- Verify TwelveData API key is valid
- Check rate limits
- Ensure proper environment variable setup

### Port Conflicts
- Default ports: API (8000), Web (3000)
- Change ports in startup commands if needed

### CORS Issues
- Check ALLOWED_ORIGINS in production
- Verify API_URL in frontend config

## Development Tools

### Code Formatting & Linting
The project enforces code quality through automated formatting:

#### Backend (Python)
```bash
cd apps/api
black .                    # Format code
ruff check . --fix        # Fix linting issues
mypy app --ignore-missing-imports  # Type checking
```

#### Frontend (TypeScript)
```bash
cd apps/web
npm run format            # Format with Prettier
npm run lint              # Fix ESLint issues
npm run type-check        # TypeScript checking
```

#### CI/CD Checks
Before pushing, ensure your code passes:
```bash
# Backend
black --check .
ruff check .

# Frontend
npm run format:check
npm run lint:check
```

## Development Workflow

1. Create feature branch
2. Make changes
3. Run formatters (`black`, `prettier`)
4. Test locally
5. Run tests
6. Create pull request
7. CI/CD validates formatting
8. Deploy to staging (if available)
9. Merge to main
10. Deploy to production

## Useful Resources

- FastAPI Documentation: https://fastapi.tiangolo.com
- Next.js Documentation: https://nextjs.org/docs
- TwelveData API: https://twelvedata.com/docs
- SQLAlchemy: https://www.sqlalchemy.org