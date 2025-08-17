"""
Index-related schemas for portfolio management.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import date as DateType
from typing import List, Optional


class AllocationItem(BaseModel):
    """Individual asset allocation in the index."""
    symbol: str = Field(..., description="Asset ticker symbol")
    weight: float = Field(..., ge=0, le=1, description="Weight in portfolio (0-1)")
    name: Optional[str] = Field(None, description="Asset name")
    sector: Optional[str] = Field(None, description="Asset sector")
    daily_return: Optional[float] = Field(None, description="Daily return percentage")
    ytd_return: Optional[float] = Field(None, description="Year-to-date return percentage")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "AAPL",
                "weight": 0.15,
                "name": "Apple Inc.",
                "sector": "Technology",
                "daily_return": 1.25,
                "ytd_return": 35.6
            }
        }
    )


class IndexCurrentResponse(BaseModel):
    """Current index composition response."""
    date: DateType = Field(..., description="Date of the allocation")
    allocations: List[AllocationItem] = Field(..., description="List of asset allocations")
    total_assets: Optional[int] = Field(None, description="Total number of assets")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date": "2024-01-15",
                "allocations": [
                    {
                        "symbol": "AAPL",
                        "weight": 0.15,
                        "name": "Apple Inc.",
                        "sector": "Technology"
                    }
                ],
                "total_assets": 10
            }
        }
    )


class SeriesPoint(BaseModel):
    """Time series data point."""
    date: DateType = Field(..., description="Date of the data point")
    value: float = Field(..., description="Value at this date (base 100)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date": "2024-01-15",
                "value": 125.50
            }
        }
    )


class IndexHistoryResponse(BaseModel):
    """Historical index performance response."""
    series: List[SeriesPoint] = Field(..., description="Time series of index values")
    start_date: Optional[DateType] = Field(None, description="Start date of the series")
    end_date: Optional[DateType] = Field(None, description="End date of the series")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "series": [
                    {"date": "2024-01-01", "value": 100.0},
                    {"date": "2024-01-02", "value": 101.5}
                ],
                "start_date": "2024-01-01",
                "end_date": "2024-01-15"
            }
        }
    )


class SimulationRequest(BaseModel):
    """Investment simulation request."""
    amount: float = Field(..., gt=0, description="Investment amount")
    start_date: DateType = Field(..., description="Simulation start date")
    currency: str = Field("USD", description="Currency code")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "amount": 10000,
                "start_date": "2023-01-01",
                "currency": "USD"
            }
        }
    )


class SimulationResponse(BaseModel):
    """Investment simulation results."""
    start_date: DateType
    end_date: DateType
    start_value: float
    end_value: float
    amount_initial: float
    amount_final: float
    roi_pct: float = Field(..., description="Return on investment percentage")
    currency: str
    series: List[SeriesPoint] = Field(..., description="Value progression over time")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_date": "2023-01-01",
                "end_date": "2024-01-15",
                "start_value": 100.0,
                "end_value": 125.5,
                "amount_initial": 10000,
                "amount_final": 12550,
                "roi_pct": 25.5,
                "currency": "USD",
                "series": []
            }
        }
    )