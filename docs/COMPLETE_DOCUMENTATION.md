# Waardhaven AutoIndex - Complete Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Backend API Documentation](#backend-api-documentation)
5. [Frontend Documentation](#frontend-documentation)
6. [Database Configuration](#database-configuration)
7. [Deployment Guide](#deployment-guide)
8. [API Endpoints Reference](#api-endpoints-reference)
9. [Environment Variables](#environment-variables)
10. [Troubleshooting](#troubleshooting)
11. [Development Workflow](#development-workflow)

---

## Project Overview

**Waardhaven AutoIndex** is a sophisticated long-term investment platform that implements an automated index strategy. The system analyzes market performance, filters underperforming assets, and maintains a balanced portfolio through intelligent rebalancing.

### Key Features
- **Automated Index Management**: Daily analysis and rebalancing of portfolio assets
- **Performance Tracking**: Real-time comparison with S&P 500 benchmark
- **Investment Simulation**: Historical backtesting capabilities
- **Secure Authentication**: JWT-based user authentication system
- **Real-time Data**: Integration with TwelveData for professional-grade market data

### Technology Stack
- **Backend**: FastAPI (Python 3.11+), SQLAlchemy ORM, PostgreSQL
- **Frontend**: Next.js 14 (App Router), TypeScript, TailwindCSS
- **Visualization**: Recharts for interactive data visualization
- **Authentication**: JWT with secure password hashing (bcrypt)
- **Market Data**: TwelveData API integration
- **Deployment**: Docker containers on Render.com

---

## Architecture

### System Design

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│                 │       │                 │       │                 │
│  Next.js Web    │◄─────►│  FastAPI API    │◄─────►│  PostgreSQL DB  │
│  (Frontend)     │       │  (Backend)      │       │                 │
│                 │       │                 │       │                 │
└─────────────────┘       └─────────────────┘       └─────────────────┘
        │                         │                          
        │                         ▼                          
        │                 ┌─────────────────┐               
        │                 │                 │               
        └────────────────►│   TwelveData    │               
                          │      API        │               
                          │                 │               
                          └─────────────────┘               
```

### Project Structure

```
waardhaven-autoindex/
├── apps/
│   ├── api/                    # Backend API Service
│   │   ├── app/
│   │   │   ├── core/           # Core configuration
│   │   │   │   ├── config.py   # Settings management
│   │   │   │   └── database.py # Database connection
│   │   │   ├── routers/        # API endpoints
│   │   │   │   ├── auth.py     # Authentication
│   │   │   │   ├── index.py    # Index operations
│   │   │   │   ├── benchmark.py # Benchmark data
│   │   │   │   ├── broker.py   # Trading operations
│   │   │   │   └── tasks.py    # Background tasks
│   │   │   ├── services/       # Business logic
│   │   │   │   ├── strategy.py # Index strategy
│   │   │   │   ├── twelvedata.py # Market data
│   │   │   │   ├── currency.py # Currency exchange
│   │   │   │   └── refresh.py  # Data refresh
│   │   │   ├── utils/          # Utilities
│   │   │   ├── models.py       # Database models
│   │   │   ├── schemas.py      # Pydantic schemas
│   │   │   └── main.py         # Application entry
│   │   ├── Dockerfile          # API container
│   │   ├── startup.sh          # Initialization script
│   │   └── requirements.txt    # Python dependencies
│   │
│   └── web/                    # Frontend Web Service
│       ├── app/
│       │   ├── dashboard/      # Dashboard page
│       │   ├── login/          # Login page
│       │   ├── register/       # Registration page
│       │   ├── utils/          # Utilities
│       │   │   └── api.ts      # API client
│       │   ├── layout.tsx      # Root layout
│       │   └── page.tsx        # Home page
│       ├── public/             # Static assets
│       ├── Dockerfile          # Web container
│       ├── package.json        # Node dependencies
│       └── next.config.js     # Next.js config
│
├── docs/                       # Documentation
├── render.yaml                 # Render deployment config
└── package.json               # Monorepo config
```

---

## Installation & Setup

### Prerequisites

- **Python** 3.11 or higher
- **Node.js** 20 or higher
- **PostgreSQL** 14 or higher
- **Docker** (optional but recommended)
- **Git** for version control

### Local Development Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/gesttaltt/waardhaven-autoindex.git
cd waardhaven-autoindex
```

#### 2. Environment Configuration

Create environment files from templates:

```bash
# Backend environment
cp apps/api/.env.example apps/api/.env

# Frontend environment
cp apps/web/.env.example apps/web/.env.local
```

#### 3. Backend Setup

```bash
cd apps/api

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test TwelveData integration (recommended)
python test_twelvedata.py

# Initialize database
python -m app.db_init

# Seed initial assets (optional)
python -m app.seed_assets

# Refresh market data
python -m app.tasks_refresh

# Start API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 4. Frontend Setup

```bash
cd apps/web

# Install dependencies
npm install

# Start development server
npm run dev
```

Access the application at `http://localhost:3000`

---

## Backend API Documentation

### Core Components

#### Authentication System
- **JWT-based authentication** with configurable expiration
- **Secure password hashing** using bcrypt
- **Token validation** middleware for protected endpoints

#### Database Models

**User Model**
```python
- id: Primary key
- email: Unique user identifier
- password_hash: Encrypted password
- created_at: Registration timestamp
```

**Asset Model**
```python
- id: Primary key
- symbol: Stock ticker symbol
- name: Company name
- sector: Industry sector
```

**Price Model**
```python
- id: Primary key
- asset_id: Foreign key to Asset
- date: Price date
- close: Closing price
```

**IndexValue Model**
```python
- id: Primary key
- date: Calculation date
- value: Index value (base 100)
```

**Allocation Model**
```python
- id: Primary key
- date: Allocation date
- asset_id: Foreign key to Asset
- weight: Portfolio weight (0-1)
```

#### Index Strategy Algorithm

The index strategy implements a sophisticated filtering mechanism:

1. **Daily Performance Analysis**
   - Calculate daily returns for all assets
   - Identify assets below threshold (default: -1%)

2. **Portfolio Rebalancing**
   - Remove underperforming assets
   - Redistribute weight equally among remaining assets

3. **Index Calculation**
   - Track portfolio value over time
   - Base index value: 100
   - Daily compounding of returns

#### Services Layer

**Strategy Service** (`services/strategy.py`)
- Implements core index logic
- Manages portfolio rebalancing
- Calculates index values

**TwelveData Service** (`services/twelvedata.py`)
- Fetches real-time and historical market data
- Provides currency exchange rates
- Handles professional-grade financial data
- Manages API credits and rate limits

**Currency Service** (`services/currency.py`)
- Currency exchange rate conversion
- Cross-currency calculations
- Supports 20+ major currencies

**Refresh Service** (`services/refresh.py`)
- Orchestrates daily updates
- Manages data consistency
- Handles error recovery

---

## Frontend Documentation

### Technology Stack

- **Next.js 14** with App Router
- **TypeScript** for type safety
- **TailwindCSS** for styling
- **Recharts** for data visualization
- **Axios** for API communication

### Pages and Components

#### Authentication Pages

**Login Page** (`app/login/page.tsx`)
- Email/password authentication
- Error handling with user feedback
- Automatic token storage
- Redirect to dashboard on success

**Register Page** (`app/register/page.tsx`)
- New user registration
- Input validation
- Duplicate email detection
- Automatic login after registration

#### Dashboard Page (`app/dashboard/page.tsx`)

Features:
- **Performance Chart**: Interactive line chart comparing index vs S&P 500
- **Current Allocations**: Real-time portfolio composition
- **Investment Simulator**: Backtesting with custom parameters
- **Protected Route**: Automatic redirect if not authenticated

Components:
- Responsive container layout
- Real-time data updates
- Interactive tooltips
- Mobile-optimized design

### API Client Configuration

The frontend uses a centralized API client (`app/utils/api.ts`):

```typescript
- Automatic token attachment to requests
- Global error handling
- 401 response interceptor for expired tokens
- Configurable base URL
```

### State Management

- **Local Storage**: JWT token persistence
- **React Hooks**: Component-level state
- **Effect Hooks**: Data fetching lifecycle

---

## Database Configuration

### PostgreSQL Setup

#### Local Development

1. **Install PostgreSQL**
```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql

# Windows
# Download from postgresql.org
```

2. **Create Database**
```bash
createdb waardhaven
```

3. **Connection String Format**
```
postgresql://username:password@localhost:5432/waardhaven
```

### Render Database Configuration

#### Automatic Setup via render.yaml

```yaml
databases:
  - name: waardhaven-db
    plan: starter
    databaseName: waardhaven_db_5t62
    user: waardhaven_db_5t62_user
```

#### Manual Configuration

1. **Create Database in Render Dashboard**
   - Navigate to Dashboard → New → PostgreSQL
   - Configure name and region
   - Select appropriate plan

2. **Connection Details**
   - **Internal hostname**: `dpg-[id]-a`
   - **Port**: 5432
   - **SSL**: Required for external connections

### Database Schema

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Assets table
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR UNIQUE NOT NULL,
    name VARCHAR,
    sector VARCHAR
);

-- Prices table
CREATE TABLE prices (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(id),
    date DATE NOT NULL,
    close FLOAT NOT NULL,
    UNIQUE(asset_id, date)
);

-- Index values table
CREATE TABLE index_values (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    value FLOAT NOT NULL
);

-- Allocations table
CREATE TABLE allocations (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    asset_id INTEGER REFERENCES assets(id),
    weight FLOAT NOT NULL
);

-- Orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    asset_symbol VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    amount FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    details JSONB
);
```

### Database Initialization

The application automatically initializes the database on startup:

1. **Table Creation**: Uses SQLAlchemy's `create_all()`
2. **Asset Seeding**: Populates initial stock symbols
3. **Index Calculation**: Computes initial index values

---

## Deployment Guide

### Render Deployment

#### Prerequisites
- Render account
- GitHub repository
- Environment variables configured

#### Service Configuration

**API Service**
```yaml
type: web
name: waardhaven-api
env: docker
dockerfilePath: ./Dockerfile
rootDir: apps/api
plan: starter
```

**Web Service**
```yaml
type: web
name: waardhaven-web
env: docker
dockerfilePath: ./Dockerfile
rootDir: apps/web
plan: starter
```

#### Environment Variables

**API Service Variables**
| Variable | Description | Example |
|----------|-------------|---------|
| PORT | Server port | 10000 |
| DATABASE_URL | PostgreSQL connection | (from database) |
| SECRET_KEY | JWT signing key | (generate secure) |
| ADMIN_TOKEN | Admin API access | (custom token) |
| TWELVEDATA_API_KEY | TwelveData API key | (get from twelvedata.com) |

**Web Service Variables**
| Variable | Description | Example |
|----------|-------------|---------|
| PORT | Server port | 10000 |
| NEXT_PUBLIC_API_URL | API endpoint | https://api-url.onrender.com |

#### Deployment Steps

1. **Push to GitHub**
```bash
git add .
git commit -m "Deploy to Render"
git push origin main
```

2. **Create Services in Render**
   - Import GitHub repository
   - Configure using render.yaml
   - Set environment variables

3. **Verify Deployment**
   - Check service logs
   - Test health endpoint
   - Verify database connection

### Docker Configuration

#### API Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY startup.sh ./
RUN chmod +x startup.sh
ENV PORT=10000
EXPOSE ${PORT}
CMD ["./startup.sh"]
```

#### Web Dockerfile
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=10000
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
EXPOSE ${PORT}
CMD ["sh", "-c", "npm start -- -p ${PORT:-10000}"]
```

---

## API Endpoints Reference

### Authentication Endpoints

#### POST /api/v1/auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### POST /api/v1/auth/login
Authenticate existing user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Index Endpoints

#### GET /api/v1/index/current
Get current index allocations.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "allocations": [
    {
      "symbol": "AAPL",
      "weight": 0.05
    },
    {
      "symbol": "MSFT",
      "weight": 0.05
    }
  ],
  "date": "2025-01-15"
}
```

#### GET /api/v1/index/history
Get historical index performance.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "series": [
    {
      "date": "2025-01-01",
      "value": 100.0
    },
    {
      "date": "2025-01-02",
      "value": 101.5
    }
  ]
}
```

#### POST /api/v1/index/simulate
Run investment simulation.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "amount": 10000,
  "start_date": "2024-01-01"
}
```

**Response:**
```json
{
  "amount_final": 12500.50,
  "roi_pct": 25.05,
  "start_date": "2024-01-01",
  "end_date": "2025-01-15"
}
```

### Benchmark Endpoints

#### GET /api/v1/benchmark/sp500
Get S&P 500 benchmark data.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "series": [
    {
      "date": "2025-01-01",
      "value": 100.0
    },
    {
      "date": "2025-01-02",
      "value": 100.8
    }
  ]
}
```

### Admin Endpoints

#### POST /api/v1/tasks/refresh
Trigger manual data refresh (requires admin token).

**Headers:**
```
X-Admin-Token: <admin_token>
```

**Response:**
```json
{
  "message": "Refresh completed",
  "assets_updated": 50,
  "index_calculated": true
}
```

### Health Check

#### GET /health
Service health status.

**Response:**
```json
{
  "status": "ok"
}
```

---

## Environment Variables

### Backend Environment Variables

```bash
# Security
SECRET_KEY=                 # JWT signing key (32+ characters)
JWT_ALGORITHM=HS256         # JWT algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # Token expiration (24 hours)

# Database
DATABASE_URL=               # PostgreSQL connection string
                           # Format: postgresql://user:pass@host:port/db

# Admin
ADMIN_TOKEN=               # Token for admin endpoints

# Index Configuration
DAILY_DROP_THRESHOLD=-0.01  # Asset filter threshold (-1%)
ASSET_DEFAULT_START=2018-01-01  # Historical data start date
SP500_TICKER=^GSPC          # S&P 500 ticker symbol

# Market Data API
TWELVEDATA_API_KEY=         # TwelveData API key for market data
                           # Get from: https://twelvedata.com/account/api-keys

# Server
PORT=10000                  # API server port
```

### Frontend Environment Variables

```bash
# API Configuration
NEXT_PUBLIC_API_URL=        # Backend API URL
                           # Local: http://localhost:8000
                           # Production: https://api.onrender.com

# Server
PORT=3000                   # Frontend server port
```

### Security Best Practices

1. **Never commit .env files** to version control
2. **Use strong SECRET_KEY** (minimum 32 characters)
3. **Rotate credentials** regularly
4. **Use HTTPS** in production
5. **Implement rate limiting** for API endpoints
6. **Enable CORS** only for trusted origins

---

## Troubleshooting

### Common Issues and Solutions

#### Database Connection Issues

**Problem**: "Connection refused" or timeout errors

**Solutions**:
- Verify DATABASE_URL is correctly formatted
- Check PostgreSQL service is running
- Ensure network connectivity between services
- For Render: Use internal connection string

**Debug Commands**:
```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check service status
systemctl status postgresql
```

#### Authentication Failures

**Problem**: "Invalid credentials" or token errors

**Solutions**:
- Verify SECRET_KEY matches between deploys
- Check token expiration settings
- Clear browser localStorage
- Ensure CORS is properly configured

**Debug Steps**:
1. Check browser console for errors
2. Verify API response headers
3. Test with curl/Postman

#### Frontend Build Errors

**Problem**: TypeScript or build failures

**Solutions**:
- Clear .next directory: `rm -rf .next`
- Reinstall dependencies: `npm ci`
- Check TypeScript errors: `npm run type-check`
- Verify environment variables are set

#### Data Refresh Issues

**Problem**: Market data not updating

**Solutions**:
- Check TwelveData API key is configured
- Verify API credits/limits at https://twelvedata.com
- Verify ADMIN_TOKEN is set
- Review refresh service logs
- Manually trigger refresh endpoint

**Debug Commands**:
```bash
# Manual refresh
curl -X POST https://api-url/api/v1/tasks/refresh \
  -H "X-Admin-Token: your-admin-token"

# Check logs
docker logs waardhaven-api
```

#### Deployment Failures on Render

**Problem**: Build or deploy failures

**Solutions**:
1. **Check build logs** in Render dashboard
2. **Verify Dockerfile** syntax and commands
3. **Ensure all files** are committed to Git
4. **Check environment variables** are set
5. **Verify port configuration** matches Render's requirements

**Common Fixes**:
```yaml
# Ensure PORT is set
envVars:
  - key: PORT
    value: "10000"
```

### Performance Optimization

#### Database Optimization
- Add indexes on frequently queried columns
- Use connection pooling
- Implement query caching
- Regular VACUUM and ANALYZE

#### API Optimization
- Implement response caching
- Use pagination for large datasets
- Optimize database queries
- Add request rate limiting

#### Frontend Optimization
- Enable Next.js image optimization
- Implement lazy loading
- Use React.memo for expensive components
- Optimize bundle size

---

## Development Workflow

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push to GitHub
git push origin feature/new-feature

# Create pull request
# Merge to main after review
```

### Testing Strategy

#### Backend Testing
```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_auth.py::test_login
```

#### Frontend Testing
```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage

# E2E testing
npm run test:e2e
```

### Code Quality

#### Python (Backend)
```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

#### TypeScript (Frontend)
```bash
# Format code
npm run format

# Lint code
npm run lint

# Type checking
npm run type-check
```

### Monitoring and Logging

#### Application Monitoring
- Use Render's built-in metrics
- Implement custom health checks
- Add performance tracking
- Monitor error rates

#### Logging Best Practices
```python
import logging

logger = logging.getLogger(__name__)

# Log levels
logger.debug("Detailed information")
logger.info("General information")
logger.warning("Warning messages")
logger.error("Error messages")
logger.critical("Critical issues")
```

### Continuous Integration

#### GitHub Actions Workflow
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r apps/api/requirements.txt
      - name: Run tests
        run: |
          pytest tests/
```

---

## Security Considerations

### Authentication Security
- Passwords hashed with bcrypt (12 rounds)
- JWT tokens with configurable expiration
- Secure token storage in httpOnly cookies (future)
- Rate limiting on auth endpoints

### API Security
- CORS configured for specific origins
- Input validation with Pydantic
- SQL injection prevention via ORM
- XSS protection in frontend

### Deployment Security
- Environment variables for secrets
- HTTPS enforcement in production
- Database SSL connections
- Regular dependency updates

### Data Protection
- Encrypted database connections
- No sensitive data in logs
- Secure password requirements
- Session management

---

## Future Enhancements

### Planned Features
1. **Advanced Analytics**
   - Machine learning predictions
   - Risk assessment metrics
   - Portfolio optimization

2. **User Features**
   - Portfolio tracking
   - Custom strategies
   - Alert notifications
   - Mobile application

3. **Technical Improvements**
   - WebSocket real-time updates
   - Redis caching layer
   - Microservices architecture
   - Kubernetes deployment

4. **Integration**
   - Multiple broker APIs
   - Cryptocurrency support
   - International markets
   - Tax reporting

---

## TwelveData Migration (2025-08-13)

### Migration Overview
The project has been migrated from Yahoo Finance to TwelveData for improved reliability and professional-grade market data access.

### Key Changes
- **Market Data Provider**: Switched from `yfinance` to `twelvedata` Python package
- **API Authentication**: Now requires TwelveData API key (free tier available)
- **Enhanced Features**: Access to technical indicators, WebSocket streaming, and more comprehensive data
- **Currency Support**: Improved foreign exchange rate handling with dedicated forex endpoints

### Migration Steps for Existing Deployments
1. **Get TwelveData API Key**
   - Sign up at https://twelvedata.com
   - Navigate to https://twelvedata.com/account/api-keys
   - Copy your API key

2. **Update Environment Variables**
   ```bash
   TWELVEDATA_API_KEY=your_api_key_here
   ```

3. **Update Dependencies**
   ```bash
   pip install twelvedata==1.2.14
   # Remove old dependency
   pip uninstall yfinance
   ```

4. **Test Integration**
   ```bash
   python apps/api/test_twelvedata.py
   ```

### API Compatibility
All existing API endpoints maintain backward compatibility. The frontend requires no changes.

---

## Support and Contribution

### Getting Help
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Refer to this guide
- **Logs**: Check application logs for debugging

### Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### License
This project is proprietary software. All rights reserved.

### Contact
- **Repository**: https://github.com/gesttaltt/waardhaven-autoindex
- **Build Date**: 2025-01-15

---

*This documentation is maintained as part of the Waardhaven AutoIndex project. For updates and corrections, please submit a pull request or open an issue on GitHub.*