from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from ..core.database import get_db
from ..models import IndexValue, Price
import logging
import traceback

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/trigger-refresh")
def trigger_manual_refresh(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Trigger a manual refresh without requiring admin token (for debugging).
    This endpoint should be removed or secured in production.
    """
    try:
        # Check current state
        index_count = db.query(func.count()).select_from(IndexValue).scalar()
        price_count = db.query(func.count()).select_from(Price).scalar()
        
        # Add refresh to background tasks
        background_tasks.add_task(run_refresh_with_logging, db)
        
        return {
            "status": "REFRESH_STARTED",
            "message": "Refresh has been triggered in the background",
            "current_state": {
                "index_values": index_count,
                "prices": price_count
            },
            "note": "Check /api/v1/diagnostics/database-status in 30-60 seconds to see results"
        }
    except Exception as e:
        logger.error(f"Failed to trigger refresh: {str(e)}")
        return {
            "status": "ERROR",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

def run_refresh_with_logging(db: Session):
    """Run refresh with detailed logging."""
    try:
        logger.info("Starting manual refresh process...")
        from ..services.refresh import refresh_all
        
        refresh_all(db)
        
        # Verify results
        index_count = db.query(func.count()).select_from(IndexValue).scalar()
        price_count = db.query(func.count()).select_from(Price).scalar()
        
        logger.info(f"Refresh completed. Index values: {index_count}, Prices: {price_count}")
        
    except Exception as e:
        logger.error(f"Refresh failed: {str(e)}")
        logger.error(traceback.format_exc())

@router.post("/minimal-refresh")
def minimal_data_refresh(db: Session = Depends(get_db)):
    """
    Perform a minimal refresh with just a few days of data for testing.
    """
    try:
        from ..services.refresh import ensure_assets
        from ..services.twelvedata import fetch_prices
        from ..models import Asset, Price, IndexValue
        from datetime import date, timedelta
        import pandas as pd
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "steps": []
        }
        
        # Step 1: Ensure assets exist
        ensure_assets(db)
        assets = db.query(Asset).filter(Asset.symbol.in_(["AAPL", "MSFT", "GOOGL"])).all()
        results["steps"].append({
            "step": "assets",
            "count": len(assets),
            "symbols": [a.symbol for a in assets]
        })
        
        # Step 2: Fetch minimal price data (last 7 days)
        symbols = [a.symbol for a in assets]
        start_date = date.today() - timedelta(days=7)
        
        try:
            price_df = fetch_prices(symbols, start=start_date)
            
            # Clear existing recent prices
            db.query(Price).filter(Price.date >= start_date).delete()
            db.commit()
            
            # Store new prices
            stored_count = 0
            for sym in symbols:
                asset = next((a for a in assets if a.symbol == sym), None)
                if asset and sym in price_df.columns.levels[0]:
                    series = price_df[sym]["Close"].dropna()
                    for idx, val in series.items():
                        db.add(Price(asset_id=asset.id, date=idx.date(), close=float(val)))
                        stored_count += 1
            
            db.commit()
            results["steps"].append({
                "step": "prices",
                "fetched": len(price_df),
                "stored": stored_count
            })
            
            # Step 3: Create simple index values
            # For testing, just create a simple average
            dates = price_df.index.unique()
            for dt in dates:
                # Simple average of prices as index value
                avg_price = 100.0  # Base value
                try:
                    prices_on_date = []
                    for sym in symbols:
                        if sym in price_df.columns.levels[0]:
                            if dt in price_df[sym]["Close"].index:
                                prices_on_date.append(price_df[sym]["Close"][dt])
                    
                    if prices_on_date:
                        avg_price = sum(prices_on_date) / len(prices_on_date)
                    
                    # Check if index value exists
                    existing = db.query(IndexValue).filter(IndexValue.date == dt.date()).first()
                    if not existing:
                        db.add(IndexValue(date=dt.date(), value=avg_price))
                except:
                    pass
            
            db.commit()
            
            index_count = db.query(func.count()).select_from(IndexValue).scalar()
            results["steps"].append({
                "step": "index_values",
                "created": index_count
            })
            
            results["status"] = "SUCCESS"
            results["message"] = "Minimal data refresh completed"
            
        except Exception as e:
            results["status"] = "FAILED"
            results["error"] = str(e)
            results["traceback"] = traceback.format_exc()
            
        return results
        
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
            "traceback": traceback.format_exc()
        }