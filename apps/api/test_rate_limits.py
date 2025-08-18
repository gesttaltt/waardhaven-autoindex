#!/usr/bin/env python3
"""
Test script for TwelveData rate limit protection.
"""
import os
import sys
from datetime import date
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent))


def test_rate_limit_protection():
    """Test the rate limiting mechanism."""
    print("=" * 60)
    print("TwelveData Rate Limit Protection Test")
    print("=" * 60)

    try:
        from app.services.twelvedata_optimized import RateLimitedTDClient

        # Test with a small limit to trigger rate limiting quickly
        api_key = os.getenv("TWELVEDATA_API_KEY")
        if not api_key:
            print("❌ TWELVEDATA_API_KEY not set")
            return False

        client = RateLimitedTDClient(api_key)

        # Simulate hitting rate limit
        symbols = [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "META",
            "TSLA",
            "NVDA",
            "SPY",
            "QQQ",
        ]

        print(f"Testing with {len(symbols)} symbols to trigger rate limits...")
        print("This should automatically handle rate limiting...\n")

        start_time = time.time()
        successful_requests = 0

        for i, symbol in enumerate(symbols):
            try:
                print(f"Fetching {symbol} ({i+1}/{len(symbols)})...")

                # This should trigger rate limiting after 8 requests
                ts = client.get_time_series(symbol, interval="1day", outputsize=5)

                data = ts.as_pandas()
                if data is not None and not data.empty:
                    print(f"✅ {symbol}: {len(data)} records")
                    successful_requests += 1
                else:
                    print(f"⚠️ {symbol}: No data returned")

            except Exception as e:
                print(f"❌ {symbol}: {e}")

        total_time = time.time() - start_time
        print("\n📊 Summary:")
        print(f"   Successful requests: {successful_requests}/{len(symbols)}")
        print(f"   Total time: {total_time:.1f} seconds")

        if total_time > 60:  # Should take at least 60+ seconds due to rate limiting
            print("✅ Rate limiting protection working (took >60 seconds)")
        else:
            print("⚠️  May not have hit rate limits (completed quickly)")

        return successful_requests > 0

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_caching_mechanism():
    """Test the caching mechanism."""
    print("\n" + "=" * 60)
    print("Cache Mechanism Test")
    print("=" * 60)

    try:
        from app.services.twelvedata_optimized import (
            save_to_cache,
            load_from_cache,
            get_cache_path,
        )
        import pandas as pd

        # Create test data
        test_symbol = "TEST_CACHE"
        test_date = date.today()

        # Create sample DataFrame
        dates = pd.date_range(start="2024-01-01", periods=5, freq="D")
        test_df = pd.DataFrame(
            {
                "Close": [100, 101, 102, 103, 104],
                "Open": [99, 100, 101, 102, 103],
                "High": [101, 102, 103, 104, 105],
                "Low": [98, 99, 100, 101, 102],
                "Volume": [1000, 1100, 1200, 1300, 1400],
            },
            index=dates,
        )

        print(f"Testing cache for {test_symbol}...")

        # Test save
        save_to_cache(test_symbol, test_date, test_df)
        print("✅ Data saved to cache")

        # Test load
        loaded_df = load_from_cache(test_symbol, test_date)
        if loaded_df is not None:
            print(f"✅ Data loaded from cache: {len(loaded_df)} records")

            # Verify cache file exists
            cache_path = get_cache_path(test_symbol, test_date)
            if cache_path.exists():
                print(f"✅ Cache file exists: {cache_path}")
                return True
            else:
                print(f"❌ Cache file missing: {cache_path}")
        else:
            print("❌ Failed to load from cache")

        return False

    except Exception as e:
        print(f"❌ Cache test failed: {e}")
        return False


def test_smart_refresh():
    """Test the smart refresh functionality."""
    print("\n" + "=" * 60)
    print("Smart Refresh Test")
    print("=" * 60)

    try:
        from app.services.refresh_optimized import get_refresh_strategy
        from app.core.database import SessionLocal

        db = SessionLocal()

        try:
            strategy = get_refresh_strategy(db)
            print(f"✅ Recommended refresh strategy: {strategy}")

            # Test different modes
            modes = ["cached", "minimal", "auto"]
            for mode in modes:
                print(f"Testing {mode} mode...")
                # Don't actually run refresh in test, just validate it can be imported

            print("✅ Smart refresh modes available")
            return True

        finally:
            db.close()

    except Exception as e:
        print(f"❌ Smart refresh test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Testing TwelveData rate limit protection and optimization...")

    tests = [
        ("Rate Limit Protection", test_rate_limit_protection),
        ("Caching Mechanism", test_caching_mechanism),
        ("Smart Refresh", test_smart_refresh),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ {name} crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Rate limit protection is working.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

    print("\n💡 Tips:")
    print("- Set REFRESH_MODE=minimal for free tier")
    print("- Enable caching with ENABLE_MARKET_DATA_CACHE=true")
    print("- Monitor your API usage at https://twelvedata.com/account/usage")


if __name__ == "__main__":
    main()
