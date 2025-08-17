# Multi-Currency Support

## Overview
Comprehensive multi-currency functionality allowing users to invest and track portfolios in various currencies.

## Supported Currencies

### Major Currencies (20+)
- **USD** - US Dollar (base)
- **EUR** - Euro
- **GBP** - British Pound
- **JPY** - Japanese Yen
- **CHF** - Swiss Franc
- **CAD** - Canadian Dollar
- **AUD** - Australian Dollar
- **NZD** - New Zealand Dollar
- **CNY** - Chinese Yuan
- **HKD** - Hong Kong Dollar
- **SGD** - Singapore Dollar
- **SEK** - Swedish Krona
- **NOK** - Norwegian Krone
- **DKK** - Danish Krone
- **PLN** - Polish Zloty
- **MXN** - Mexican Peso
- **ZAR** - South African Rand
- **BRL** - Brazilian Real
- **INR** - Indian Rupee
- **KRW** - South Korean Won

## Implementation Details

### Currency Service
Located in `apps/api/app/services/currency.py`

#### Core Functions
- `get_exchange_rate()` - Fetch current FX rates
- `convert_amount()` - Convert between currencies
- `get_supported_currencies()` - List available currencies
- `update_fx_rates()` - Refresh exchange rates

### Data Source
- **TwelveData API** for real-time FX rates
- Automatic rate updates every hour
- Fallback to cached rates if API unavailable
- Historical rates for backtesting

## User Features

### Portfolio Currency
- Select base currency during setup
- All values displayed in chosen currency
- Performance calculated in base currency
- Easy currency switching

### Currency Conversion
- Real-time conversion rates
- Automatic updates
- Historical rate tracking
- Transaction currency recording

### Multi-Currency Assets
- Track assets in original currency
- Convert to portfolio currency
- Show both values
- Currency impact analysis

## Technical Implementation

### Database Schema
```sql
-- User preferences
user_currency VARCHAR(3) DEFAULT 'USD'

-- Transaction recording
original_currency VARCHAR(3)
original_amount DECIMAL(20,2)
converted_amount DECIMAL(20,2)
exchange_rate DECIMAL(10,6)

-- FX rate cache
currency_pair VARCHAR(7)
rate DECIMAL(10,6)
timestamp TIMESTAMP
```

### API Endpoints
- `GET /api/v1/currencies` - List supported currencies
- `GET /api/v1/currencies/rates` - Current exchange rates
- `POST /api/v1/users/currency` - Update user currency
- `GET /api/v1/portfolio/value?currency=EUR` - Get value in specific currency

## Conversion Logic

### Rate Calculation
```python
def convert_amount(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount
    
    # Direct rate if available
    rate = get_direct_rate(from_currency, to_currency)
    
    # Cross rate through USD if needed
    if not rate:
        rate = get_cross_rate(from_currency, to_currency)
    
    return amount * rate
```

### Portfolio Valuation
1. Get asset prices in original currencies
2. Convert each to user's base currency
3. Sum total portfolio value
4. Cache for performance

## Performance Considerations

### Caching Strategy
- Exchange rates cached for 1 hour
- Portfolio values cached for 5 minutes
- User preference cached in session
- Batch conversions for efficiency

### Optimization
- Minimize API calls
- Bulk rate fetching
- Pre-calculate common conversions
- Use database for historical rates

## User Experience

### Currency Selection
- Dropdown in user settings
- Flag icons for recognition
- Search functionality
- Popular currencies first

### Display Options
- Show original currency
- Show converted value
- Display exchange rate
- Toggle between currencies

### Reporting
- Statements in chosen currency
- Tax reports with conversions
- Performance in multiple currencies
- Currency impact breakdown

## Currency Impact Analysis

### Performance Attribution
- Separate investment returns from FX impact
- Show currency contribution to returns
- Historical FX performance
- Hedging opportunities

### Risk Metrics
- Currency volatility
- Correlation analysis
- Exposure reporting
- Diversification benefits

## Edge Cases

### Handling Issues
- Missing exchange rates
- Weekend/holiday rates
- Extreme volatility
- Currency redenomination
- Discontinued currencies

### Fallback Mechanisms
- Use last known rate
- Apply average rates
- Manual rate override
- Admin intervention

## Compliance

### Regulatory Requirements
- Accurate rate sourcing
- Audit trail for conversions
- Transparent methodology
- Regular rate updates

### Tax Implications
- Track conversion dates
- Store historical rates
- Provide tax reports
- Cost basis tracking

## Future Enhancements

### Planned Features
- Cryptocurrency support
- Real-time streaming rates
- Currency hedging options
- Multi-currency portfolios
- Forward contracts

### Advanced Analytics
- Currency correlation matrix
- Optimal currency allocation
- Risk-adjusted returns by currency
- Currency momentum strategies

## Testing

### Test Coverage
- Rate conversion accuracy
- Edge case handling
- Performance under load
- Cache invalidation
- API failure scenarios

### Validation
- Compare with multiple sources
- Historical rate verification
- Calculation accuracy
- User acceptance testing

## Monitoring

### Metrics Tracked
- Conversion accuracy
- API response times
- Cache hit rates
- Error rates
- User currency distribution

### Alerts
- Rate discrepancies
- API failures
- Unusual volatility
- Conversion errors
- Performance degradation