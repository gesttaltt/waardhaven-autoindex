-- Performance optimization indexes for Waardhaven AutoIndex
-- Run this on your Render PostgreSQL database

-- Composite index for price queries (most common query pattern)
CREATE INDEX IF NOT EXISTS idx_prices_asset_date 
ON prices(asset_id, date DESC);

-- Index for date-based queries on allocations
CREATE INDEX IF NOT EXISTS idx_allocations_date 
ON allocations(date DESC);

-- Index for date-based queries on index values
CREATE INDEX IF NOT EXISTS idx_index_values_date 
ON index_values(date DESC);

-- Index for finding latest risk metrics
CREATE INDEX IF NOT EXISTS idx_risk_metrics_date 
ON risk_metrics(date DESC);

-- Index for strategy config (though there's usually only one row)
CREATE INDEX IF NOT EXISTS idx_strategy_configs_updated 
ON strategy_configs(updated_at DESC);

-- Partial index for orders that are pending
CREATE INDEX IF NOT EXISTS idx_orders_pending 
ON orders(status, created_at DESC) 
WHERE status = 'pending';

-- Index for user email lookups (for login)
CREATE INDEX IF NOT EXISTS idx_users_email_lower 
ON users(LOWER(email));

-- Analyze tables to update statistics for query planner
ANALYZE prices;
ANALYZE allocations;
ANALYZE index_values;
ANALYZE assets;

-- Show index usage stats (optional - for monitoring)
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;