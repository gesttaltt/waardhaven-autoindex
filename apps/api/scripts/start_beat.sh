#!/bin/bash
# Start Celery beat scheduler

echo "Starting Celery beat scheduler..."

# Change to API directory
cd /app || cd apps/api

# Start beat scheduler
celery -A app.core.celery_app beat \
  --loglevel=info \
  --scheduler=celery.beat:PersistentScheduler