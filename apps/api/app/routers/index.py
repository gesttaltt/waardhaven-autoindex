from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from ..core.database import get_db
from ..models import Asset, Price, Allocation, IndexValue
from ..schemas import IndexCurrentResponse, AllocationItem, IndexHistoryResponse, SeriesPoint, SimulationRequest, SimulationResponse

router = APIRouter()

@router.get("/current", response_model=IndexCurrentResponse)
def get_current_index(db: Session = Depends(get_db)):
    # Latest allocation date
    latest_date = db.query(func.max(Allocation.date)).scalar()
    if latest_date is None:
        raise HTTPException(status_code=404, detail="No allocations computed yet. Run tasks/refresh.")
    allocations = db.query(Allocation, Asset).join(Asset, Allocation.asset_id == Asset.id).filter(Allocation.date == latest_date).all()
    items = []
    for alloc, asset in allocations:
        items.append(AllocationItem(symbol=asset.symbol, name=asset.name, sector=asset.sector, weight=alloc.weight))
    return IndexCurrentResponse(date=latest_date, allocations=items)

@router.get("/history", response_model=IndexHistoryResponse)
def get_history(db: Session = Depends(get_db)):
    rows = db.query(IndexValue).order_by(IndexValue.date.asc()).all()
    if not rows:
        raise HTTPException(status_code=404, detail="No index history. Run tasks/refresh.")
    return IndexHistoryResponse(series=[SeriesPoint(date=r.date, value=r.value) for r in rows])

@router.post("/simulate", response_model=SimulationResponse)
def simulate(req: SimulationRequest, db: Session = Depends(get_db)):
    # Get index series
    q = db.query(IndexValue).order_by(IndexValue.date.asc())
    series = q.all()
    if not series:
        raise HTTPException(status_code=404, detail="No index history. Run tasks/refresh.")

    # Find start and end
    start = next((r for r in series if r.date >= req.start_date), None)
    if start is None:
        raise HTTPException(status_code=400, detail="Start date out of range")
    end = series[-1]

    amount_final = req.amount * (end.value / start.value)
    roi_pct = (amount_final / req.amount - 1.0) * 100.0

    resp_series = [SeriesPoint(date=r.date, value=r.value) for r in series if r.date >= req.start_date]
    return SimulationResponse(
        start_date=start.date,
        end_date=end.date,
        start_value=start.value,
        end_value=end.value,
        amount_initial=req.amount,
        amount_final=amount_final,
        roi_pct=roi_pct,
        series=resp_series
    )
