"""Shared test fixtures and configuration."""

import os
import pytest
from typing import Generator
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Set test environment variables before importing app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-32chars"
os.environ["TWELVEDATA_API_KEY"] = "test-api-key"
os.environ["DEBUG"] = "true"

from app.main import app
from app.core.database import Base
from app.models import User, Asset, Price, StrategyConfig
from app.utils.security import get_password_hash


@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """Create a test database session."""
    # Create in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db: Session) -> TestClient:
    """Create a test client with database override."""
    from app.core.database import get_db

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(test_db: Session) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def auth_headers(client: TestClient, test_user: User) -> dict:
    """Get authentication headers for test user."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_assets(test_db: Session) -> list[Asset]:
    """Create sample assets for testing."""
    assets = [
        Asset(symbol="AAPL", name="Apple Inc.", sector="Technology"),
        Asset(symbol="MSFT", name="Microsoft Corp.", sector="Technology"),
        Asset(symbol="GOOGL", name="Alphabet Inc.", sector="Technology"),
        Asset(symbol="SPY", name="SPDR S&P 500 ETF", sector="Benchmark"),
        Asset(symbol="GLD", name="SPDR Gold Shares", sector="Commodity"),
    ]

    for asset in assets:
        test_db.add(asset)
    test_db.commit()

    for asset in assets:
        test_db.refresh(asset)

    return assets


@pytest.fixture
def sample_prices(test_db: Session, sample_assets: list[Asset]) -> list[Price]:
    """Create sample price data for testing."""
    prices = []
    _base_date = date(2024, 1, 1)

    for day_offset in range(30):  # 30 days of data
        current_date = date(2024, 1, 1 + day_offset)
        for asset in sample_assets:
            # Generate realistic price with some volatility
            base_price = {
                "AAPL": 150,
                "MSFT": 300,
                "GOOGL": 140,
                "SPY": 450,
                "GLD": 180,
            }
            price_value = base_price.get(asset.symbol, 100) * (1 + (day_offset * 0.001))

            price = Price(
                asset_id=asset.id, date=current_date, close=price_value, volume=1000000
            )
            prices.append(price)
            test_db.add(price)

    test_db.commit()
    return prices


@pytest.fixture
def sample_strategy_config(test_db: Session) -> StrategyConfig:
    """Create a sample strategy configuration."""
    config = StrategyConfig(
        momentum_weight=0.4,
        market_cap_weight=0.3,
        risk_parity_weight=0.3,
        rebalance_frequency="monthly",
        min_price_threshold=1.0,
        max_daily_return=0.5,
        min_daily_return=-0.5,
        max_forward_fill_days=2,
        outlier_std_threshold=3.0,
        daily_drop_threshold=-0.01,
    )
    test_db.add(config)
    test_db.commit()
    test_db.refresh(config)
    return config


@pytest.fixture
def mock_twelvedata_response():
    """Mock TwelveData API response."""
    return {
        "AAPL": {
            "meta": {
                "symbol": "AAPL",
                "interval": "1day",
                "currency": "USD",
                "exchange": "NASDAQ",
                "type": "Common Stock",
            },
            "values": [
                {
                    "datetime": "2024-01-01",
                    "open": "150.00",
                    "high": "152.00",
                    "low": "149.00",
                    "close": "151.00",
                    "volume": "50000000",
                },
                {
                    "datetime": "2024-01-02",
                    "open": "151.00",
                    "high": "153.00",
                    "low": "150.50",
                    "close": "152.50",
                    "volume": "48000000",
                },
            ],
            "status": "ok",
        }
    }
