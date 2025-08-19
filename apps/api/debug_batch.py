#!/usr/bin/env python3
"""
Debug batch fetching issue.
"""

import os
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

os.environ["TWELVEDATA_API_KEY"] = "e9b09b7610734d2699dc083f4ef5336d"

from twelvedata import TDClient

client = TDClient(apikey=os.environ["TWELVEDATA_API_KEY"])

# Test batch fetch
symbols = ["AAPL", "MSFT"]
start = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
end = date.today().strftime("%Y-%m-%d")

print(f"Fetching batch for {symbols}...")

ts = client.time_series(
    symbol=symbols,  # Pass as list
    interval="1day",
    start_date=start,
    end_date=end,
    outputsize=10,
    order="asc"
)

# Check as JSON first
json_data = ts.as_json()
print(f"\nJSON data keys: {json_data.keys() if json_data else 'None'}")

if json_data:
    for symbol in symbols:
        if symbol in json_data:
            print(f"\n{symbol} data:")
            symbol_data = json_data[symbol]
            print(f"  - Type: {type(symbol_data)}")
            
            if isinstance(symbol_data, dict):
                if "values" in symbol_data:
                    print(f"  - Has 'values' key with {len(symbol_data['values'])} entries")
                    if symbol_data['values']:
                        print(f"  - First entry: {symbol_data['values'][0]}")
                else:
                    print(f"  - Keys: {symbol_data.keys()}")
                    print(f"  - Data: {symbol_data}")
            else:
                print(f"  - Data (not dict): {symbol_data}")

# Try as pandas
try:
    df = ts.as_pandas()
    print(f"\nPandas DataFrame:")
    print(f"  - Shape: {df.shape if df is not None else 'None'}")
    print(f"  - Empty: {df.empty if df is not None else 'N/A'}")
    if df is not None and not df.empty:
        print(f"  - Columns: {df.columns}")
except Exception as e:
    print(f"Error converting to pandas: {e}")