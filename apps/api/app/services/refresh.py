from sqlalchemy.orm import Session
from datetime import date, timedelta
import pandas as pd
from ..models import Asset, Price, IndexValue, Allocation
from ..core.config import settings
from .yahoo import fetch_prices
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

def refresh_all(db: Session):
    ensure_assets(db)

    # Load asset list
    assets = db.query(Asset).all()
    symbols = [a.symbol for a in assets]

    # Fetch prices since start
    start = pd.to_datetime(settings.ASSET_DEFAULT_START).date()
    price_df = fetch_prices(symbols, start=start)

    # Store prices
    # Clear existing prices for simplicity (MVP)
    db.query(Price).delete()
    db.commit()

    for sym in price_df.columns.levels[0]:
        asset = db.query(Asset).filter(Asset.symbol == sym).first()
        if not asset:
            continue
        series = price_df[sym]["Close"].dropna()
        for idx, val in series.items():
            db.add(Price(asset_id=asset.id, date=idx.date(), close=float(val)))
    db.commit()

    # Compute index + allocations
    compute_index_and_allocations(db)
