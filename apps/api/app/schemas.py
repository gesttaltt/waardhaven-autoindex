from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import List, Optional

# Auth
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Index
class AllocationItem(BaseModel):
    symbol: str
    weight: float
    name: Optional[str] = None
    sector: Optional[str] = None
    daily_return: Optional[float] = None
    ytd_return: Optional[float] = None

class IndexCurrentResponse(BaseModel):
    date: date
    allocations: List[AllocationItem]

class SeriesPoint(BaseModel):
    date: date
    value: float

class IndexHistoryResponse(BaseModel):
    series: List[SeriesPoint]

class SimulationRequest(BaseModel):
    amount: float
    start_date: date
    currency: str = "USD"  # Default to USD

class SimulationResponse(BaseModel):
    start_date: date
    end_date: date
    start_value: float
    end_value: float
    amount_initial: float
    amount_final: float
    roi_pct: float
    series: List[SeriesPoint]
    currency: str  # Currency used for amounts

# Orders
class OrderRequest(BaseModel):
    type: str  # "BUY" or "SELL"
    amount: float

class OrderResponse(BaseModel):
    id: int
    created_at: datetime

# Benchmark
class BenchmarkResponse(BaseModel):
    series: List[SeriesPoint]
