# Waardhaven AutoIndex - System Architecture

## Executive Summary

Waardhaven AutoIndex is a modern portfolio management platform built with a modular, microservices-ready architecture. The system consists of three main components:

1. **FastAPI Backend** - Modular Python API server
2. **Next.js Frontend** - React-based web application
3. **PostgreSQL Database** - Persistent data storage

All components are deployed on Render.com with automatic CI/CD from GitHub.

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         Client Browser                           │
│                    (Next.js React Application)                   │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  │ HTTPS
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Render CDN & Edge Network                   │
└──────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│   Frontend Service          │   │   Backend API Service       │
│   (Next.js on Render)       │   │   (FastAPI on Render)       │
│                             │   │                             │
│   waardhaven-web.           │   │   waardhaven-api.           │
│   onrender.com              │   │   onrender.com              │
└─────────────────────────────┘   └─────────────────────────────┘
                    │                           │
                    │                           │ SQL/TCP
                    │                           ▼
                    │              ┌─────────────────────────────┐
                    │              │   PostgreSQL Database       │
                    │              │   (Render Managed)          │
                    │              │                             │
                    │              │   - Users & Auth            │
                    │              │   - Assets & Prices         │
                    │              │   - Index Values            │
                    │              │   - Allocations             │
                    │              │   - Strategy Configs        │
                    │              └─────────────────────────────┘
                    │                           │
                    └───────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │   External APIs             │
                    │                             │
                    │   - TwelveData (Market)    │
                    │   - Exchange Rates API     │
                    └─────────────────────────────┘
```

## Backend Architecture (FastAPI)

### Modular Structure

```
apps/api/app/
├── core/                  # Core functionality
│   ├── config.py         # Environment & settings
│   └── database.py       # Database connection
│
├── models/               # Domain models (SQLAlchemy)
│   ├── user.py          # User authentication
│   ├── asset.py         # Assets & prices
│   ├── index.py         # Index & allocations
│   ├── trading.py       # Orders & transactions
│   └── strategy.py      # Strategy & risk metrics
│
├── schemas/              # API contracts (Pydantic)
│   ├── auth.py          # Auth request/response
│   ├── index.py         # Portfolio schemas
│   ├── benchmark.py     # Benchmark schemas
│   ├── broker.py        # Trading schemas
│   └── strategy.py      # Strategy schemas
│
├── routers/              # API endpoints
│   ├── auth.py          # /api/v1/auth/*
│   ├── index.py         # /api/v1/index/*
│   ├── benchmark.py     # /api/v1/benchmark/*
│   ├── broker.py        # /api/v1/broker/*
│   ├── strategy.py      # /api/v1/strategy/*
│   ├── diagnostics.py   # /api/v1/diagnostics/*
│   └── manual_refresh.py# /api/v1/manual/*
│
├── services/             # Business logic
│   ├── refresh.py       # Data refresh pipeline
│   ├── strategy.py      # Portfolio allocation
│   ├── performance.py   # Risk metrics
│   ├── twelvedata.py    # Market data client
│   └── currency.py      # FX conversion
│
├── utils/                # Utilities
│   ├── security.py      # JWT & password
│   ├── token_dep.py     # Auth dependencies
│   └── cache.py         # Caching utilities
│
└── main.py              # Application entry
```

### Key Design Patterns

1. **Domain-Driven Design**: Models organized by business domain
2. **Dependency Injection**: FastAPI's DI for database sessions and auth
3. **Repository Pattern**: Services abstract database operations
4. **DTO Pattern**: Schemas separate API contracts from domain models
5. **Middleware Pipeline**: Security, CORS, rate limiting, headers

### API Endpoints

#### Authentication (`/api/v1/auth`)
- `POST /register` - User registration
- `POST /login` - User authentication
- `GET /me` - Current user info

#### Portfolio Management (`/api/v1/index`)
- `GET /current` - Current allocations
- `GET /history` - Historical performance
- `POST /simulate` - Investment simulation
- `GET /currencies` - Supported currencies
- `GET /assets/{symbol}/history` - Asset history

#### Strategy (`/api/v1/strategy`)
- `GET /config` - Current strategy
- `PUT /config` - Update strategy
- `POST /config/ai-adjust` - AI adjustments
- `GET /risk-metrics` - Risk analytics
- `POST /rebalance` - Trigger rebalance

#### Market Data (`/api/v1/manual`)
- `POST /trigger-refresh` - Standard refresh
- `POST /smart-refresh` - Optimized refresh
- `POST /minimal-refresh` - Test refresh

#### Diagnostics (`/api/v1/diagnostics`)
- `GET /database-status` - DB health
- `GET /refresh-status` - Data freshness
- `POST /test-refresh` - Test pipeline
- `POST /recalculate-index` - Recalculate

## Frontend Architecture (Next.js)

### Component Structure

```
apps/web/app/
├── components/           # Reusable components
│   ├── charts/          # Chart components
│   ├── portfolio/       # Portfolio widgets
│   ├── strategy/        # Strategy controls
│   └── ui/              # UI primitives
│
├── services/            # API clients
│   ├── api/
│   │   ├── base.ts     # Base API service
│   │   ├── portfolio.ts# Portfolio endpoints
│   │   └── market.ts   # Market data endpoints
│   └── aiInsights.ts   # AI service
│
├── hooks/               # Custom React hooks
│   ├── usePortfolioData.ts
│   ├── useSimulation.ts
│   └── useChartData.ts
│
├── types/               # TypeScript types
│   ├── api.ts          # API types
│   ├── portfolio.ts    # Portfolio types
│   └── chart.ts        # Chart types
│
├── constants/           # Configuration
│   ├── config.ts       # App config
│   └── theme.ts        # Theme constants
│
├── utils/               # Utilities
│   └── api.ts          # API helpers
│
└── (routes)/           # Next.js pages
    ├── page.tsx        # Home
    ├── dashboard/      # Dashboard
    ├── login/          # Auth pages
    └── admin/          # Admin panel
```

### Frontend-Backend Integration

#### API Client Configuration

```typescript
// Base configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Authentication handling
- JWT tokens stored in localStorage
- Automatic token injection in headers
- Global 401 error handling

// Service layer pattern
- Base ApiService class for common functionality
- Domain-specific services (portfolio, market, strategy)
- Type-safe API calls with TypeScript
```

#### Data Flow

1. **User Action** → React Component
2. **Component** → Custom Hook
3. **Hook** → API Service
4. **API Service** → HTTP Request
5. **Backend** → Process & Response
6. **Response** → Update State
7. **State** → Re-render Component

## Database Schema

### Core Tables

```sql
-- User Management
users (id, email, password_hash, created_at)

-- Market Data
assets (id, symbol, name, sector)
prices (id, asset_id, date, close)

-- Portfolio
index_values (id, date, value)
allocations (id, date, asset_id, weight)

-- Strategy
strategy_configs (id, weights, parameters, ai_metadata)
risk_metrics (id, date, metrics, performance)

-- Trading
orders (id, user_id, asset_symbol, type, amount)
```

### Relationships

- **User** → Orders (1:N)
- **Asset** → Prices (1:N)
- **Asset** → Allocations (1:N)
- **IndexValue** ← Strategy (N:1)

## Deployment Architecture

### Infrastructure (Render.com)

```yaml
Services:
  Frontend:
    - Type: Static Site
    - Build: npm run build
    - URL: waardhaven-web.onrender.com
    
  Backend:
    - Type: Web Service
    - Runtime: Python 3.11
    - Build: pip install -r requirements.txt
    - Start: uvicorn app.main:app
    - URL: waardhaven-api.onrender.com
    
  Database:
    - Type: PostgreSQL
    - Version: 15
    - Plan: Starter
    - Backup: Daily
```

### Environment Variables

#### Backend
- `DATABASE_URL` - PostgreSQL connection
- `SECRET_KEY` - JWT signing key
- `TWELVEDATA_API_KEY` - Market data API
- `RENDER` - Deployment flag

#### Frontend
- `NEXT_PUBLIC_API_URL` - Backend URL

### CI/CD Pipeline

1. **GitHub Push** → Main branch
2. **Render Webhook** → Triggered
3. **Build Process** → Dependencies & compilation
4. **Health Check** → Service validation
5. **Deploy** → Blue-green deployment
6. **Rollback** → On failure

## Security Architecture

### Authentication & Authorization

- **JWT Tokens**: Stateless authentication
- **Password Hashing**: bcrypt with salt
- **Token Expiration**: 24-hour validity
- **Dependency Injection**: Route protection

### API Security

- **CORS**: Restricted origins
- **Rate Limiting**: 100 req/min per IP
- **Security Headers**: XSS, frame, content-type
- **HTTPS**: TLS encryption
- **Input Validation**: Pydantic schemas

### Data Protection

- **SQL Injection**: ORM parameterization
- **Environment Variables**: Secrets management
- **Database Encryption**: At-rest encryption
- **Backup**: Daily automated backups

## Performance Optimizations

### Backend

1. **Database**
   - Connection pooling (20 connections)
   - Indexed columns (date, symbol)
   - Batch operations for bulk inserts
   - UPSERT pattern for updates

2. **Caching**
   - In-memory cache for hot data
   - API response caching (5 min TTL)
   - Market data caching

3. **API Optimization**
   - Async request handling
   - Pagination for large datasets
   - Selective field returns

### Frontend

1. **Next.js Optimizations**
   - Server-side rendering
   - Static generation where possible
   - Image optimization
   - Code splitting

2. **Client Optimizations**
   - React Query for caching
   - Debounced API calls
   - Lazy loading components
   - Virtual scrolling for lists

## Monitoring & Observability

### Health Checks

- `/health` - Basic liveness
- `/api/v1/diagnostics/database-status` - DB health
- `/api/v1/diagnostics/refresh-status` - Data freshness

### Logging

- Structured JSON logging
- Request/response logging
- Error tracking with stack traces
- Performance metrics

### Metrics

- Response times
- Error rates
- Database query performance
- External API latency

## Scalability Considerations

### Horizontal Scaling

- Stateless backend services
- Database read replicas
- Load balancer ready
- Session-less authentication

### Vertical Scaling

- Configurable worker processes
- Memory optimization
- Connection pool sizing
- Query optimization

### Future Enhancements

1. **Microservices Split**
   - Auth service
   - Market data service
   - Portfolio service
   - Strategy service

2. **Event-Driven Architecture**
   - Message queue (RabbitMQ/Kafka)
   - Event sourcing
   - CQRS pattern

3. **Caching Layer**
   - Redis integration
   - Distributed caching
   - Session storage

4. **Real-time Updates**
   - WebSocket support
   - Server-sent events
   - Live price feeds

## Development Workflow

### Local Development

```bash
# Backend
cd apps/api
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd apps/web
npm install
npm run dev

# Database
docker-compose up postgres
```

### Testing Strategy

1. **Unit Tests**: Service logic
2. **Integration Tests**: API endpoints
3. **E2E Tests**: User workflows
4. **Performance Tests**: Load testing

### Code Quality

- **Linting**: Black, ESLint
- **Type Checking**: mypy, TypeScript
- **Code Review**: PR process
- **Documentation**: Inline + markdown

## Conclusion

The Waardhaven AutoIndex architecture is designed for:

- **Modularity**: Clear separation of concerns
- **Scalability**: Ready for growth
- **Maintainability**: Clean code structure
- **Security**: Defense in depth
- **Performance**: Optimized for speed
- **Reliability**: Error handling & recovery

The modular structure allows for easy extension, testing, and deployment while maintaining clean boundaries between different parts of the system.