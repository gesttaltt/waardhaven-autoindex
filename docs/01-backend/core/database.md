# Database Module

## Overview
Manages database connections and session handling for the PostgreSQL database.

## Location
`apps/api/app/core/database.py`

## Purpose
Provides database connectivity using SQLAlchemy with async support.

## Key Components

### Database URL
- Reads from DATABASE_URL environment variable
- PostgreSQL connection string format
- Supports connection pooling

### SessionLocal
- SQLAlchemy session factory
- Configured for PostgreSQL
- Transaction management

### Base
- Declarative base for models
- Used by all database models
- Handles table metadata

### get_db()
- Dependency injection function
- Provides database sessions
- Automatic session cleanup
- Used in API endpoints

## Database Configuration

### Connection Pool
- Pool size configuration
- Connection recycling
- Timeout settings

### Transaction Management
- Automatic commit/rollback
- Session scoping
- Error handling

## Usage in Routers
```python
from app.core.database import get_db
from sqlalchemy.orm import Session

@router.get("/")
def get_items(db: Session = Depends(get_db)):
    # Use db session
    pass
```

## Database Schema
- Users table
- Assets table
- Prices table
- IndexValues table
- Allocations table
- StrategyConfig table

## Performance Considerations
- Connection pooling enabled
- Lazy loading strategies
- Query optimization needed
- Index creation important

## Dependencies
- sqlalchemy: ORM framework
- psycopg2-binary: PostgreSQL adapter

## Related Modules
- models.py: Defines database models
- All routers: Use get_db dependency