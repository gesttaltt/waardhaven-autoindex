# Database Models

## Overview
Complete reference for all SQLAlchemy database models in the Waardhaven AutoIndex application.

## Model Architecture

### Core Domain Models
1. **User Management**: `user.py`
2. **Asset Management**: `asset.py` 
3. **Index Management**: `index.py`
4. **Strategy Configuration**: `strategy.py`
5. **News & Sentiment**: `news.py`
6. **Insider Trading**: `insider_trading.py`

## User Models (`app/models/user.py`)

### User
User authentication and account management.

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_google_user = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### Fields
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Indexed | Unique user identifier |
| email | String | Unique, Indexed, Not Null | User email address |
| password_hash | String | Not Null | Bcrypt hashed password |
| is_google_user | Boolean | Default: False | Indicates if user authenticated via Google OAuth |
| created_at | DateTime | Default: utcnow | Account creation timestamp |

#### Indexes
- Primary: `id`
- Unique: `email`

#### Security Notes
- Passwords stored as bcrypt hashes
- Email used as username for authentication
- No sensitive data stored in plain text

## Asset Models (`app/models/asset.py`)

### Asset
Financial instruments (stocks, ETFs, commodities).

```python
class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    sector = Column(String, nullable=True)
```

#### Fields
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key | Unique asset identifier |
| symbol | String | Unique, Indexed, Not Null | Ticker symbol (e.g., "AAPL") |
| name | String | Optional | Full company/asset name |
| sector | String | Optional | Sector classification |

#### Examples
```python
Asset(symbol="AAPL", name="Apple Inc.", sector="Technology")
Asset(symbol="SPY", name="SPDR S&P 500 ETF", sector="Benchmark")
Asset(symbol="GLD", name="SPDR Gold Shares", sector="Commodity")
```

### Price
Historical price data for assets.

```python
class Price(Base):
    __tablename__ = "prices"
    
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    close = Column(Float, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('asset_id', 'date', name='_asset_date_uc'),
    )
```

#### Fields
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key | Unique price record ID |
| asset_id | Integer | Foreign Key, Indexed, Not Null | Reference to Asset |
| date | Date | Indexed, Not Null | Trading date |
| close | Float | Not Null | Closing price |

#### Constraints
- Unique constraint on `(asset_id, date)` prevents duplicates
- Foreign key relationship to assets table

#### Indexes
- Composite: `(asset_id, date)` for efficient queries
- Individual: `asset_id`, `date`

## Index Models (`app/models/index.py`)

### IndexValue
Portfolio index values over time (normalized to base 100).

```python
class IndexValue(Base):
    __tablename__ = "index_values"
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, index=True, nullable=False)
    value = Column(Float, nullable=False)  # base = 100
```

#### Fields
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key | Unique record ID |
| date | Date | Unique, Indexed, Not Null | Trading date |
| value | Float | Not Null | Index value (base 100) |

#### Usage
- Base value of 100 on inception date
- Daily index performance calculations
- Used for portfolio simulation and tracking

### Allocation
Asset allocation weights in the index.

```python
class Allocation(Base):
    __tablename__ = "allocations"
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, index=True, nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True, nullable=False)
    weight = Column(Float, nullable=False)
```

#### Fields
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key | Unique allocation ID |
| date | Date | Indexed, Not Null | Allocation date |
| asset_id | Integer | Foreign Key, Indexed, Not Null | Reference to Asset |
| weight | Float | Not Null | Allocation weight (0.0-1.0) |

#### Business Rules
- Weights should sum to 1.0 for each date
- Represents portfolio composition over time
- Used for rebalancing calculations

## Strategy Models (`app/models/strategy.py`)

### StrategyConfig
Dynamic strategy configuration and parameters.

```python
class StrategyConfig(Base):
    __tablename__ = "strategy_configs"
    
    # Weight parameters (sum should equal 1.0)
    momentum_weight = Column(Float, default=0.4)
    market_cap_weight = Column(Float, default=0.3)  
    risk_parity_weight = Column(Float, default=0.3)
    
    # Risk parameters
    daily_drop_threshold = Column(Float, default=-0.01)
    max_daily_return = Column(Float, default=0.5)
    min_daily_return = Column(Float, default=-0.5)
    min_price_threshold = Column(Float, default=1.0)
    
    # Rebalancing
    rebalance_frequency = Column(String, default="weekly")
    last_rebalance = Column(DateTime)
    force_rebalance = Column(Boolean, default=False)
    
    # Data quality
    max_forward_fill_days = Column(Integer, default=2)
    outlier_std_threshold = Column(Float, default=3.0)
    
    # AI adjustments
    ai_adjusted = Column(Boolean, default=False)
    ai_adjustment_reason = Column(String)
    ai_confidence_score = Column(Float)
    
    # Audit trail
    adjustment_history = Column(JSON, default=list)
```

#### Weight Parameters
| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| momentum_weight | 0.4 | 0.0-1.0 | Momentum strategy weight |
| market_cap_weight | 0.3 | 0.0-1.0 | Market cap strategy weight |
| risk_parity_weight | 0.3 | 0.0-1.0 | Risk parity strategy weight |

#### Risk Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| daily_drop_threshold | -0.01 | Alert threshold (-1%) |
| max_daily_return | 0.5 | Maximum daily return cap |
| min_daily_return | -0.5 | Minimum daily return floor |
| min_price_threshold | 1.0 | Minimum asset price |

#### Rebalancing
| Parameter | Default | Options |
|-----------|---------|---------|
| rebalance_frequency | "weekly" | daily, weekly, monthly, quarterly |
| force_rebalance | False | AI can trigger immediate rebalance |

### RiskMetrics
Calculated risk and performance metrics.

```python
class RiskMetrics(Base):
    __tablename__ = "risk_metrics"
    
    # Performance metrics
    total_return = Column(Float)
    annualized_return = Column(Float)
    daily_return = Column(Float)
    
    # Risk metrics
    volatility = Column(Float)
    sharpe_ratio = Column(Float)
    sortino_ratio = Column(Float)
    max_drawdown = Column(Float)
    current_drawdown = Column(Float)
    
    # Value at Risk
    var_95 = Column(Float)
    var_99 = Column(Float)
    
    # Market comparison
    beta_sp500 = Column(Float)
    correlation_sp500 = Column(Float)
    tracking_error = Column(Float)
    information_ratio = Column(Float)
    
    # AI metrics
    ai_risk_score = Column(Float)
    ai_risk_adjusted_roi = Column(Float)
    ai_market_regime = Column(String)
```

#### Core Metrics
| Metric | Description | Typical Range |
|--------|-------------|---------------|
| sharpe_ratio | Risk-adjusted return | 0.5-3.0 (good) |
| sortino_ratio | Downside risk-adjusted return | Higher is better |
| max_drawdown | Peak-to-trough decline | 0% to -50% |
| volatility | Annualized standard deviation | 10%-30% |

#### Value at Risk
- **var_95**: 5% chance of loss exceeding this value
- **var_99**: 1% chance of loss exceeding this value

#### Market Comparison
- **beta_sp500**: Volatility relative to S&P 500
- **correlation_sp500**: Correlation with S&P 500 (-1 to 1)

### MarketCapData
Market capitalization data for weighting.

```python
class MarketCapData(Base):
    __tablename__ = "market_cap_data"
    
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True)
    date = Column(DateTime, index=True)
    market_cap = Column(Float)  # In USD
    shares_outstanding = Column(Float)
    free_float = Column(Float)  # Available for trading
    average_volume = Column(Float)  # 30-day average
```

## News Models (`app/models/news.py`)

### NewsSource
News source/publisher information.

```python
class NewsSource(Base):
    __tablename__ = 'news_sources'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    domain = Column(String(255))
    country = Column(String(2))
    language = Column(String(2))
    credibility_score = Column(Float, default=0.5)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
```

### NewsArticle
Financial news articles with metadata.

```python
class NewsArticle(Base):
    __tablename__ = 'news_articles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(255), unique=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    content = Column(Text)
    url = Column(String(500), nullable=False, unique=True)
    image_url = Column(String(500))
    source_id = Column(UUID(as_uuid=True), ForeignKey('news_sources.id'))
    source_name = Column(String(100))
    language = Column(String(2), default='en')
    country = Column(String(2))
    published_at = Column(DateTime(timezone=True), nullable=False)
    categories = Column(JSON, default=list)
    keywords = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
```

### NewsSentiment
Sentiment analysis results for articles.

```python
class NewsSentiment(Base):
    __tablename__ = 'news_sentiment'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey('news_articles.id'), nullable=False, unique=True)
    sentiment_score = Column(Float, nullable=False)  # -1 to 1
    sentiment_label = Column(String(20))  # positive, negative, neutral
    confidence = Column(Float, default=0.5)  # 0 to 1
    positive_score = Column(Float)
    negative_score = Column(Float)
    neutral_score = Column(Float)
    provider = Column(String(50))
    analyzed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
```

### NewsEntity
Entities (companies, people, products) mentioned in articles.

```python
class NewsEntity(Base):
    __tablename__ = 'news_entities'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey('news_articles.id'), nullable=False)
    symbol = Column(String(20))
    name = Column(String(255), nullable=False)
    type = Column(String(50))  # company, person, location, product
    exchange = Column(String(20))
    country = Column(String(2))
    industry = Column(String(100))
    match_score = Column(Float)
    sentiment_score = Column(Float)
    mention_count = Column(Integer, default=1)
```

### Asset-News Association Table
Many-to-many relationship between assets and news articles.

```python
asset_news_association = Table(
    'asset_news',
    Base.metadata,
    Column('asset_id', Integer, ForeignKey('assets.id'), primary_key=True),  # Should be Integer
    Column('article_id', UUID(as_uuid=True), ForeignKey('news_articles.id'), primary_key=True),
    Column('relevance_score', Float, default=1.0),
    Column('sentiment_score', Float),
    Column('created_at', DateTime(timezone=True), default=datetime.utcnow)
)
```

**⚠️ CODE BUG**: The actual implementation in `app/models/news.py` incorrectly uses UUID for asset_id, but `assets.id` is Integer. This type mismatch will cause database foreign key errors.

### EntitySentimentHistory
Historical sentiment tracking for entities over time.

```python
class EntitySentimentHistory(Base):
    __tablename__ = 'entity_sentiment_history'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    sentiment_score = Column(Float, nullable=False)
    article_count = Column(Integer, default=0)
    positive_count = Column(Integer, default=0)
    negative_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    total_mentions = Column(Integer, default=0)
    unique_sources = Column(Integer, default=0)
```

## Relationships

### Entity Relationship Diagram
```
users (1) ─── (∞) [future: portfolios]
assets (1) ─── (∞) prices
assets (1) ─── (∞) allocations
assets (1) ─── (∞) market_cap_data
assets (∞) ─── (∞) news_articles (via asset_news)
news_sources (1) ─── (∞) news_articles
news_articles (1) ─── (1) news_sentiment
news_articles (1) ─── (∞) news_entities
```

### Foreign Key Relationships
- `prices.asset_id` → `assets.id`
- `news_articles.source_id` → `news_sources.id`
- `news_sentiment.article_id` → `news_articles.id`
- `news_entities.article_id` → `news_articles.id`
- `asset_news.asset_id` → `assets.id`
- `asset_news.article_id` → `news_articles.id`
- `allocations.asset_id` → `assets.id`
- `market_cap_data.asset_id` → `assets.id`

## Indexes and Performance

### Composite Indexes
```sql
-- High-performance indexes for common queries
CREATE INDEX idx_price_asset_date ON prices(asset_id, date);
CREATE INDEX idx_allocation_date ON allocations(date);
CREATE INDEX idx_index_value_date ON index_values(date);
CREATE INDEX idx_risk_metrics_date ON risk_metrics(date);
```

### Query Patterns
```python
# Efficient queries using indexes
prices = db.query(Price).filter(
    Price.asset_id == asset_id,
    Price.date >= start_date
).order_by(Price.date)

# Latest allocations
allocations = db.query(Allocation).filter(
    Allocation.date == latest_date
).all()
```

## Audit Trail Features

### Timestamp Columns
Most tables include automatic timestamp tracking:
```python
created_at = Column(DateTime, server_default=func.now())
updated_at = Column(DateTime, onupdate=func.now())
```

### JSON History
`StrategyConfig.adjustment_history` stores change history:
```json
[
  {
    "timestamp": "2024-01-15T10:30:00Z",
    "changes": {"momentum_weight": 0.45},
    "user_id": 123,
    "reason": "Market volatility increase"
  }
]
```

## Data Validation

### Model-Level Constraints
- Unique constraints prevent duplicates
- Foreign keys ensure referential integrity
- NOT NULL constraints ensure required fields

### Application-Level Validation
- Pydantic schemas validate inputs
- Business logic ensures weight sums = 1.0
- Range checks for reasonable values

## Migration Considerations

### Schema Evolution
- Use Alembic for schema changes
- Automatic index creation on startup
- Backward-compatible modifications

### Data Integrity
- Always use transactions for multi-table operations
- Validate data consistency after migrations
- Backup before major schema changes

## Performance Optimization

### Bulk Operations
```python
# Efficient bulk insert
db.bulk_insert_mappings(Price, price_data)

# Bulk update with ON CONFLICT
stmt = insert(Price).values(data)
stmt = stmt.on_conflict_do_update(
    index_elements=['asset_id', 'date'],
    set_={'close': stmt.excluded.close}
)
```

### Query Optimization
1. Use appropriate indexes
2. Limit result sets with pagination
3. Use eager loading for relationships
4. Cache frequently accessed data

## Security Features

### Data Protection
- Password hashing with bcrypt
- No sensitive data in plain text
- Audit trails for configuration changes

### Access Control
- User-based authentication
- Admin token for sensitive operations
- Input validation and sanitization

## Insider Trading Models (`app/models/insider_trading.py`)

### InsiderProfile
Profiles of insider traders including politicians, executives, and institutional investors.

```python
class InsiderProfile(Base):
    __tablename__ = 'insider_profiles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(255), nullable=False)
    trader_type = Column(Enum(TraderType), nullable=False)  # corporate_executive, senator, etc.
    title = Column(String(255))  # CEO, Senator from NY, etc.
    organization = Column(String(255))  # Company or Government body
    state = Column(String(2))  # For politicians
    party = Column(String(50))  # For politicians
    total_trades = Column(Integer, default=0)
    profitable_trades = Column(Integer, default=0)
    average_return = Column(Float)
    win_rate = Column(Float)
```

#### Trader Types
- `CORPORATE_EXECUTIVE` - CEOs, CFOs, CTOs
- `CORPORATE_DIRECTOR` - Board members
- `MAJOR_SHAREHOLDER` - 10%+ ownership
- `SENATOR` - US Senators
- `REPRESENTATIVE` - House Representatives
- `GOVERNMENT_OFFICIAL` - Other government positions
- `INSTITUTIONAL` - Hedge funds, mutual funds

### InsiderTransaction
Individual insider trading transactions with performance tracking.

```python
class InsiderTransaction(Base):
    __tablename__ = 'insider_transactions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trader_id = Column(UUID(as_uuid=True), ForeignKey('insider_profiles.id'), nullable=False)
    symbol = Column(String(20), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)  # buy, sell, option_exercise
    shares = Column(Integer)
    price_per_share = Column(Float)
    total_value = Column(Float)
    transaction_date = Column(Date, nullable=False)
    filing_date = Column(Date, nullable=False)
    delay_days = Column(Integer)  # Days between transaction and filing
    
    # Performance tracking
    price_1d_after = Column(Float)
    price_7d_after = Column(Float)
    price_30d_after = Column(Float)
    price_90d_after = Column(Float)
    return_1d = Column(Float)
    return_7d = Column(Float)
    return_30d = Column(Float)
    return_90d = Column(Float)
    
    # Flags
    is_10b5_1 = Column(Boolean, default=False)  # Planned trade
    is_unusual = Column(Boolean, default=False)  # Flagged as unusual
    is_clustered = Column(Boolean, default=False)  # Part of cluster
```

### InstitutionalHolding
13F filings and institutional holdings tracking.

```python
class InstitutionalHolding(Base):
    __tablename__ = 'institutional_holdings'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_name = Column(String(255), nullable=False)
    cik = Column(String(20))  # SEC CIK number
    symbol = Column(String(20), nullable=False)
    shares_held = Column(Integer, nullable=False)
    market_value = Column(Float)
    percentage_of_portfolio = Column(Float)
    percentage_of_shares_outstanding = Column(Float)
    shares_change = Column(Integer)
    shares_change_percentage = Column(Float)
    report_date = Column(Date, nullable=False)  # Quarter end date
    filing_date = Column(Date, nullable=False)
```

### InsiderCluster
Clusters of coordinated insider trading activity.

```python
class InsiderCluster(Base):
    __tablename__ = 'insider_clusters'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False)
    cluster_type = Column(String(50))  # political, executive, institutional
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    transaction_count = Column(Integer, nullable=False)
    unique_traders = Column(Integer, nullable=False)
    total_value = Column(Float)
    net_shares = Column(Integer)  # Net bought/sold
    cluster_score = Column(Float)  # Significance score
    sentiment = Column(String(20))  # bullish, bearish, mixed
```

### InsiderAlert
Alerts for unusual insider trading patterns.

```python
class InsiderAlert(Base):
    __tablename__ = 'insider_alerts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_type = Column(String(50), nullable=False)  # unusual_volume, cluster, pattern
    severity = Column(String(20))  # low, medium, high, critical
    symbol = Column(String(20))
    trader_id = Column(UUID(as_uuid=True), ForeignKey('insider_profiles.id'))
    cluster_id = Column(UUID(as_uuid=True), ForeignKey('insider_clusters.id'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    was_accurate = Column(Boolean)  # Was the alert predictive?
```

### InsiderPerformance
Performance metrics for insider traders over time periods.

```python
class InsiderPerformance(Base):
    __tablename__ = 'insider_performance'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trader_id = Column(UUID(as_uuid=True), ForeignKey('insider_profiles.id'), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    period_type = Column(String(20))  # monthly, quarterly, yearly
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    win_rate = Column(Float)
    average_return = Column(Float)
    market_return = Column(Float)  # S&P 500 return for period
    alpha = Column(Float)  # Excess return vs market
```

### Insider Trading Indexes
Comprehensive indexing for high-performance queries:
- `ix_insider_profiles_name` - Search by trader name
- `ix_insider_transactions_symbol_date` - Find trades by symbol and date
- `ix_insider_transactions_value` - High-value transaction queries
- `ix_institutional_holdings_symbol` - Holdings by symbol
- `ix_insider_clusters_score` - Most significant clusters
- `ix_insider_alerts_severity` - Priority alerts

### Use Cases
1. **Track Political Trading**: Monitor congressional stock trades
2. **Detect Unusual Patterns**: Identify suspicious trading clusters
3. **Follow Smart Money**: Track high-performing insider traders
4. **13F Analysis**: Monitor institutional position changes
5. **Alert Generation**: Real-time alerts for significant activity