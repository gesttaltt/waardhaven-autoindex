#!/bin/bash

echo "=== Waardhaven API Smart Startup ==="
echo "Starting with rate limit protection..."

# Initialize database tables
echo "Initializing database..."
python -m app.db_init || {
    echo "Database initialization failed!"
    exit 1
}

# Seed initial assets if needed
echo "Seeding initial assets..."
python -m app.seed_assets || echo "Asset seeding skipped (may already exist)"

# Smart refresh with rate limit protection
echo "Performing smart market data refresh..."
python -c "
from app.core.database import SessionLocal
from app.services.refresh import refresh_all
import os

# Check if we should skip refresh on startup
if os.getenv('SKIP_STARTUP_REFRESH', '').lower() == 'true':
    print('Skipping market data refresh (SKIP_STARTUP_REFRESH=true)')
else:
    db = SessionLocal()
    try:
        # Use smart refresh with rate limiting
        result = refresh_all(db, smart_mode=True)
        print(f'Refresh completed: {result}')
    except Exception as e:
        print(f'Refresh failed (non-critical): {e}')
        print('Continuing with cached/existing data...')
    finally:
        db.close()
" || echo "Market data refresh failed, continuing with existing data..."

# Start the API server
echo "Starting API server on port ${PORT:-10000}..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}