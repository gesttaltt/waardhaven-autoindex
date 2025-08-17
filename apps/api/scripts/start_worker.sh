#!/bin/bash
# Start Celery worker

echo "Starting Celery worker..."

# Change to API directory
cd /app || cd apps/api

# Start worker with appropriate settings
celery -A app.core.celery_app worker \
  --loglevel=info \
  --concurrency=2 \
  --queues=high_priority,low_priority \
  --hostname=worker@%h \
  --max-tasks-per-child=50 \
  --time-limit=1800 \
  --soft-time-limit=1500