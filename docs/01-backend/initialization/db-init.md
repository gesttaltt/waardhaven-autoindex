# Database Initialization

## Overview
Database setup and initialization process for the application.

## Location
`apps/api/app/db_init.py`

## Purpose
Creates database schema and initial setup for PostgreSQL database.

## Initialization Process

### Schema Creation
- Create all tables
- Set up relationships
- Apply constraints
- Create indexes

### Initial Data
- Default configurations
- System settings
- Reference data
- Admin user (optional)

## Tables Created

### Core Tables
- users
- assets
- prices
- index_values
- allocations

### Configuration Tables
- strategy_config
- risk_metrics
- market_cap_data

## Dependencies
- SQLAlchemy Base
- Database connection
- Model definitions
- Environment config
