#!/bin/bash

echo "=== Waardhaven API Startup Debug ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Environment variables check:"

# Check critical environment variables
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL is not set!"
    exit 1
else
    echo "✓ DATABASE_URL is set"
fi

if [ -z "$SECRET_KEY" ]; then
    echo "ERROR: SECRET_KEY is not set!"
    exit 1
else
    echo "✓ SECRET_KEY is set"
fi

if [ -z "$TWELVEDATA_API_KEY" ]; then
    echo "WARNING: TWELVEDATA_API_KEY is not set - market data refresh will fail!"
else
    echo "✓ TWELVEDATA_API_KEY is set"
fi

echo ""
echo "=== Installing Dependencies ==="
pip list | grep -E "fastapi|twelvedata|SQLAlchemy"

echo ""
echo "=== Testing Database Connection ==="
python -c "
from app.core.database import engine
from sqlalchemy import text
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✓ Database connection successful')
except Exception as e:
    print(f'✗ Database connection failed: {e}')
    exit(1)
"

echo ""
echo "=== Initializing Database Tables ==="
python -m app.db_init || {
    echo "Database initialization failed!"
    exit 1
}

echo ""
echo "=== Seeding Assets ==="
python -m app.seed_assets || {
    echo "Asset seeding failed!"
    # Don't exit, this might be okay if assets already exist
}

echo ""
echo "=== Testing TwelveData Connection ==="
if [ ! -z "$TWELVEDATA_API_KEY" ]; then
    python -c "
from twelvedata import TDClient
import os
try:
    client = TDClient(apikey=os.getenv('TWELVEDATA_API_KEY'))
    quote = client.quote(symbol='AAPL').as_json()
    if quote and 'symbol' in quote:
        print('✓ TwelveData connection successful')
    else:
        print('✗ TwelveData connection failed - invalid response')
except Exception as e:
    print(f'✗ TwelveData connection failed: {e}')
"
else
    echo "Skipping TwelveData test - no API key"
fi

echo ""
echo "=== Attempting Market Data Refresh ==="
if [ ! -z "$TWELVEDATA_API_KEY" ]; then
    python -m app.tasks_refresh || {
        echo "Market data refresh failed - continuing anyway"
        echo "This is expected on first deploy or if API limits are reached"
    }
else
    echo "Skipping market data refresh - no TwelveData API key"
fi

echo ""
echo "=== Starting API Server ==="
echo "Port: ${PORT:-10000}"
echo "Host: 0.0.0.0"

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}