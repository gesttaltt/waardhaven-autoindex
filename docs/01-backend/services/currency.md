# Currency Service

## Overview
Handles multi-currency support and foreign exchange conversions.

## Location
`apps/api/app/services/currency.py`

## Core Functions

### get_exchange_rate(from_currency, to_currency)
- Fetch current FX rates
- Cache for performance
- Fallback mechanisms
- Error handling

### convert_amount(amount, from_currency, to_currency)
- Currency conversion
- Precision handling
- Rate application
- Rounding rules

### get_supported_currencies()
- List available currencies
- Currency metadata
- Symbol mapping
- Display names

## Supported Currencies

### Major Currencies
- USD (US Dollar)
- EUR (Euro)
- GBP (British Pound)
- JPY (Japanese Yen)
- CHF (Swiss Franc)

### Additional Currencies
- CAD, AUD, NZD
- CNY, HKD, SGD
- SEK, NOK, DKK
- 20+ total currencies

## Data Sources

### Primary Source
- TwelveData FX rates
- Real-time updates
- Historical rates
- Cross rates

### Fallback Sources
- Cached rates
- Default rates
- Manual overrides

## Conversion Logic

### Rate Calculation
- Direct rates
- Cross rate calculation
- Triangulation
- Spread consideration

### Precision Handling
- Decimal places
- Rounding methods
- Significant figures
- Display formatting

## Caching Strategy

### Rate Caching
- TTL: 5 minutes
- Invalidation triggers
- Stale data handling
- Cache warming

### Performance
- Batch fetching
- Lazy loading
- Memory optimization
- Query reduction

## Portfolio Impact

### Multi-Currency Portfolios
- Base currency setting
- Asset currency tracking
- Performance calculation
- Reporting currency

### FX Impact Analysis
- Currency attribution
- Hedging calculations
- Risk assessment
- Performance impact

## Error Handling

### Rate Unavailable
- Use cached rates
- Apply defaults
- User notification
- Manual override

### Invalid Currency
- Validation checks
- Error messages
- Suggested alternatives
- Fallback options

## API Integration

### Endpoints Used
- /exchange_rate
- /currency_list
- /historical_rates

### Request Management
- Rate limiting
- Batch requests
- Error recovery
- Retry logic

## Dependencies
- TwelveData client
- Cache service
- Database models
- Validation utilities