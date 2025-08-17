# Startup Scripts

## Overview
Various startup scripts for different deployment scenarios and debugging needs.

## Script Files

### startup.sh
Basic startup script for production deployment.

#### Features
- Database connection check
- Environment validation
- Server startup
- Basic error handling
- Logging setup

#### Process
1. Check environment variables
2. Test database connection
3. Run migrations
4. Start Uvicorn server
5. Monitor health

### startup_debug.sh
Enhanced startup with debugging output.

#### Debug Features
- Verbose logging
- Environment variable display
- Connection testing
- Step-by-step execution
- Error details

#### Usage
```bash
# Enable debug mode
export DEBUG=true
./startup_debug.sh
```

### startup_improved.sh
Production-ready startup with improvements.

#### Improvements
- Retry logic for database
- Graceful error handling
- Health check validation
- Resource optimization
- Signal handling

#### Features
- Database retry (5 attempts)
- Migration safety checks
- Worker process management
- Memory limit configuration
- Graceful shutdown

### startup_smart.sh
Intelligent startup with advanced features.

#### Smart Features
- Auto-configuration
- Environment detection
- Performance tuning
- Dependency checking
- Self-healing

#### Capabilities
- Dynamic worker calculation
- Memory-based tuning
- Network optimization
- Cache warming
- Monitoring integration

## Common Functions

### Environment Validation
```bash
check_env_vars() {
  required_vars=(
    "DATABASE_URL"
    "SECRET_KEY"
    "TWELVEDATA_API_KEY"
  )
  
  for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
      echo "Error: $var is not set"
      exit 1
    fi
  done
}
```

### Database Check
```bash
check_database() {
  echo "Checking database connection..."
  python -c "
    from app.core.database import engine
    engine.connect()
    print('Database connected')
  " || {
    echo "Database connection failed"
    return 1
  }
}
```

### Migration Runner
```bash
run_migrations() {
  echo "Running database migrations..."
  alembic upgrade head || {
    echo "Migration failed"
    exit 1
  }
}
```

## Server Configuration

### Uvicorn Settings
```bash
# Production settings
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port ${PORT:-8000} \
  --workers ${WORKERS:-4} \
  --loop uvloop \
  --log-level ${LOG_LEVEL:-info}
```

### Worker Calculation
```bash
# Calculate optimal workers
calculate_workers() {
  cpu_count=$(nproc)
  workers=$((cpu_count * 2 + 1))
  echo $workers
}
```

### Memory Limits
```bash
# Set memory limits
set_memory_limits() {
  ulimit -v ${MAX_MEMORY:-2097152}  # 2GB default
  ulimit -n ${MAX_FILES:-4096}      # File descriptors
}
```

## Health Checks

### Startup Health Check
```bash
health_check() {
  max_attempts=30
  attempt=0
  
  while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:${PORT:-8000}/health; then
      echo "Server is healthy"
      return 0
    fi
    
    attempt=$((attempt + 1))
    sleep 2
  done
  
  echo "Health check failed"
  return 1
}
```

### Continuous Monitoring
```bash
monitor_server() {
  while true; do
    if ! health_check; then
      echo "Server unhealthy, restarting..."
      restart_server
    fi
    sleep 60
  done
}
```

## Error Handling

### Graceful Shutdown
```bash
trap cleanup EXIT INT TERM

cleanup() {
  echo "Shutting down gracefully..."
  kill -TERM $SERVER_PID
  wait $SERVER_PID
  echo "Shutdown complete"
}
```

### Error Recovery
```bash
handle_error() {
  error_code=$1
  case $error_code in
    1) echo "Database error - retrying..." ;;
    2) echo "Migration error - manual intervention needed" ;;
    3) echo "Server start failed - checking ports..." ;;
    *) echo "Unknown error - check logs" ;;
  esac
}
```

## Logging Configuration

### Log Setup
```bash
setup_logging() {
  export LOG_DIR=${LOG_DIR:-/app/logs}
  mkdir -p $LOG_DIR
  
  # Redirect output
  exec 1> >(tee -a $LOG_DIR/startup.log)
  exec 2> >(tee -a $LOG_DIR/error.log)
}
```

### Log Rotation
```bash
rotate_logs() {
  if [ -f $LOG_DIR/startup.log ]; then
    mv $LOG_DIR/startup.log $LOG_DIR/startup.$(date +%Y%m%d).log
  fi
}
```

## Environment Detection

### Development vs Production
```bash
detect_environment() {
  if [ "$NODE_ENV" = "production" ]; then
    export WORKERS=4
    export LOG_LEVEL=info
  else
    export WORKERS=1
    export LOG_LEVEL=debug
    export RELOAD=--reload
  fi
}
```

## Performance Tuning

### Resource Optimization
```bash
optimize_performance() {
  # Enable Python optimizations
  export PYTHONOPTIMIZE=1
  
  # Disable debug
  export PYTHONDONTWRITEBYTECODE=1
  
  # Set garbage collection threshold
  export PYTHONGC=700
}
```

## Docker Integration

### Container Startup
```bash
# Wait for database
wait_for_db() {
  until pg_isready -h $DB_HOST -p $DB_PORT; do
    echo "Waiting for database..."
    sleep 2
  done
}
```

## Monitoring Integration

### Metrics Export
```bash
export_metrics() {
  # Export to monitoring service
  curl -X POST $METRICS_URL \
    -d "startup_time=$(date +%s)" \
    -d "workers=$WORKERS" \
    -d "status=running"
}
```

## Best Practices

### Script Guidelines
- Always validate environment
- Implement retry logic
- Log all operations
- Handle signals properly
- Clean up on exit

### Security
- Don't log sensitive data
- Validate inputs
- Use secure defaults
- Limit permissions
- Audit regularly