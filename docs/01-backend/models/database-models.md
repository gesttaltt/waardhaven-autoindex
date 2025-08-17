# Database Models

## Overview
SQLAlchemy ORM models defining the database schema for the application.

## Location
`apps/api/app/models.py`

## Core Models

### User Model
- User authentication and profile
- Fields: id, email, username, password_hash
- Relationships: portfolios, transactions
- Authentication integration

### Asset Model
- Investment assets/securities
- Fields: id, symbol, name, asset_type, sector
- Market data association
- Portfolio inclusion

### Price Model
- Historical and current prices
- Fields: id, asset_id, date, open, high, low, close, volume
- Time series data
- Data quality tracking

### IndexValue Model
- Calculated index values
- Fields: id, date, value, return_pct
- Performance tracking
- Historical record

### Allocation Model
- Portfolio allocations
- Fields: id, date, asset_id, weight, value
- Rebalancing history
- Strategy application

### StrategyConfig Model
- Strategy parameters
- Fields: id, name, parameters, active
- User customization
- Version control

### RiskMetrics Model
- Calculated risk metrics
- Fields: id, date, volatility, sharpe_ratio, max_drawdown
- Performance analytics
- Risk monitoring

### MarketCapData Model
- Market capitalization data
- Fields: id, asset_id, date, market_cap
- Fundamental data
- Weight calculations

## Relationships

### One-to-Many
- User → Portfolios
- Asset → Prices
- Asset → Allocations
- Strategy → Configurations

### Many-to-Many
- Portfolio ↔ Assets
- User ↔ Strategies

## Database Constraints

### Unique Constraints
- User email
- Asset symbol
- Price (asset_id, date)
- Allocation (date, asset_id)

### Foreign Keys
- Cascading deletes
- Referential integrity
- Null handling

## Indexes

### Performance Indexes
- Price lookups by date
- Asset queries by symbol
- User lookups by email
- Allocation queries by date

## Data Types

### Numeric Fields
- DECIMAL for prices
- FLOAT for percentages
- INTEGER for counts
- BIGINT for IDs

### Date/Time Fields
- DATE for daily data
- TIMESTAMP for events
- Time zone handling

### Text Fields
- VARCHAR for symbols
- TEXT for descriptions
- JSON for flexible data

## Model Methods

### Instance Methods
- Validation logic
- Calculation methods
- Serialization
- Business logic

### Class Methods
- Query builders
- Bulk operations
- Factory methods
- Aggregations

## Migration Strategy

### Version Control
- Alembic migrations
- Schema versioning
- Rollback capability
- Data preservation

## Performance Considerations

### Query Optimization
- Eager loading
- Query batching
- Connection pooling
- Caching strategy

## Data Integrity

### Validation
- Field validators
- Business rules
- Data quality checks
- Consistency rules

## Dependencies
- SQLAlchemy ORM
- PostgreSQL database
- Pydantic schemas
- Database migrations