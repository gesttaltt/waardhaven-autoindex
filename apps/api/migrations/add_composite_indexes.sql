-- Add composite indexes for better query performance
-- Run this migration to improve database performance

-- Price table: Most queries filter by asset_id and date
CREATE INDEX IF NOT EXISTS idx_price_asset_date ON prices(asset_id, date);
CREATE INDEX IF NOT EXISTS idx_price_date ON prices(date);
CREATE INDEX IF NOT EXISTS idx_price_asset_id ON prices(asset_id);

-- Allocation table: Queries often filter by date
CREATE INDEX IF NOT EXISTS idx_allocation_date ON allocations(date);
CREATE INDEX IF NOT EXISTS idx_allocation_asset_date ON allocations(asset_id, date);

-- Index values table: Queries filter by date
CREATE INDEX IF NOT EXISTS idx_index_value_date ON index_values(date);

-- Add timestamp columns for audit trail (if not exists)
DO $$ 
BEGIN
    -- Add created_at to prices if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='prices' AND column_name='created_at') THEN
        ALTER TABLE prices ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
    
    -- Add updated_at to prices if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='prices' AND column_name='updated_at') THEN
        ALTER TABLE prices ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
    
    -- Add created_at to allocations if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='allocations' AND column_name='created_at') THEN
        ALTER TABLE allocations ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
    
    -- Add updated_at to allocations if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='allocations' AND column_name='updated_at') THEN
        ALTER TABLE allocations ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
    
    -- Add created_at to index_values if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='index_values' AND column_name='created_at') THEN
        ALTER TABLE index_values ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
    
    -- Add updated_at to index_values if not exists
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

-- Analyze tables to update statistics for query planner
ANALYZE prices;
ANALYZE allocations;
ANALYZE index_values;

-- Show created indexes
SELECT schemaname, tablename, indexname, indexdef
FROM pg_indexes
WHERE tablename IN ('prices', 'allocations', 'index_values')
ORDER BY tablename, indexname;