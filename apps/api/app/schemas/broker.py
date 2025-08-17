"""
Broker and trading related schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class OrderRequest(BaseModel):
    """Trading order request."""
    asset_symbol: str = Field(..., description="Asset ticker symbol")
    type: Literal["BUY", "SELL"] = Field(..., description="Order type")
    amount: float = Field(..., gt=0, description="Order amount in USD")
    
    class Config:
        json_schema_extra = {
            "example": {
                "asset_symbol": "AAPL",
                "type": "BUY",
                "amount": 1000.0
            }
        }


class OrderResponse(BaseModel):
    """Trading order response."""
    order_id: int = Field(..., description="Unique order identifier")
    asset_symbol: str
    type: Literal["BUY", "SELL"]
    amount: float
    created_at: datetime
    status: str = Field("pending", description="Order status")
    execution_price: Optional[float] = Field(None, description="Execution price if filled")
    
    class Config:
        json_schema_extra = {
            "example": {
                "order_id": 1,
                "asset_symbol": "AAPL",
                "type": "BUY",
                "amount": 1000.0,
                "created_at": "2024-01-15T10:30:00",
                "status": "filled",
                "execution_price": 185.50
            }
        }