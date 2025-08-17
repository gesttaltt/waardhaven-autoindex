# Pydantic Schemas

## Overview
Pydantic models for request/response validation and serialization.

## Location
`apps/api/app/schemas.py`

## Purpose
Define data structures for API communication with automatic validation.

## User Schemas

### UserCreate
- Registration payload
- Email, username, password
- Validation rules
- Password requirements

### UserLogin
- Authentication payload
- Email/username, password
- Token generation

### UserResponse
- User data response
- Excludes password
- Includes metadata

## Portfolio Schemas

### PortfolioCreate
- New portfolio request
- Name, initial capital
- Strategy selection
- Currency preference

### PortfolioResponse
- Portfolio details
- Current value
- Performance metrics
- Allocation data

## Asset Schemas

### AssetBase
- Basic asset info
- Symbol, name, type
- Sector classification

### AssetWithPrice
- Asset with current price
- Latest market data
- Change percentages

## Price Schemas

### PriceData
- OHLCV data
- Timestamp
- Volume information
- Data quality flags

### PriceHistory
- Historical prices
- Date range
- Aggregation level

## Allocation Schemas

### AllocationRequest
- Rebalancing request
- Target weights
- Constraints

### AllocationResponse
- Current allocations
- Asset weights
- Values and changes

## Strategy Schemas

### StrategyConfig
- Strategy parameters
- Weight allocations
- Thresholds
- Frequency settings

### StrategyUpdate
- Parameter updates
- Validation rules
- Constraints

## Performance Schemas

### PerformanceMetrics
- Return calculations
- Risk metrics
- Comparison data
- Time periods

### BenchmarkComparison
- Index comparison
- Relative performance
- Tracking error

## Validation Rules

### Email Validation
- Format checking
- Domain validation
- Uniqueness check

### Password Rules
- Minimum length
- Complexity requirements
- Special characters

### Numeric Validation
- Range constraints
- Precision limits
- Positive values

### Date Validation
- Format checking
- Range limits
- Business days

## Serialization

### JSON Encoding
- Datetime handling
- Decimal precision
- Null values
- Nested objects

### Response Formatting
- Consistent structure
- Error messages
- Pagination
- Metadata

## Type Hints

### Optional Fields
- Default values
- Nullable fields
- Union types

### Complex Types
- Lists and dicts
- Nested schemas
- Generic types

## Error Schemas

### ValidationError
- Field errors
- Error messages
- Error codes

### APIError
- Status codes
- Error details
- Stack traces

## Dependencies
- Pydantic v2
- Type hints
- Email validator
- Custom validators