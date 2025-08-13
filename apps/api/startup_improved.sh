#!/bin/bash

echo "============================================"
echo "Starting Waardhaven API - Improved Startup"
echo "============================================"

# Function to check if database is accessible
check_database() {
    echo "Checking database connection..."
    python -c "
from app.core.database import SessionLocal
try:
    db = SessionLocal()
    db.execute('SELECT 1')
    db.close()
    print('✓ Database connection successful')
    exit(0)
except Exception as e:
    print(f'✗ Database connection failed: {e}')
    exit(1)
"
    return $?
}

# Function to check if tables exist
check_tables() {
    echo "Checking database tables..."
    python -c "
from app.core.database import SessionLocal
from app.models import Asset, Price, IndexValue
from sqlalchemy import inspect

try:
    db = SessionLocal()
    inspector = inspect(db.bind)
    tables = inspector.get_table_names()
    required_tables = ['users', 'assets', 'prices', 'index_values', 'allocations']
    missing = [t for t in required_tables if t not in tables]
    
    if missing:
        print(f'✗ Missing tables: {missing}')
        exit(1)
    else:
        print('✓ All required tables exist')
        exit(0)
except Exception as e:
    print(f'✗ Error checking tables: {e}')
    exit(1)
finally:
    db.close()
"
    return $?
}

# Function to check data status
check_data_status() {
    echo "Checking data status..."
    python -c "
from app.core.database import SessionLocal
from app.models import IndexValue, Asset
from sqlalchemy import func

try:
    db = SessionLocal()
    
    # Check assets
    asset_count = db.query(func.count()).select_from(Asset).scalar()
    print(f'  Assets: {asset_count}')
    
    # Check index values
    index_count = db.query(func.count()).select_from(IndexValue).scalar()
    print(f'  Index values: {index_count}')
    
    if index_count > 0:
        print('✓ Data is available')
        exit(0)
    else:
        print('⚠ No index data available')
        exit(1)
        
except Exception as e:
    print(f'✗ Error checking data: {e}')
    exit(1)
finally:
    db.close()
"
    return $?
}

# Step 1: Wait for database to be ready
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if check_database; then
        break
    fi
    echo "Waiting for database... (attempt $((RETRY_COUNT+1))/$MAX_RETRIES)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT+1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "ERROR: Database connection failed after $MAX_RETRIES attempts"
    echo "Starting API anyway (may have limited functionality)"
else
    echo "Database is ready!"
fi

# Step 2: Initialize database tables
echo ""
echo "Initializing database tables..."
python -m app.db_init || {
    echo "WARNING: Database initialization had issues"
}

# Step 3: Check if tables were created
if check_tables; then
    echo "Database tables verified!"
else
    echo "WARNING: Some tables may be missing"
fi

# Step 4: Seed initial assets
echo ""
echo "Seeding initial assets..."
python -m app.seed_assets || {
    echo "WARNING: Asset seeding had issues"
}

# Step 5: Check if we need to refresh market data
echo ""
if check_data_status; then
    echo "Index data exists, skipping initial refresh"
else
    echo "No index data found, attempting initial refresh..."
    
    # Try to refresh with timeout
    timeout 120 python -m app.tasks_refresh && {
        echo "✓ Initial refresh completed successfully"
    } || {
        echo "⚠ WARNING: Initial refresh failed or timed out"
        echo "The API will start but simulation features may not work"
        echo "You can manually trigger refresh at /api/v1/manual/trigger-refresh"
    }
fi

# Step 6: Final data check
echo ""
echo "Final data status:"
check_data_status || true

# Step 7: Start the API server
echo ""
echo "============================================"
echo "Starting uvicorn server on port ${PORT:-10000}..."
echo "============================================"
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}