# Waardhaven Autoindex — MVP

Minimal MVP for a long-term investment autoindex platform.

- Backend: FastAPI (Python), SQLAlchemy, JWT, TwelveData
- Frontend: Next.js 14 (App Router), TypeScript, TailwindCSS, Recharts
- DB: PostgreSQL
- Deploy target: Render (Docker for API & Web), Render PostgreSQL

## Quick Start (Local)

### Prerequisites
- Python 3.11+
- Node 20+
- Docker (optional but recommended)
- PostgreSQL

### Environment
Copy the env templates and fill values:
```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
```

**Important**: Get your TwelveData API key from https://twelvedata.com/account/api-keys and add it to `apps/api/.env`:
```
TWELVEDATA_API_KEY=your_api_key_here
```

### Backend (API)
```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Initialize DB
python -m app.db_init
# (Optional) Seed assets
python -m app.seed_assets
# Test TwelveData integration (optional)
python test_twelvedata.py
# Refresh prices + compute index
python -m app.tasks_refresh
# Run API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Web)
```bash
cd apps/web
npm install
npm run dev
```

Open: http://localhost:3000

## Render Deployment

- API: Deploy as a Docker web service using `apps/api/Dockerfile.api`.
- Web: Deploy as a Docker web service using `apps/web/Dockerfile.web`.
- DB: Create a managed PostgreSQL on Render.
- Set environment variables from `.env.example` files.
- Optionally schedule a daily cron (on Render) calling `/api/v1/tasks/refresh` with `X-Admin-Token` header.

## Notes

- The index logic is simple by design for MVP: filter assets with daily return below threshold and rebalance equally.
- The history endpoint returns precomputed index values (base = 100) and the benchmark (S&P 500) for comparison.
- Simulation uses index history to compute ROI given a start date and amount.
- Market data is provided by TwelveData API, offering professional-grade financial data with real-time updates.
- Supports multi-currency simulations with automatic exchange rate conversion.

Build date: 2025-08-12
Updated: 2025-08-13 - Migrated from Yahoo Finance to TwelveData API
