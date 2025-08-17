from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Date, UniqueConstraint, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from .core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    sector = Column(String, nullable=True)

class Price(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    close = Column(Float, nullable=False)
    __table_args__ = (UniqueConstraint('asset_id', 'date', name='_asset_date_uc'),)

class IndexValue(Base):
    __tablename__ = "index_values"
    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, index=True, nullable=False)
    value = Column(Float, nullable=False)  # base = 100

class Allocation(Base):
    __tablename__ = "allocations"
    id = Column(Integer, primary_key=True)
    date = Column(Date, index=True, nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True, nullable=False)
    weight = Column(Float, nullable=False)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    asset_symbol = Column(String, nullable=False)
    type = Column(String, nullable=False)  # "BUY" / "SELL"
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, nullable=True)


class StrategyConfig(Base):
    """Stores dynamic strategy weights and parameters."""
    __tablename__ = "strategy_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Weight parameters (sum should equal 1.0)
    momentum_weight = Column(Float, default=0.4)  # Weight for momentum strategy
    market_cap_weight = Column(Float, default=0.3)  # Weight for market cap strategy  
    risk_parity_weight = Column(Float, default=0.3)  # Weight for risk parity strategy
    
    # Risk parameters
    daily_drop_threshold = Column(Float, default=-0.01)  # -1% default
    max_daily_return = Column(Float, default=0.5)  # 50% cap
    min_daily_return = Column(Float, default=-0.5)  # -50% floor
    min_price_threshold = Column(Float, default=1.0)  # $1 minimum
    
    # Rebalancing parameters
    rebalance_frequency = Column(String, default="weekly")  # daily, weekly, monthly
    last_rebalance = Column(DateTime)
    force_rebalance = Column(Boolean, default=False)  # AI can trigger
    
    # Data quality parameters
    max_forward_fill_days = Column(Integer, default=2)
    outlier_std_threshold = Column(Float, default=3.0)  # Standard deviations for outlier detection
    
    # AI adjustment metadata
    ai_adjusted = Column(Boolean, default=False)
    ai_adjustment_reason = Column(String)
    ai_confidence_score = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Store historical adjustments
    adjustment_history = Column(JSON, default=list)


class RiskMetrics(Base):
    """Stores calculated risk metrics for the index."""
    __tablename__ = "risk_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    
    # Performance metrics
    total_return = Column(Float)  # Total return from inception
    annualized_return = Column(Float)  # Annualized return
    daily_return = Column(Float)  # Daily return
    
    # Risk metrics
    volatility = Column(Float)  # Annualized volatility
    sharpe_ratio = Column(Float)  # Risk-adjusted return (using risk-free rate)
    sortino_ratio = Column(Float)  # Downside risk-adjusted return
    max_drawdown = Column(Float)  # Maximum peak-to-trough decline
    current_drawdown = Column(Float)  # Current drawdown from peak
    
    # AI-calculated metrics
    ai_risk_score = Column(Float)  # AI-calculated risk score (0-100)
    ai_risk_adjusted_roi = Column(Float)  # AI-adjusted ROI considering market conditions
    ai_market_regime = Column(String)  # Bull, Bear, Sideways, Volatile
    
    # Value at Risk
    var_95 = Column(Float)  # 95% Value at Risk
    var_99 = Column(Float)  # 99% Value at Risk
    
    # Beta and correlation
    beta_sp500 = Column(Float)  # Beta relative to S&P 500
    correlation_sp500 = Column(Float)  # Correlation with S&P 500
    
    # Tracking metrics
    tracking_error = Column(Float)  # Standard deviation of excess returns
    information_ratio = Column(Float)  # Excess return per unit of tracking error
    
    created_at = Column(DateTime, server_default=func.now())


class MarketCapData(Base):
    """Stores market capitalization data for assets."""
    __tablename__ = "market_cap_data"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True)
    date = Column(DateTime, index=True)
    market_cap = Column(Float)  # In USD
    shares_outstanding = Column(Float)
    
    # Additional metrics for weighting
    free_float = Column(Float)  # Percentage of shares available for trading
    average_volume = Column(Float)  # 30-day average volume
    
    created_at = Column(DateTime, server_default=func.now())
