#!/usr/bin/env python3
"""
Test script for TwelveData integration.
Run this to verify TwelveData API is working correctly.
"""

import os
import sys
from datetime import date, timedelta
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_api_key():
    """Test if API key is configured."""
    api_key = os.getenv('TWELVEDATA_API_KEY')
    if not api_key or api_key == 'your_twelvedata_api_key_here':
        print("❌ TWELVEDATA_API_KEY not configured in .env file")
        print("   Please get an API key from https://twelvedata.com/account/api-keys")
        return False
    print(f"✅ API key configured: {api_key[:8]}...")
    return True

def test_basic_connection():
    """Test basic TwelveData connection."""
    try:
        from twelvedata import TDClient
        api_key = os.getenv('TWELVEDATA_API_KEY')
        
        client = TDClient(apikey=api_key)
        
        # Test with a simple quote request
        quote = client.quote(symbol="AAPL").as_json()
        
        if quote and 'symbol' in quote:
            print("✅ Basic connection successful")
            print(f"   AAPL current price: ${quote.get('close', 'N/A')}")
            return True
        else:
            print("❌ Failed to get quote data")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_fetch_prices():
    """Test the fetch_prices function."""
    try:
        from app.services.twelvedata import fetch_prices
        
        symbols = ["AAPL", "MSFT", "GOOGL"]
        start = date.today() - timedelta(days=7)
        
        print(f"\nTesting fetch_prices for {symbols}...")
        df = fetch_prices(symbols, start)
        
        if df.empty:
            print("❌ No data returned from fetch_prices")
            return False
            
        print(f"✅ Fetched {len(df)} rows of data")
        print(f"   Date range: {df.index.min()} to {df.index.max()}")
        print(f"   Symbols: {list(df.columns.levels[0])}")
        
        # Check data structure
        for symbol in symbols:
            if symbol in df.columns.levels[0]:
                close_prices = df[symbol]['Close'].dropna()
                print(f"   {symbol}: {len(close_prices)} price points")
        
        return True
        
    except Exception as e:
        print(f"❌ fetch_prices failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_exchange_rates():
    """Test currency exchange rate fetching."""
    try:
        from app.services.twelvedata import get_exchange_rate
        
        print("\nTesting exchange rates...")
        
        # Test some common currency pairs
        pairs = [
            ("EUR", "USD"),
            ("USD", "EUR"),
            ("GBP", "USD"),
            ("USD", "JPY")
        ]
        
        success = True
        for from_curr, to_curr in pairs:
            rate = get_exchange_rate(from_curr, to_curr)
            if rate:
                print(f"✅ {from_curr}/{to_curr}: {rate:.4f}")
            else:
                print(f"❌ Failed to get {from_curr}/{to_curr} rate")
                success = False
        
        return success
        
    except Exception as e:
        print(f"❌ Exchange rate test failed: {e}")
        return False

def test_symbol_validation():
    """Test symbol validation."""
    try:
        from app.services.twelvedata import validate_symbols
        
        print("\nTesting symbol validation...")
        
        symbols = ["AAPL", "MSFT", "INVALID_SYMBOL_XYZ", "^GSPC", "GLD"]
        results = validate_symbols(symbols)
        
        for symbol, is_valid in results.items():
            status = "✅" if is_valid else "❌"
            print(f"   {status} {symbol}: {'available' if is_valid else 'not found'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Symbol validation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("TwelveData Integration Test Suite")
    print("=" * 60)
    
    # Check environment setup
    if not test_api_key():
        print("\n⚠️  Please configure your API key first!")
        return
    
    # Run tests
    tests = [
        ("Basic Connection", test_basic_connection),
        ("Fetch Prices", test_fetch_prices),
        ("Exchange Rates", test_exchange_rates),
        ("Symbol Validation", test_symbol_validation)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! TwelveData integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()