import yfinance as yf
from datetime import date, datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Common currency pairs for USD base
CURRENCY_PAIRS = {
    "USD": 1.0,  # Base currency
    "EUR": "EURUSD=X",
    "GBP": "GBPUSD=X", 
    "JPY": "JPYUSD=X",
    "CAD": "CADUSD=X",
    "AUD": "AUDUSD=X",
    "CHF": "CHFUSD=X",
    "CNY": "CNYUSD=X",
    "INR": "INRUSD=X",
    "MXN": "MXNUSD=X",
    "BRL": "BRLUSD=X",
    "SEK": "SEKUSD=X",
    "NOK": "NOKUSD=X",
    "DKK": "DKKUSD=X",
    "SGD": "SGDUSD=X",
    "HKD": "HKDUSD=X",
    "KRW": "KRWUSD=X",
    "TWD": "TWDUSD=X",
    "NZD": "NZDUSD=X",
    "ZAR": "ZARUSD=X"
}

def get_exchange_rate(from_currency: str, to_currency: str = "USD") -> Optional[float]:
    """
    Get current exchange rate between two currencies.
    Returns the rate to convert from_currency to to_currency.
    """
    try:
        # If converting to/from USD
        if from_currency == to_currency:
            return 1.0
        
        if from_currency == "USD":
            # USD to other currency
            if to_currency in CURRENCY_PAIRS:
                if CURRENCY_PAIRS[to_currency] == 1.0:
                    return 1.0
                ticker = yf.Ticker(CURRENCY_PAIRS[to_currency])
                data = ticker.history(period="1d")
                if not data.empty:
                    # For USD to other, we need the reciprocal
                    return 1.0 / data['Close'].iloc[-1]
            return None
            
        elif to_currency == "USD":
            # Other currency to USD
            if from_currency in CURRENCY_PAIRS:
                if CURRENCY_PAIRS[from_currency] == 1.0:
                    return 1.0
                ticker = yf.Ticker(CURRENCY_PAIRS[from_currency])
                data = ticker.history(period="1d")
                if not data.empty:
                    return data['Close'].iloc[-1]
            return None
            
        else:
            # Cross rate through USD
            rate_to_usd = get_exchange_rate(from_currency, "USD")
            rate_from_usd = get_exchange_rate("USD", to_currency)
            if rate_to_usd and rate_from_usd:
                return rate_to_usd * rate_from_usd
            return None
            
    except Exception as e:
        logger.error(f"Error fetching exchange rate {from_currency} to {to_currency}: {e}")
        return None

def convert_amount(amount: float, from_currency: str, to_currency: str = "USD") -> Optional[float]:
    """
    Convert an amount from one currency to another.
    Returns None if conversion fails.
    """
    if from_currency == to_currency:
        return amount
        
    rate = get_exchange_rate(from_currency, to_currency)
    if rate:
        return amount * rate
    return None

def get_supported_currencies() -> Dict[str, str]:
    """
    Return dictionary of supported currency codes and their names.
    """
    return {
        "USD": "US Dollar",
        "EUR": "Euro",
        "GBP": "British Pound",
        "JPY": "Japanese Yen",
        "CAD": "Canadian Dollar",
        "AUD": "Australian Dollar",
        "CHF": "Swiss Franc",
        "CNY": "Chinese Yuan",
        "INR": "Indian Rupee",
        "MXN": "Mexican Peso",
        "BRL": "Brazilian Real",
        "SEK": "Swedish Krona",
        "NOK": "Norwegian Krone",
        "DKK": "Danish Krone",
        "SGD": "Singapore Dollar",
        "HKD": "Hong Kong Dollar",
        "KRW": "South Korean Won",
        "TWD": "Taiwan Dollar",
        "NZD": "New Zealand Dollar",
        "ZAR": "South African Rand"
    }