#!/usr/bin/env python3
"""
Debug the TwelveDataProvider to find the empty DataFrame issue.
"""

import os
import sys
from datetime import date, timedelta
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables
os.environ["DATABASE_URL"] = "postgresql://waardhaven_db_5t62_user:tJGnwSw4vLwNVAN7JWzi3BhP6yniOnS4@dpg-d2dpibbe5dus7390qqcg-a.oregon-postgres.render.com/waardhaven_db_5t62"
os.environ["TWELVEDATA_API_KEY"] = "e9b09b7610734d2699dc083f4ef5336d"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["ADMIN_TOKEN"] = "test-admin-token"
os.environ["TWELVEDATA_RATE_LIMIT"] = "8"
os.environ["ENABLE_MARKET_DATA_CACHE"] = "false"  # Disable cache for debugging

def debug_provider():
    """Debug the provider step by step."""
    print("\n🔍 DEBUGGING TWELVEDATA PROVIDER")
    print("=" * 60)
    
    # Import after env vars are set
    from app.providers.market_data.twelvedata import TwelveDataProvider
    from twelvedata import TDClient
    import logging
    
    # Enable detailed logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()
    
    # Test raw client first
    print("\n1. Testing raw TDClient...")
    client = TDClient(apikey=os.environ["TWELVEDATA_API_KEY"])
    
    symbol = "AAPL"
    start = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
    end = date.today().strftime("%Y-%m-%d")
    
    ts = client.time_series(
        symbol=symbol,
        interval="1day",
        start_date=start,
        end_date=end,
        outputsize=10,
        order="asc"
    )
    
    df = ts.as_pandas()
    print(f"Raw DataFrame shape: {df.shape}")
    print(f"Raw DataFrame columns: {df.columns.tolist()}")
    print(f"First row:\n{df.iloc[0] if not df.empty else 'Empty'}")
    
    # Now test the provider
    print("\n2. Testing TwelveDataProvider...")
    provider = TwelveDataProvider()
    
    # Test the _process_price_data method directly
    print("\n3. Testing _process_price_data...")
    processed = provider._process_price_data(df.copy(), symbol)
    print(f"Processed DataFrame shape: {processed.shape}")
    print(f"Processed DataFrame columns: {processed.columns.tolist()}")
    
    # Test fetch_historical_prices
    print("\n4. Testing fetch_historical_prices...")
    symbols = ["AAPL"]
    start_date = date.today() - timedelta(days=7)
    
    result = provider.fetch_historical_prices(symbols, start_date=start_date)
    print(f"Result shape: {result.shape}")
    print(f"Result empty: {result.empty}")
    
    if not result.empty:
        print(f"Result columns: {result.columns}")
        if hasattr(result.columns, 'levels'):
            print(f"Column levels: {result.columns.levels}")
    
    # Test with multiple symbols
    print("\n5. Testing with multiple symbols...")
    symbols = ["AAPL", "MSFT"]
    result = provider.fetch_historical_prices(symbols, start_date=start_date)
    print(f"Multi-symbol result shape: {result.shape}")
    print(f"Multi-symbol result empty: {result.empty}")
    
    if not result.empty:
        print(f"Result columns: {result.columns}")
        if hasattr(result.columns, 'levels'):
            print(f"Column levels: {result.columns.levels}")

if __name__ == "__main__":
    debug_provider()