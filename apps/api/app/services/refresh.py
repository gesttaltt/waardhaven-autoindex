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
        for sym in price_df.columns.levels[0]:
            asset = db.query(Asset).filter(Asset.symbol == sym).first()
            if not asset:
                logger.warning(f"Asset {sym} not found in database")
                continue
            series = price_df[sym]["Close"].dropna()
            for idx, val in series.items():
                db.add(Price(asset_id=asset.id, date=idx.date(), close=float(val)))
                price_count += 1
        
        db.commit()
        logger.info(f"Stored {price_count} price records")
        
        # Step 4: Compute index + allocations
        logger.info("Computing index and allocations...")
        compute_index_and_allocations(db)
        
        # Verify results
        index_count = db.query(func.count()).select_from(IndexValue).scalar()
        logger.info(f"Refresh completed successfully. Index values: {index_count}")
        
    except Exception as e:
        logger.error(f"Refresh failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise
