#!/bin/bash
# Start Flower monitoring dashboard

echo "Starting Flower monitoring dashboard..."

# Change to API directory
cd /app || cd apps/api

# Start Flower on port 5555
celery -A app.core.celery_app flower \
  --port=5555 \
  --basic_auth=admin:password \
  --url_prefix=flower