"""
Optimized refresh service with intelligent API usage.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
import pandas as pd
from ..models import Asset, Price, IndexValue, Allocation
from ..core.config import settings
from .twelvedata_optimized import (
    fetch_prices_optimized, 
    get_minimal_refresh_data,
    validate_api_key
)
from .strategy import compute_index_and_allocations
import logging

logger = logging.getLogger(__name__)

# Priority assets for limited API plans
PRIORITY_ASSETS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META",  # Top tech stocks
    "SPY", "QQQ",  # Major ETFs
    "GLD",  # Gold
]

def smart_refresh(db: Session, mode: str = "auto"):
    """
    Smart refresh with multiple strategies based on API limits.
    
    Modes:
    - "full": Fetch all data (may hit rate limits)
    - "minimal": Fetch only recent data for priority assets
    - "cached": Use cached data only
    - "auto": Automatically choose based on API plan
    """
    logger.info(f"Starting smart refresh in {mode} mode...")
    
    # Validate API key and check plan
    is_valid, plan_info = validate_api_key()
    
    if not is_valid:
        logger.warning("API key validation failed, using cached data only")
        mode = "cached"
    elif plan_info and plan_info.get('credits_limit', 8) <= 8:
        logger.info(f"Free tier detected (limit: {plan_info.get('credits_limit')} credits/min)")
        if mode == "auto":
            mode = "minimal"
    
    try:
        # Ensure assets exist
        from .refresh import ensure_assets
        ensure_assets(db)
        
        # Get assets based on mode
        if mode == "minimal":
            # Only fetch priority assets for free tier
            assets = db.query(Asset).filter(
                Asset.symbol.in_(PRIORITY_ASSETS)
            ).all()
            days_back = 30  # Fetch only last 30 days
        elif mode == "cached":
            # Don't fetch new data, just use what's cached
            assets = db.query(Asset).all()
            days_back = 0
        else:  # full
            assets = db.query(Asset).all()
            days_back = 365  # Fetch full year
        
        symbols = [a.symbol for a in assets]
        logger.info(f"Processing {len(symbols)} assets: {symbols}")
        
        # Fetch prices based on mode
        if mode != "cached":
            if mode == "minimal":
                # Use minimal refresh for free tier
                start_date = date.today() - timedelta(days=days_back)
                price_df = get_minimal_refresh_data(symbols, days_back)
            else:
                # Full refresh with optimization
                start_date = pd.to_datetime(settings.ASSET_DEFAULT_START).date()
                price_df = fetch_prices_optimized(symbols, start=start_date)
        else:
            # Load from cache only
            logger.info("Using cached data only mode")
            price_df = load_all_cached_data(symbols)
        
        if price_df.empty:
            logger.error("No price data available!")
            raise ValueError("Unable to fetch or load any price data")
        
        # Store prices in database
        logger.info("Storing prices in database...")
        store_prices_efficiently(db, price_df, assets)
        
        # Compute index and allocations
        logger.info("Computing index and allocations...")
        compute_index_and_allocations(db)
        
        # Log success metrics
        index_count = db.query(func.count()).select_from(IndexValue).scalar()
        price_count = db.query(func.count()).select_from(Price).scalar()
        logger.info(f"Refresh completed. Index values: {index_count}, Prices: {price_count}")
        
        return {
            "success": True,
            "mode": mode,
            "assets_processed": len(symbols),
            "index_values": index_count,
            "prices": price_count
        }
        
    except Exception as e:
        logger.error(f"Smart refresh failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Try fallback to cached data
        if mode != "cached":
            logger.info("Attempting fallback to cached data...")
            return smart_refresh(db, mode="cached")
        
        raise

def store_prices_efficiently(db: Session, price_df: pd.DataFrame, assets: list):
    """
    Store prices efficiently with batch operations.
    """
    # Get existing price dates to avoid duplicates
    existing_dates = set()
    for asset in assets:
        dates = db.query(Price.date).filter(Price.asset_id == asset.id).all()
        existing_dates.update((asset.id, d[0]) for d in dates)
    
    # Prepare batch insert
    new_prices = []
    
    for sym in price_df.columns.levels[0] if hasattr(price_df.columns, 'levels') else []:
        asset = next((a for a in assets if a.symbol == sym), None)
        if not asset:
            continue
            
        if sym in price_df.columns:
            series = price_df[sym]["Close"].dropna()
            for idx, val in series.items():
                price_date = idx.date() if hasattr(idx, 'date') else idx
                
                # Skip if already exists
                if (asset.id, price_date) not in existing_dates:
                    new_prices.append(Price(
                        asset_id=asset.id,
                        date=price_date,
                        close=float(val)
                    ))
    
    # Batch insert
    if new_prices:
        db.bulk_save_objects(new_prices)
        db.commit()
        logger.info(f"Inserted {len(new_prices)} new price records")
    else:
        logger.info("No new prices to insert")

def load_all_cached_data(symbols: list) -> pd.DataFrame:
    """
    Load all available cached data for symbols.
    """
    from .twelvedata_optimized import load_from_cache
    
    all_data = {}
    # Try multiple date ranges to find cached data
    date_ranges = [
        date.today() - timedelta(days=7),
        date.today() - timedelta(days=30),
        date.today() - timedelta(days=90),
        date.today() - timedelta(days=365),
    ]
    
    for symbol in symbols:
        for start_date in date_ranges:
            df = load_from_cache(symbol, start_date)
            if df is not None:
                all_data[symbol] = df
                break
    
    if not all_data:
        return pd.DataFrame()
    
    return pd.concat(all_data, axis=1)

def get_refresh_strategy(db: Session) -> str:
    """
    Determine the best refresh strategy based on current state.
    """
    # Check last refresh time
    latest_price = db.query(func.max(Price.date)).scalar()
    
    if not latest_price:
        return "minimal"  # First run, use minimal
    
    days_old = (date.today() - latest_price).days
    
    if days_old == 0:
        return "cached"  # Already updated today
    elif days_old <= 1:
        return "minimal"  # Recent, just get latest
    else:
        return "auto"  # Let system decide based on API plan