#!/bin/bash

# Waardhaven API Unified Startup Script
# Combines all startup functionality with environment-based configuration

set -e

# Configuration from environment
DEBUG_MODE="${DEBUG_MODE:-false}"
SKIP_STARTUP_REFRESH="${SKIP_STARTUP_REFRESH:-false}"
MAX_DB_RETRIES="${MAX_DB_RETRIES:-60}"
REFRESH_TIMEOUT="${REFRESH_TIMEOUT:-120}"
PORT="${PORT:-10000}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_debug() {
    if [ "$DEBUG_MODE" = "true" ]; then
        echo -e "[DEBUG] $1"
    fi
}

# Header
echo "============================================"
echo "Waardhaven API Startup"
echo "============================================"
log_info "Debug Mode: $DEBUG_MODE"
log_info "Skip Refresh: $SKIP_STARTUP_REFRESH"
log_info "Port: $PORT"
echo ""

# Debug information
if [ "$DEBUG_MODE" = "true" ]; then
    log_debug "Current directory: $(pwd)"
    log_debug "Python version: $(python --version)"
    echo ""
fi

# Check environment variables
check_environment() {
    log_info "Checking environment variables..."
    
    local has_errors=false
    
    if [ -z "$DATABASE_URL" ]; then
        log_error "DATABASE_URL is not set!"
        has_errors=true
    else
        log_info "✓ DATABASE_URL is set"
        log_debug "DATABASE_URL: ${DATABASE_URL:0:30}..."
    fi
    
    if [ -z "$SECRET_KEY" ]; then
        log_error "SECRET_KEY is not set!"
        has_errors=true
    else
        log_info "✓ SECRET_KEY is set"
    fi
    
    if [ -z "$TWELVEDATA_API_KEY" ]; then
        log_warn "TWELVEDATA_API_KEY is not set - market data refresh will be limited"
    else
        log_info "✓ TWELVEDATA_API_KEY is set"
    fi
    
    if [ "$has_errors" = true ]; then
        log_error "Missing required environment variables"
        exit 1
    fi
    
    echo ""
}

# Check database connection
check_database() {
    python -c "
import os
import time
from sqlalchemy import create_engine, text

# Get DATABASE_URL directly from environment
database_url = os.getenv('DATABASE_URL')
if not database_url:
    print('DATABASE_URL not set')
    exit(1)

try:
    # Create a simple engine without pooling for connection test
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args={'connect_timeout': 10} if 'postgresql' in database_url else {}
    )
    
    # Try to connect and execute a simple query
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        conn.commit()
    
    engine.dispose()
    exit(0)
except Exception as e:
    if '$DEBUG_MODE' == 'true':
        print(f'Database error: {e}')
    exit(1)
"
    return $?
}

# Wait for database
wait_for_database() {
    log_info "Waiting for database connection..."
    
    local retry_count=0
    
    while [ $retry_count -lt $MAX_DB_RETRIES ]; do
        if check_database; then
            log_info "✓ Database connection successful"
            return 0
        fi
        
        retry_count=$((retry_count+1))
        log_debug "Database connection attempt $retry_count/$MAX_DB_RETRIES"
        sleep 2
    done
    
    log_error "Database connection failed after $MAX_DB_RETRIES attempts"
    return 1
}

# Check database tables
check_tables() {
    python -c "
from app.core.database import SessionLocal
from sqlalchemy import inspect

try:
    db = SessionLocal()
    inspector = inspect(db.bind)
    tables = inspector.get_table_names()
    required_tables = ['users', 'assets', 'prices', 'index_values', 'allocations']
    missing = [t for t in required_tables if t not in tables]
    
    if missing:
        print(f'Missing tables: {missing}')
        exit(1)
    else:
        exit(0)
except Exception as e:
    if '$DEBUG_MODE' == 'true':
        print(f'Error checking tables: {e}')
    exit(1)
finally:
    db.close()
"
    return $?
}

# Initialize database
initialize_database() {
    log_info "Initializing database tables..."
    
    if python -m app.db_init; then
        log_info "✓ Database initialization successful"
        
        if check_tables; then
            log_info "✓ All required tables verified"
        else
            log_warn "Some tables may be missing"
        fi
    else
        log_warn "Database initialization had issues (tables may already exist)"
    fi
    
    echo ""
}

# Seed assets
seed_assets() {
    log_info "Seeding initial assets..."
    
    if python -m app.seed_assets; then
        log_info "✓ Asset seeding successful"
    else
        log_debug "Asset seeding skipped (assets may already exist)"
    fi
    
    echo ""
}

# Check data status
check_data_status() {
    python -c "
from app.core.database import SessionLocal
from app.models import IndexValue, Asset
from sqlalchemy import func

try:
    db = SessionLocal()
    
    asset_count = db.query(func.count()).select_from(Asset).scalar()
    index_count = db.query(func.count()).select_from(IndexValue).scalar()
    
    if '$DEBUG_MODE' == 'true':
        print(f'  Assets: {asset_count}')
        print(f'  Index values: {index_count}')
    
    if index_count > 0:
        exit(0)  # Has data
    else:
        exit(1)  # No data
        
except Exception as e:
    if '$DEBUG_MODE' == 'true':
        print(f'Error checking data: {e}')
    exit(1)
finally:
    db.close()
"
    return $?
}

# Test TwelveData connection
test_twelvedata() {
    if [ -z "$TWELVEDATA_API_KEY" ]; then
        return 1
    fi
    
    if [ "$DEBUG_MODE" = "true" ]; then
        log_info "Testing TwelveData API connection..."
        
        python -c "
from twelvedata import TDClient
import os
try:
    client = TDClient(apikey=os.getenv('TWELVEDATA_API_KEY'))
    quote = client.quote(symbol='AAPL').as_json()
    if quote and 'symbol' in quote:
        print('✓ TwelveData connection successful')
        exit(0)
    else:
        print('✗ TwelveData connection failed - invalid response')
        exit(1)
except Exception as e:
    print(f'✗ TwelveData connection failed: {e}')
    exit(1)
"
        return $?
    fi
    
    return 0
}

# Refresh market data
refresh_market_data() {
    if [ "$SKIP_STARTUP_REFRESH" = "true" ]; then
        log_info "Skipping market data refresh (SKIP_STARTUP_REFRESH=true)"
        return 0
    fi
    
    if check_data_status; then
        log_info "Index data exists, skipping initial refresh"
        return 0
    fi
    
    log_info "Performing market data refresh..."
    
    # Use smart refresh with rate limiting
    timeout $REFRESH_TIMEOUT python -c "
from app.core.database import SessionLocal
from app.services.refresh import refresh_all
import os

db = SessionLocal()
try:
    # Try smart mode first (with rate limiting)
    result = refresh_all(db, smart_mode=True)
    print(f'Refresh completed: {result}')
except Exception as e:
    print(f'Refresh failed (non-critical): {e}')
    print('Continuing with cached/existing data...')
finally:
    db.close()
" || {
    log_warn "Market data refresh failed or timed out"
    log_warn "The API will start but some features may be limited"
    log_warn "You can manually trigger refresh at /api/v1/manual/trigger-refresh"
}
    
    echo ""
}

# Main execution
main() {
    # Check environment
    check_environment
    
    # Wait for database
    if wait_for_database; then
        # Initialize database
        initialize_database
        
        # Seed assets
        seed_assets
        
        # Test TwelveData if in debug mode
        if [ "$DEBUG_MODE" = "true" ]; then
            test_twelvedata || log_warn "TwelveData test failed"
            echo ""
        fi
        
        # Refresh market data
        refresh_market_data
        
        # Final status check
        if [ "$DEBUG_MODE" = "true" ]; then
            log_info "Final data status:"
            check_data_status && log_info "✓ Data is available" || log_warn "⚠ Limited data available"
            echo ""
        fi
    else
        log_warn "Database connection not established during startup"
        log_warn "The API will attempt to connect when handling requests"
        log_info "This is common on Render.com during cold starts"
    fi
    
    # Start Celery worker in background if Redis is available
    if [ ! -z "$REDIS_URL" ]; then
        log_info "Starting Celery worker in background..."
        celery -A app.core.celery_app worker --loglevel=info --detach --pidfile=/tmp/celery.pid
        
        # Start Celery beat scheduler for periodic tasks
        log_info "Starting Celery beat scheduler..."
        celery -A app.core.celery_app beat --loglevel=info --detach --pidfile=/tmp/celerybeat.pid
    else
        log_warn "REDIS_URL not set - background tasks will not be available"
    fi
    
    # Start the API server
    echo "============================================"
    log_info "Starting uvicorn server on port $PORT..."
    echo "============================================"
    
    # Set environment variable to indicate startup without initial DB connection
    export DB_INIT_DELAYED=true
    
    exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
}

# Run main function
main