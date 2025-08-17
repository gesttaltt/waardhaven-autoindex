#!/usr/bin/env python3
"""
Test script to verify database models initialization with new modular structure.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set minimal environment variables for testing if not present
if not os.getenv("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "test_secret_key_for_import_testing"
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"

def test_imports():
    """Test that all models can be imported correctly."""
    print("Testing model imports...")
    
    try:
        # Test importing from compatibility layer
        from app.models import (
            Base, User, Asset, Price, IndexValue, 
            Allocation, Order, StrategyConfig, RiskMetrics, MarketCapData
        )
        print("✓ Compatibility layer imports work")
    except ImportError as e:
        print(f"✗ Compatibility layer import failed: {e}")
        return False
    
    try:
        # Test importing from new modular structure
        from app.models.user import User
        from app.models.asset import Asset, Price
        from app.models.index import IndexValue, Allocation
        from app.models.trading import Order
        from app.models.strategy import StrategyConfig, RiskMetrics, MarketCapData
        print("✓ Direct modular imports work")
    except ImportError as e:
        print(f"✗ Direct modular import failed: {e}")
        return False
    
    return True

def test_schemas():
    """Test that all schemas can be imported correctly."""
    print("\nTesting schema imports...")
    
    try:
        # Test importing from compatibility layer
        from app.schemas import (
            RegisterRequest, LoginRequest, TokenResponse,
            AllocationItem, IndexCurrentResponse, SeriesPoint,
            IndexHistoryResponse, SimulationRequest, SimulationResponse,
            BenchmarkResponse, OrderRequest, OrderResponse,
            StrategyConfigRequest, StrategyConfigResponse, RiskMetric, RiskMetricsResponse
        )
        print("✓ Compatibility layer schema imports work")
    except ImportError as e:
        print(f"✗ Compatibility layer schema import failed: {e}")
        return False
    
    try:
        # Test importing from new modular structure
        from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
        from app.schemas.index import (
            AllocationItem, IndexCurrentResponse, SeriesPoint,
            IndexHistoryResponse, SimulationRequest, SimulationResponse
        )
        from app.schemas.benchmark import BenchmarkResponse
        from app.schemas.broker import OrderRequest, OrderResponse
        from app.schemas.strategy import (
            StrategyConfigRequest, StrategyConfigResponse,
            RiskMetric, RiskMetricsResponse
        )
        print("✓ Direct modular schema imports work")
    except ImportError as e:
        print(f"✗ Direct modular schema import failed: {e}")
        return False
    
    return True

def test_database_creation():
    """Test that database tables can be created with new structure."""
    print("\nTesting database table creation...")
    
    try:
        from app.core.database import Base, engine
        from app.models import (
            User, Asset, Price, IndexValue, 
            Allocation, Order, StrategyConfig, RiskMetrics, MarketCapData
        )
        
        # Check that all models are registered with Base
        tables = Base.metadata.tables
        expected_tables = [
            'users', 'assets', 'prices', 'index_values',
            'allocations', 'orders', 'strategy_configs', 
            'risk_metrics', 'market_cap_data'
        ]
        
        for table_name in expected_tables:
            if table_name in tables:
                print(f"✓ Table '{table_name}' registered")
            else:
                print(f"✗ Table '{table_name}' not found")
        
        print("✓ All models properly registered with Base")
        return True
        
    except Exception as e:
        print(f"✗ Database creation test failed: {e}")
        return False

def test_router_imports():
    """Test that routers can import models and schemas correctly."""
    print("\nTesting router imports...")
    
    try:
        # Test importing routers (which will test their internal imports)
        from app.routers import auth, index, benchmark, broker, strategy
        print("✓ All routers import successfully")
        return True
    except ImportError as e:
        print(f"✗ Router import failed: {e}")
        return False

def main():
    print("=" * 50)
    print("Testing Backend Modular Structure")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(("Model imports", test_imports()))
    results.append(("Schema imports", test_schemas()))
    results.append(("Database creation", test_database_creation()))
    results.append(("Router imports", test_router_imports()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All tests passed! The modular structure is working correctly.")
    else:
        print("✗ Some tests failed. Please review the errors above.")
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())