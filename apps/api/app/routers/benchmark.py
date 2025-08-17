from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..core.database import get_db
from ..models.index import IndexValue
from ..models.asset import Asset, Price
from ..models.user import User
from ..schemas.benchmark import BenchmarkResponse
from ..schemas.index import SeriesPoint
from ..utils.token_dep import get_current_user

router = APIRouter()

@router.get("/sp500", response_model=BenchmarkResponse)
def sp500(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # S&P 500 is stored as an asset with symbol '^GSPC' in prices table for history
    # Try multiple possible S&P 500 symbols (different data providers use different symbols)
    sp500_symbols = ["^GSPC", "SPY", "SPX", ".SPX", "^SPX"]
    
    sp500_asset = None
    for symbol in sp500_symbols:
        sp500_asset = db.query(Asset).filter(Asset.symbol == symbol).first()
        if sp500_asset:
            break
    
    if not sp500_asset:
        # Return empty series instead of raising error to prevent frontend crashes
        import logging
        logging.getLogger(__name__).warning("S&P 500 benchmark asset not found. Returning empty series.")
        return BenchmarkResponse(series=[])
    
    rows = db.query(Price).filter(Price.asset_id == sp500_asset.id).order_by(Price.date.asc()).all()
    if not rows:
        # Return empty series instead of raising error
        import logging
        logging.getLogger(__name__).warning(f"No price data for S&P 500 ({sp500_asset.symbol}). Returning empty series.")
        return BenchmarkResponse(series=[])
    
    # Normalize to base 100
    base = rows[0].close
    series = [SeriesPoint(date=r.date, value=(r.close / base) * 100.0) for r in rows]
    return BenchmarkResponse(series=series)
