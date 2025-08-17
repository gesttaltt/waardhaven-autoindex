"""
Pydantic schemas for API request/response validation.
Organized by domain for better modularity.
"""

from .auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse
)

from .index import (
    AllocationItem,
    IndexCurrentResponse,
    SeriesPoint,
    IndexHistoryResponse,
    SimulationRequest,
    SimulationResponse
)

from .benchmark import (
    BenchmarkResponse
)

from .broker import (
    OrderRequest,
    OrderResponse
)

from .strategy import (
    StrategyConfigRequest,
    StrategyConfigResponse,
    RiskMetric,
    RiskMetricsResponse
)

__all__ = [
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    # Index
    "AllocationItem",
    "IndexCurrentResponse",
    "SeriesPoint",
    "IndexHistoryResponse",
    "SimulationRequest",
    "SimulationResponse",
    # Benchmark
    "BenchmarkResponse",
    # Broker
    "OrderRequest",
    "OrderResponse",
    # Strategy
    "StrategyConfigRequest",
    "StrategyConfigResponse",
    "RiskMetric",
    "RiskMetricsResponse",
]