# Getting Started with Waardhaven AutoIndex

## Prerequisites

### Required Software
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 14+
- Docker (optional, for containerized deployment)

### API Keys
- TwelveData API key for market data

## Local Development Setup

### 1. Clone the Repository
```bash
git clone [repository-url]
cd AI-Investment
```

### 2. Install Dependencies

#### Backend Setup
```bash
cd apps/api
pip install -r requirements.txt
```

#### Frontend Setup
```bash
cd apps/web
npm install
```

### 3. Environment Configuration

#### Backend (.env in apps/api)
```
DATABASE_URL=postgresql://user:password@localhost/waardhaven
SECRET_KEY=your-secret-key
TWELVEDATA_API_KEY=your-api-key
NODE_ENV=development
```

#### Frontend (.env.local in apps/web)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Database Setup

#### Create Database
```sql
CREATE DATABASE waardhaven;
```

#### Run Initialization
```bash
cd apps/api
python app/db_init.py
python app/seed_assets.py
```

### 5. Start Development Servers

#### Backend Server
```bash
cd apps/api
uvicorn app.main:app --reload --port 8000
```

#### Frontend Server
```bash
cd apps/web
npm run dev
```

### 6. Access the Application
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/docs

## Docker Development

### Using Docker Compose
```bash
docker-compose up
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

## Development Workflow

1. Create feature branch
2. Make changes
3. Test locally
4. Run tests
5. Create pull request
6. Deploy to staging (if available)
7. Merge to main
8. Deploy to production

## Useful Resources

- FastAPI Documentation: https://fastapi.tiangolo.com
- Next.js Documentation: https://nextjs.org/docs
- TwelveData API: https://twelvedata.com/docs
- SQLAlchemy: https://www.sqlalchemy.org