"""
Compatibility layer for backward compatibility.
Re-exports all models from the new modular structure.

This file will be deprecated. Please import from app.models.* directly.
"""

# Re-export all models from modular structure
from .models.user import User
from .models.asset import Asset, Price
from .models.index import IndexValue, Allocation
from .models.trading import Order
from .models.strategy import StrategyConfig, RiskMetrics, MarketCapData

# Re-export Base for migrations
from .core.database import Base

# Make all models available for import
__all__ = [
    "Base",
    "User",
    "Asset",
    "Price",
    "IndexValue",
    "Allocation",
    "Order",
    "StrategyConfig",
    "RiskMetrics",
    "MarketCapData",
]