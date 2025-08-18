"""API endpoint integration tests."""
import pytest
from datetime import date
from unittest.mock import patch

from app.models import Asset, Price, IndexValue, Allocation


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    @pytest.mark.api
    def test_register_user(self, client):
        """Test user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "SecurePassword123!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "id" in data
        assert "hashed_password" not in data  # Should not expose password
    
    @pytest.mark.api
    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.api
    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    @pytest.mark.api
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user info."""
        response = client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"


class TestIndexEndpoints:
    """Test index management endpoints."""
    
    @pytest.mark.api
    def test_get_index_history(self, client, auth_headers, test_db):
        """Test getting index history."""
        # Add some index values
        for i in range(5):
            test_db.add(IndexValue(
                date=date(2024, 1, i + 1),
                value=100 + i
            ))
        test_db.commit()
        
        response = client.get(
            "/api/v1/index/history",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "series" in data
        assert len(data["series"]) == 5
        assert data["series"][0]["value"] == 100
    
    @pytest.mark.api
    def test_get_current_allocations(self, client, auth_headers, test_db, sample_assets):
        """Test getting current allocations."""
        # Add allocations
        latest_date = date(2024, 1, 1)
        for i, asset in enumerate(sample_assets[:3]):
            test_db.add(Allocation(
                date=latest_date,
                asset_id=asset.id,
                weight=0.33
            ))
        test_db.commit()
        
        response = client.get(
            "/api/v1/index/current",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "allocations" in data
        assert len(data["allocations"]) == 3
        assert all("symbol" in a for a in data["allocations"])
        assert all("weight" in a for a in data["allocations"])
    
    @pytest.mark.api
    def test_simulate_investment(self, client, auth_headers, test_db):
        """Test investment simulation."""
        # Add index values for simulation
        values = [100, 102, 105, 103, 108, 110]
        for i, val in enumerate(values):
            test_db.add(IndexValue(
                date=date(2024, 1, i + 1),
                value=val
            ))
        test_db.commit()
        
        response = client.post(
            "/api/v1/index/simulate",
            headers=auth_headers,
            json={
                "amount": 10000,
                "currency": "USD",
                "start_date": "2024-01-01"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "amount_final" in data
        assert "roi_pct" in data
        assert data["amount_final"] > 0
        # ROI should be 10% (100 -> 110)
        assert abs(data["roi_pct"] - 10.0) < 0.1
    
    @pytest.mark.api
    def test_get_asset_history(self, client, auth_headers, test_db, sample_assets):
        """Test getting individual asset history."""
        # Add price data for AAPL
        aapl = sample_assets[0]
        for i in range(5):
            test_db.add(Price(
                asset_id=aapl.id,
                date=date(2024, 1, i + 1),
                close=150 + i,
                volume=1000000
            ))
        test_db.commit()
        
        response = client.get(
            "/api/v1/index/assets/AAPL/history",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "series" in data
        assert len(data["series"]) == 5
        assert data["series"][0]["value"] == 150


class TestStrategyEndpoints:
    """Test strategy configuration endpoints."""
    
    @pytest.mark.api
    def test_get_strategy_config(self, client, auth_headers, sample_strategy_config):
        """Test getting strategy configuration."""
        response = client.get(
            "/api/v1/strategy/config",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["momentum_weight"] == 0.4
        assert data["market_cap_weight"] == 0.3
        assert data["risk_parity_weight"] == 0.3
    
    @pytest.mark.api
    def test_update_strategy_config(self, client, auth_headers, sample_strategy_config):
        """Test updating strategy configuration."""
        response = client.put(
            "/api/v1/strategy/config",
            headers=auth_headers,
            json={
                "momentum_weight": 0.5,
                "market_cap_weight": 0.25,
                "risk_parity_weight": 0.25
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["momentum_weight"] == 0.5
        assert data["market_cap_weight"] == 0.25
        assert data["risk_parity_weight"] == 0.25
        
        # Weights should sum to 1
        total = data["momentum_weight"] + data["market_cap_weight"] + data["risk_parity_weight"]
        assert abs(total - 1.0) < 0.001
    
    @pytest.mark.api
    def test_get_risk_metrics(self, client, auth_headers, test_db):
        """Test getting risk metrics."""
        # Add index values for metric calculation
        values = [100, 102, 101, 103, 105, 104, 106, 108]
        for i, val in enumerate(values):
            test_db.add(IndexValue(
                date=date(2024, 1, i + 1),
                value=val
            ))
        test_db.commit()
        
        response = client.get(
            "/api/v1/strategy/risk-metrics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "sharpe_ratio" in data
        assert "max_drawdown" in data
        assert "volatility" in data


class TestDiagnosticsEndpoints:
    """Test diagnostic endpoints."""
    
    @pytest.mark.api
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @pytest.mark.api
    def test_data_status(self, client, auth_headers, test_db, sample_assets, sample_prices):
        """Test data status endpoint."""
        response = client.get(
            "/api/v1/diagnostics/data-status",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_assets" in data
        assert "total_prices" in data
        assert "last_refresh" in data
        assert data["total_assets"] == len(sample_assets)
        assert data["total_prices"] == len(sample_prices)


class TestManualRefreshEndpoints:
    """Test manual refresh endpoints."""
    
    @pytest.mark.api
    def test_trigger_refresh_requires_auth(self, client):
        """Test that refresh requires authentication."""
        response = client.post("/api/v1/manual/refresh")
        assert response.status_code == 401
    
    @pytest.mark.api
    def test_trigger_refresh_with_auth(self, client, auth_headers, test_db):
        """Test triggering manual refresh."""
        # Mock the refresh function to avoid actual API calls
        with patch('app.routers.manual_refresh.refresh_all') as mock_refresh:
            mock_refresh.return_value = None
            
            response = client.post(
                "/api/v1/manual/refresh",
                headers=auth_headers,
                json={"mode": "smart"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "started_at" in data
            
            # Verify refresh was called
            mock_refresh.assert_called_once()


class TestBenchmarkEndpoints:
    """Test benchmark endpoints."""
    
    @pytest.mark.api
    def test_get_sp500_benchmark(self, client, auth_headers, test_db):
        """Test getting S&P 500 benchmark data."""
        # Add S&P 500 asset and prices
        sp500 = Asset(symbol="SPY", name="S&P 500", sector="Benchmark")
        test_db.add(sp500)
        test_db.commit()
        test_db.refresh(sp500)
        
        for i in range(5):
            test_db.add(Price(
                asset_id=sp500.id,
                date=date(2024, 1, i + 1),
                close=450 + i,
                volume=10000000
            ))
        test_db.commit()
        
        response = client.get(
            "/api/v1/benchmark/sp500",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "series" in data
        assert len(data["series"]) == 5
        assert data["series"][0]["value"] == 450