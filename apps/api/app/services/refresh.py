from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
import pandas as pd
from ..models import Asset, Price, IndexValue, Allocation
from ..core.config import settings
try:
    from .twelvedata_optimized import fetch_prices_optimized as fetch_prices
    use_optimized = True
except ImportError:
    from .twelvedata import fetch_prices
    use_optimized = False
from .strategy import compute_index_and_allocations
from ..models import StrategyConfig

DEFAULT_ASSETS = [
    # Stocks
    ("AAPL", "Apple Inc.", "Technology"),
    ("MSFT", "Microsoft Corp.", "Technology"),
    ("GOOGL", "Alphabet Inc.", "Technology"),
    ("AMZN", "Amazon.com Inc.", "Consumer Discretionary"),
    ("META", "Meta Platforms Inc.", "Communication Services"),
    ("TSLA", "Tesla Inc.", "Consumer Discretionary"),
    ("NVDA", "NVIDIA Corp.", "Technology"),
    # Commodities via ETFs
    ("GLD", "SPDR Gold Shares", "Commodity"),
    ("SLV", "iShares Silver Trust", "Commodity"),
    ("USO", "United States Oil Fund", "Commodity"),
    # Bonds via ETFs
    ("TLT", "iShares 20+ Year Treasury Bond ETF", "Bond"),
    ("IEF", "iShares 7-10 Year Treasury Bond ETF", "Bond"),
]

def ensure_assets(db: Session):
    for sym, name, sector in DEFAULT_ASSETS + [(settings.SP500_TICKER, "S&P 500", "Benchmark")]:
        exists = db.query(Asset).filter(Asset.symbol == sym).first()
        if not exists:
            db.add(Asset(symbol=sym, name=name, sector=sector))
    db.commit()

def refresh_all(db: Session, smart_mode: bool = True):
    import logging
    logger = logging.getLogger(__name__)
    
    # Use smart refresh if optimized module is available and enabled
    if smart_mode and use_optimized:
        try:
            from .refresh_optimized import smart_refresh
            logger.info("Using smart refresh with rate limit protection...")
            return smart_refresh(db, mode=settings.REFRESH_MODE)
        except ImportError:
            logger.warning("Smart refresh not available, falling back to standard refresh")
    
    try:
        logger.info("Starting standard refresh process...")
        
        # Step 1: Ensure assets exist
        logger.info("Ensuring assets...")
        ensure_assets(db)
        
        # Load asset list
        assets = db.query(Asset).all()
        symbols = [a.symbol for a in assets]
        logger.info(f"Found {len(symbols)} assets to refresh: {symbols}")
        
        # Step 2: Fetch prices
        logger.info("Fetching price data from TwelveData...")
        start = pd.to_datetime(settings.ASSET_DEFAULT_START).date()
        
        try:
            price_df = fetch_prices(symbols, start=start)
            logger.info(f"Fetched {len(price_df)} price records")
        except Exception as e:
            logger.error(f"Failed to fetch prices: {e}")
            # Try fetching with a shorter period as fallback
            from datetime import timedelta
            fallback_start = date.today() - timedelta(days=90)
            logger.info(f"Trying fallback period from {fallback_start}")
            price_df = fetch_prices(symbols, start=fallback_start)
        
        if price_df.empty:
            logger.error("No price data fetched!")
            raise ValueError("Unable to fetch any price data")
        
        # Step 3: Store prices
        logger.info("Storing prices in database...")
        # Clear existing prices for simplicity (MVP)
        db.query(Price).delete()
        db.commit()
        
        price_count = 0
        skipped_count = 0
        
        for sym in price_df.columns.levels[0]:
            asset = db.query(Asset).filter(Asset.symbol == sym).first()
            if not asset:
                logger.warning(f"Asset {sym} not found in database")
                continue
            
            # Get the Close price series for this symbol
            try:
                series = price_df[sym]["Close"]
                
                # Log data quality info
                null_count = series.isnull().sum()
                if null_count > 0:
                    logger.warning(f"{sym}: {null_count} null values in {len(series)} total prices")
                
                # Only store non-null prices above minimum threshold
                min_price = 1.0  # Match our strategy's min_price_threshold
                for idx, val in series.items():
                    if pd.notna(val) and float(val) >= min_price:
                        db.add(Price(asset_id=asset.id, date=idx.date(), close=float(val)))
                        price_count += 1
                    elif pd.notna(val):
                        skipped_count += 1
                        logger.debug(f"Skipped {sym} price on {idx.date()}: ${val:.4f} below threshold")
                        
            except KeyError as e:
                logger.error(f"Missing 'Close' data for {sym}: {e}")
                continue
        
        db.commit()
        logger.info(f"Stored {price_count} price records, skipped {skipped_count} below threshold")
        
        # Step 4: Compute index + allocations with strategy config
        logger.info("Computing index and allocations...")
        
        # Get strategy configuration from database
        strategy_config = db.query(StrategyConfig).first()
        if strategy_config:
            config = {
                'momentum_weight': strategy_config.momentum_weight,
                'market_cap_weight': strategy_config.market_cap_weight,
                'risk_parity_weight': strategy_config.risk_parity_weight,
                'min_price': strategy_config.min_price_threshold,
                'max_daily_return': strategy_config.max_daily_return,
                'min_daily_return': strategy_config.min_daily_return,
                'max_forward_fill_days': strategy_config.max_forward_fill_days,
                'outlier_std_threshold': strategy_config.outlier_std_threshold,
                'rebalance_frequency': strategy_config.rebalance_frequency,
                'daily_drop_threshold': strategy_config.daily_drop_threshold
            }
            compute_index_and_allocations(db, config)
        else:
            compute_index_and_allocations(db)
        
        # Verify results
        index_count = db.query(func.count()).select_from(IndexValue).scalar()
        logger.info(f"Refresh completed successfully. Index values: {index_count}")
        
    except Exception as e:
        logger.error(f"Refresh failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise
