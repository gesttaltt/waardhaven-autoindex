from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
import pandas as pd
from ..models import Asset, Price, IndexValue, Allocation
from ..core.config import settings

def compute_index_and_allocations(db: Session):
    # Load prices into DataFrame
    prices = db.query(Price).all()
    if not prices:
        return

    # Map asset_id -> symbol
    assets = {a.id: a for a in db.query(Asset).all()}

    # Create DataFrame: rows=date, columns=symbol, values=close
    records = [(p.date, assets[p.asset_id].symbol, p.close) for p in prices if assets[p.asset_id].symbol != "^GSPC"]
    df = pd.DataFrame(records, columns=["date", "symbol", "close"])
    pivot = df.pivot_table(index="date", columns="symbol", values="close").sort_index()

    # Compute daily returns
    rets = pivot.pct_change().fillna(0.0)

    threshold = settings.DAILY_DROP_THRESHOLD

    # Initialize index value
    index_values = []
    allocations = []

    value = 1.0  # Start at 1.0 for compounding
    for dt, row in rets.iterrows():
        # Filter assets where daily return >= threshold
        included = row[row >= threshold].index.tolist()
        if len(included) == 0:
            included = row.index.tolist()  # fallback: include all

        w = 1.0 / len(included)
        # portfolio daily return = average of included returns
        port_ret = row[included].mean()
        value *= (1.0 + float(port_ret))
        index_values.append((dt, float(value)))

        # Save allocations for this day
        for sym in included:
            asset = next((a for a in assets.values() if a.symbol == sym), None)
            if asset:
                allocations.append((dt, asset.id, w))

    # Normalize index values to base 100 (consistent with individual assets and benchmarks)
    if index_values:
        first_value = index_values[0][1]  # First calculated value
        normalized_index_values = [(dt, (val / first_value) * 100.0) for dt, val in index_values]
    else:
        normalized_index_values = []

    # Clear and store
    db.query(IndexValue).delete()
    db.query(Allocation).delete()
    db.commit()

    for dt, val in normalized_index_values:
        db.add(IndexValue(date=dt, value=val))
    for dt, aid, w in allocations:
        db.add(Allocation(date=dt, asset_id=aid, weight=w))
    db.commit()
