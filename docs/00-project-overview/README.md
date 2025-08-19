# Waardhaven AutoIndex - Project Overview

## What is Waardhaven AutoIndex?

Waardhaven AutoIndex is an intelligent automated investment platform that manages portfolios using dynamic index strategies. It analyzes market data, applies quantitative investment strategies, and automatically rebalances portfolios to optimize returns while managing risk.

## Project Structure

```
AI-Investment/
├── apps/
│   ├── api/          # Backend FastAPI application
│   └── web/          # Frontend Next.js application
├── docs/             # Project documentation
└── Configuration files
```

## Core Functionality

### 1. Portfolio Management
- Automated index-based investment strategy
- Dynamic asset allocation
- Configurable rebalancing frequencies
- Multi-currency support

### 2. Market Data Integration
- Real-time price data from TwelveData API
- Historical data analysis
- Market benchmarking against S&P 500

### 3. Investment Strategies
- Momentum-based filtering
- Market capitalization weighting
- Risk parity allocation
- Configurable strategy parameters

### 4. User Features
- Secure authentication system
- Interactive dashboard
- Performance analytics
- AI-powered insights

## Technology Overview

### Backend (FastAPI)
- Python 3.11+ with async support
- PostgreSQL database with SQLAlchemy ORM
- JWT-based authentication
- RESTful API design

### Frontend (Next.js)
- React 18 with TypeScript
- Server-side rendering
- TailwindCSS for styling
- Recharts for data visualization

### Infrastructure
- Docker containerization
- Render.com deployment
- Turborepo monorepo management

## Key Modules

### Backend Modules
- **Core**: Configuration and database setup
- **Models**: Database models and schemas
- **Routers**: API endpoint handlers
- **Services**: Business logic and integrations
- **Utils**: Security and helper functions

### Frontend Modules
- **Pages**: Application routes and views
- **Components**: Reusable UI components
- **Services**: API communication layer
- **Utils**: Helper functions and utilities

## Current Capabilities

1. **User Management**
   - Registration and login
   - JWT token authentication
   - Secure password storage

2. **Portfolio Operations**
   - Create and manage investment portfolios
   - Track performance over time
   - Compare against market benchmarks

3. **Data Processing**
   - Fetch real-time market data
   - Calculate portfolio metrics
   - Generate investment insights

4. **Visualization**
   - Interactive performance charts
   - Asset allocation displays
   - Historical trend analysis

## Development Status

The project is currently in active development with core features implemented and operational. The platform successfully:
- Manages user authentication
- Fetches and processes market data
- Implements investment strategies
- Provides real-time portfolio tracking
- Generates AI-powered insights

## Documentation Organization

This documentation is organized into the following sections:

1. **00-project-overview**: High-level project information
2. **01-backend**: Backend module documentation
3. **02-frontend**: Frontend module documentation
4. **03-infrastructure**: Deployment and infrastructure
5. **04-current-features**: Detailed feature documentation
6. **05-ideas-and-concepts**: Future plans and concepts

## Getting Started

For setup instructions, see [getting-started.md](./getting-started.md)