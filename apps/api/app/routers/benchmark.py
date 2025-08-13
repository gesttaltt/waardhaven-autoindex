from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..core.database import get_db
from ..models import IndexValue, Price, Asset, User
from ..schemas import BenchmarkResponse, SeriesPoint
from ..utils.token_dep import get_current_user

router = APIRouter()

@router.get("/sp500", response_model=BenchmarkResponse)
def sp500(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # S&P 500 is stored as an asset with symbol '^GSPC' in prices table for history
    sp500_asset = db.query(Asset).filter(Asset.symbol == "^GSPC").first()
    if not sp500_asset:
        raise HTTPException(status_code=404, detail="Benchmark asset not found. Run tasks/refresh.")
    rows = db.query(Price).filter(Price.asset_id == sp500_asset.id).order_by(Price.date.asc()).all()
    if not rows:
        raise HTTPException(status_code=404, detail="No benchmark prices. Run tasks/refresh.")
    # Normalize to base 100
    base = rows[0].close
    series = [SeriesPoint(date=r.date, value= (r.close / base) * 100.0) for r in rows]
    return BenchmarkResponse(series=series)
