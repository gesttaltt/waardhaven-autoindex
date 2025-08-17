"""
Run database migrations including index creation.
This can be called from the application startup or manually.
"""
import os
import logging
from sqlalchemy import text
from ..core.database import engine

logger = logging.getLogger(__name__)

def run_index_migration():
    """Create database indexes for performance optimization."""
    
    migration_sql = """
    -- Add composite indexes for better query performance
    CREATE INDEX IF NOT EXISTS idx_price_asset_date ON prices(asset_id, date);
    CREATE INDEX IF NOT EXISTS idx_price_date ON prices(date);
    CREATE INDEX IF NOT EXISTS idx_price_asset_id ON prices(asset_id);
    CREATE INDEX IF NOT EXISTS idx_allocation_date ON allocations(date);
    CREATE INDEX IF NOT EXISTS idx_allocation_asset_date ON allocations(asset_id, date);
    CREATE INDEX IF NOT EXISTS idx_index_value_date ON index_values(date);
    
    -- Add timestamp columns if they don't exist
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name='prices' AND column_name='created_at') THEN
            ALTER TABLE prices ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name='prices' AND column_name='updated_at') THEN
            ALTER TABLE prices ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name='allocations' AND column_name='created_at') THEN
            ALTER TABLE allocations ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name='allocations' AND column_name='updated_at') THEN
            ALTER TABLE allocations ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name='index_values' AND column_name='created_at') THEN
            ALTER TABLE index_values ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name='index_values' AND column_name='updated_at') THEN
            ALTER TABLE index_values ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        END IF;
    END $$;
    
    -- Create function to automatically update updated_at timestamp
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    
    -- Create triggers to auto-update updated_at
    DROP TRIGGER IF EXISTS update_prices_updated_at ON prices;
    CREATE TRIGGER update_prices_updated_at BEFORE UPDATE ON prices
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
    DROP TRIGGER IF EXISTS update_allocations_updated_at ON allocations;
    CREATE TRIGGER update_allocations_updated_at BEFORE UPDATE ON allocations
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
    DROP TRIGGER IF EXISTS update_index_values_updated_at ON index_values;
    CREATE TRIGGER update_index_values_updated_at BEFORE UPDATE ON index_values
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
    -- Update statistics for query planner
    ANALYZE prices;
    ANALYZE allocations;
    ANALYZE index_values;
    """
    
    try:
        with engine.begin() as conn:
            logger.info("Running database index migration...")
            
            # Execute migration
            conn.execute(text(migration_sql))
            
            # Verify indexes were created
            result = conn.execute(text("""
                SELECT COUNT(*) as index_count
                FROM pg_indexes
                WHERE tablename IN ('prices', 'allocations', 'index_values')
                AND indexname LIKE 'idx_%'
            """))
            
            index_count = result.fetchone()[0]
            logger.info(f"Migration completed. {index_count} custom indexes found.")
            
            # Log index details
            result = conn.execute(text("""
                SELECT tablename, indexname
                FROM pg_indexes
                WHERE tablename IN ('prices', 'allocations', 'index_values')
                AND indexname LIKE 'idx_%'
                ORDER BY tablename, indexname
            """))
            
            for row in result:
                logger.info(f"  Index: {row[1]} on table {row[0]}")
            
            return True
            
    except Exception as e:
        logger.error(f"Failed to run index migration: {e}")
        return False

def run_all_migrations():
    """Run all pending database migrations."""
    
    migrations = [
        ("indexes", run_index_migration),
    ]
    
    success_count = 0
    for name, migration_func in migrations:
        logger.info(f"Running migration: {name}")
        if migration_func():
            success_count += 1
            logger.info(f"Migration {name} completed successfully")
        else:
            logger.error(f"Migration {name} failed")
    
    logger.info(f"Migrations complete: {success_count}/{len(migrations)} successful")
    return success_count == len(migrations)

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Run migrations
    if run_all_migrations():
        print("All migrations completed successfully")
    else:
        print("Some migrations failed. Check logs for details.")
        exit(1)