#!/usr/bin/env python3
"""
Direct test of TwelveData API to diagnose refresh issues.
"""

import os
import sys
from datetime import date, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables before importing anything
os.environ["DATABASE_URL"] = "postgresql://waardhaven_db_5t62_user:tJGnwSw4vLwNVAN7JWzi3BhP6yniOnS4@dpg-d2dpibbe5dus7390qqcg-a.oregon-postgres.render.com/waardhaven_db_5t62"
os.environ["TWELVEDATA_API_KEY"] = "e9b09b7610734d2699dc083f4ef5336d"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["ADMIN_TOKEN"] = "test-admin-token"

def test_twelvedata_api():
    """Test TwelveData API directly."""
    print("\n🔬 TWELVEDATA API DIRECT TEST")
    print("=" * 60)
    
    # Step 1: Test raw TwelveData client
    print("\n1️⃣ Testing Raw TwelveData Client")
    print("-" * 40)
    
    try:
        from twelvedata import TDClient
        
        api_key = os.environ.get("TWELVEDATA_API_KEY")
        print(f"API Key: {api_key[:10]}... (length: {len(api_key)})")
        
        client = TDClient(apikey=api_key)
        print("✅ TwelveData client created")
        
        # Test API key validity
        print("\nTesting API key validity with a simple request...")
        test_symbol = "AAPL"
        
        try:
            # Get quote for a single symbol
            quote = client.quote(symbol=test_symbol)
            quote_data = quote.as_json()
            
            if "code" in quote_data and quote_data["code"] == 401:
                print(f"❌ API Key invalid: {quote_data.get('message', 'Unknown error')}")
                return False
            elif "symbol" in quote_data:
                print(f"✅ API Key valid! Got quote for {test_symbol}")
                print(f"   Price: ${quote_data.get('close', 'N/A')}")
            else:
                print(f"⚠️ Unexpected response: {quote_data}")
                
        except Exception as e:
            print(f"❌ Quote request failed: {e}")
            
        # Test time series fetch
        print("\nTesting time series fetch...")
        start_date = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = date.today().strftime("%Y-%m-%d")
        
        try:
            ts = client.time_series(
                symbol=test_symbol,
                interval="1day",
                start_date=start_date,
                end_date=end_date,
                outputsize=10
            )
            
            df = ts.as_pandas()
            
            if df is not None and not df.empty:
                print(f"✅ Time series fetched: {len(df)} records")
                print(f"   Date range: {df.index[0]} to {df.index[-1]}")
                print(f"   Latest close: ${df['close'].iloc[-1]:.2f}")
            else:
                print("❌ No data returned for time series")
                
        except Exception as e:
            print(f"❌ Time series fetch failed: {e}")
            
    except ImportError as e:
        print(f"❌ Failed to import TwelveData: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    # Step 2: Test Provider Implementation
    print("\n2️⃣ Testing Provider Implementation")
    print("-" * 40)
    
    try:
        from app.providers.market_data import TwelveDataProvider
        from app.core.config import settings
        
        print(f"Settings loaded:")
        print(f"   API Key configured: {'Yes' if settings.TWELVEDATA_API_KEY else 'No'}")
        print(f"   Rate limit: {settings.TWELVEDATA_RATE_LIMIT} credits/min")
        print(f"   Cache enabled: {settings.ENABLE_MARKET_DATA_CACHE}")
        
        provider = TwelveDataProvider()
        print("✅ Provider initialized")
        
        # Test fetching multiple symbols
        symbols = ["AAPL", "MSFT", "GOOGL"]
        start = date.today() - timedelta(days=7)
        
        print(f"\nFetching prices for {symbols} from {start}...")
        
        try:
            df = provider.fetch_historical_prices(symbols, start_date=start)
            
            if not df.empty:
                print(f"✅ Fetched {len(df)} dates")
                print(f"   Columns: {list(df.columns.levels[0]) if hasattr(df.columns, 'levels') else df.columns.tolist()}")
                print(f"   Latest date: {df.index[-1]}")
                
                # Check for each symbol
                for symbol in symbols:
                    if hasattr(df.columns, 'levels'):
                        if symbol in df.columns.levels[0]:
                            closes = df[symbol]["close"].dropna()
                            print(f"   {symbol}: {len(closes)} prices, latest=${closes.iloc[-1]:.2f}")
                    else:
                        print(f"   Single symbol mode")
            else:
                print("❌ Empty DataFrame returned")
                
        except Exception as e:
            print(f"❌ Provider fetch failed: {e}")
            import traceback
            traceback.print_exc()
            
    except ImportError as e:
        print(f"❌ Failed to import provider: {e}")
    except Exception as e:
        print(f"❌ Provider test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 3: Test Database Storage
    print("\n3️⃣ Testing Database Storage")
    print("-" * 40)
    
    try:
        from app.core.database import get_db, engine
        from app.models.asset import Asset, Price
        from sqlalchemy import func
        
        # Create a session
        db = next(get_db())
        
        # Check current data
        price_count = db.query(func.count()).select_from(Price).scalar()
        print(f"Current prices in DB: {price_count}")
        
        latest_price = db.query(func.max(Price.date)).scalar()
        print(f"Latest price date: {latest_price}")
        
        if latest_price:
            days_old = (date.today() - latest_price).days
            print(f"Data age: {days_old} days old")
            
            if days_old > 3:
                print("⚠️ Data is stale, refresh needed")
            else:
                print("✅ Data is relatively fresh")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
    
    print("\n" + "="*60)
    print("Diagnostic complete!")
    
    return True

if __name__ == "__main__":
    test_twelvedata_api()