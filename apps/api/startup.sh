#!/bin/bash

echo "Starting Waardhaven API..."

# Initialize database tables
echo "Initializing database..."
python -m app.db_init

# Seed initial assets if needed
echo "Seeding initial assets..."
python -m app.seed_assets

# Refresh market data and calculate index
echo "Refreshing market data..."
python -m app.tasks_refresh || echo "Initial refresh failed, continuing anyway..."

# Start the API server
echo "Starting uvicorn server..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}