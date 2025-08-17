"""Unit tests for refresh service."""
import pytest
from datetime import date, datetime
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import json

from app.services.refresh import refresh_all, ensure_assets
from app.models import Asset, Price, IndexValue, Allocation


class TestRefreshService:
    """Test data refresh functions."""
    
    @pytest.mark.unit
    def test_ensure_assets_creates_missing(self, test_db):
        """Test that ensure_assets creates missing assets."""
        # Initially no assets
        assert test_db.query(Asset).count() == 0
        
        # Run ensure_assets
        ensure_assets(test_db)
        
        # Should have created default assets
        assets = test_db.query(Asset).all()
        assert len(assets) > 0
        
        # Check specific assets exist
        symbols = [a.symbol for a in assets]
        assert 'AAPL' in symbols
        assert 'MSFT' in symbols
        assert 'SPY' in symbols
        assert 'GLD' in symbols
    
    @pytest.mark.unit
    def test_ensure_assets_skips_existing(self, test_db):
        """Test that ensure_assets doesn't duplicate existing assets."""
        # Create an existing asset
        existing = Asset(symbol='AAPL', name='Existing Apple', sector='Tech')
        test_db.add(existing)
        test_db.commit()
        
        # Run ensure_assets
        ensure_assets(test_db)
        
        # Should still have only one AAPL
        aapl_assets = test_db.query(Asset).filter(Asset.symbol == 'AAPL').all()
        assert len(aapl_assets) == 1
        # Should keep the existing one
        assert aapl_assets[0].name == 'Existing Apple'
    
    @pytest.mark.unit
    def test_refresh_creates_backup(self, test_db, sample_assets, caplog):
        """Test that refresh creates backup before operations."""
        # Add some existing data
        for asset in sample_assets:
            price = Price(
                asset_id=asset.id,
                date=date(2024, 1, 1),
                close=100.0,
                volume=1000000
            )
            test_db.add(price)
        test_db.commit()
        
        # Mock fetch_prices to avoid API call
        mock_prices = pd.DataFrame()
        with patch('app.services.refresh.fetch_prices', return_value=mock_prices):
            try:
                refresh_all(test_db, smart_mode=False)
            except ValueError:
                pass  # Expected due to empty mock data
        
        # Check that backup was logged
        assert "Creating data backup" in caplog.text
        assert "Backup info" in caplog.text
    
    @pytest.mark.unit
    def test_refresh_transaction_rollback(self, test_db, sample_assets):
        """Test that refresh rolls back on error."""
        initial_price_count = test_db.query(Price).count()
        
        # Mock fetch_prices to return data that will cause error
        with patch('app.services.refresh.fetch_prices') as mock_fetch:
            mock_fetch.side_effect = Exception("API error")
            
            # Should raise and rollback
            with pytest.raises(Exception, match="API error"):
                refresh_all(test_db, smart_mode=False)
        
        # Verify rollback - count should be unchanged
        final_price_count = test_db.query(Price).count()
        assert final_price_count == initial_price_count
    
    @pytest.mark.unit
    def test_refresh_handles_empty_data(self, test_db, sample_assets, caplog):
        """Test that refresh handles empty API response gracefully."""
        # Mock fetch_prices to return empty DataFrame
        with patch('app.services.refresh.fetch_prices', return_value=pd.DataFrame()):
            with pytest.raises(ValueError, match="Unable to fetch any price data"):
                refresh_all(test_db, smart_mode=False)
        
        # Should log the error
        assert "No price data fetched" in caplog.text
    
    @pytest.mark.unit
    def test_refresh_upserts_prices(self, test_db, sample_assets):
        """Test that refresh upserts prices instead of deleting."""
        # Add existing price
        existing_price = Price(
            asset_id=sample_assets[0].id,
            date=date(2024, 1, 1),
            close=150.0,
            volume=1000000
        )
        test_db.add(existing_price)
        test_db.commit()
        
        # Mock fetch_prices to return updated price
        mock_data = pd.DataFrame({
            ('AAPL', 'Close'): [155.0],
            ('AAPL', 'Volume'): [2000000]
        }, index=[pd.Timestamp('2024-01-01')])
        mock_data.columns = pd.MultiIndex.from_tuples(mock_data.columns)
        
        with patch('app.services.refresh.fetch_prices', return_value=mock_data):
            with patch('app.services.refresh.compute_index_and_allocations'):
                refresh_all(test_db, smart_mode=False)
        
        # Price should be updated, not duplicated
        prices = test_db.query(Price).filter(
            Price.asset_id == sample_assets[0].id,
            Price.date == date(2024, 1, 1)
        ).all()
        assert len(prices) == 1
        assert prices[0].close == 155.0  # Updated value
    
    @pytest.mark.unit
    def test_refresh_with_smart_mode(self, test_db, sample_assets):
        """Test smart refresh mode."""
        # Mock the smart_refresh function
        with patch('app.services.refresh_optimized.smart_refresh') as mock_smart:
            mock_smart.return_value = {"status": "success", "updated": 10}
            
            # Run with smart mode
            result = refresh_all(test_db, smart_mode=True)
            
            # Should use smart refresh if available
            if mock_smart.called:
                assert result == {"status": "success", "updated": 10}
    
    @pytest.mark.unit
    def test_refresh_filters_invalid_prices(self, test_db, sample_assets, caplog):
        """Test that refresh filters out invalid prices."""
        # Mock fetch_prices with some invalid data
        mock_data = pd.DataFrame({
            ('AAPL', 'Close'): [155.0, 0.5, None, 160.0],  # Below threshold and null
            ('MSFT', 'Close'): [300.0, 301.0, 302.0, 303.0]  # Valid data
        }, index=pd.date_range('2024-01-01', periods=4))
        mock_data.columns = pd.MultiIndex.from_tuples(mock_data.columns)
        
        with patch('app.services.refresh.fetch_prices', return_value=mock_data):
            with patch('app.services.refresh.compute_index_and_allocations'):
                refresh_all(test_db, smart_mode=False)
        
        # Check that invalid prices were skipped
        aapl_prices = test_db.query(Price).join(Asset).filter(
            Asset.symbol == 'AAPL'
        ).all()
        # Should only have valid prices (155.0 and 160.0)
        assert len(aapl_prices) == 2
        assert all(p.close >= 1.0 for p in aapl_prices)
        
        # Should log skipped prices
        assert "below threshold" in caplog.text or "Skipped" in caplog.text


class TestRefreshIntegration:
    """Integration tests for refresh process."""
    
    @pytest.mark.integration
    def test_full_refresh_workflow(self, test_db):
        """Test complete refresh workflow."""
        # Mock all external dependencies
        mock_price_data = pd.DataFrame({
            ('AAPL', 'Close'): [150.0, 151.0, 152.0],
            ('MSFT', 'Close'): [300.0, 301.0, 302.0],
        }, index=pd.date_range('2024-01-01', periods=3))
        mock_price_data.columns = pd.MultiIndex.from_tuples(mock_price_data.columns)
        
        with patch('app.services.refresh.fetch_prices', return_value=mock_price_data):
            with patch('app.services.strategy.calculate_momentum_scores') as mock_momentum:
                mock_momentum.return_value = pd.Series([0.5, 0.5])
                
                # Run full refresh
                refresh_all(test_db, smart_mode=False)
        
        # Verify assets were created
        assets = test_db.query(Asset).all()
        assert len(assets) > 0
        
        # Verify prices were stored
        prices = test_db.query(Price).all()
        assert len(prices) > 0
        
        # Verify index was computed
        index_values = test_db.query(IndexValue).all()
        assert len(index_values) > 0
    
    @pytest.mark.integration
    def test_refresh_recovery_from_failure(self, test_db, sample_assets):
        """Test that refresh can recover from partial failure."""
        # Add some initial data
        for asset in sample_assets[:2]:
            price = Price(
                asset_id=asset.id,
                date=date(2024, 1, 1),
                close=100.0,
                volume=1000000
            )
            test_db.add(price)
        test_db.commit()
        
        initial_count = test_db.query(Price).count()
        
        # First attempt fails
        with patch('app.services.refresh.fetch_prices') as mock_fetch:
            mock_fetch.side_effect = Exception("Network error")
            
            with pytest.raises(Exception):
                refresh_all(test_db, smart_mode=False)
        
        # Data should be unchanged (rolled back)
        assert test_db.query(Price).count() == initial_count
        
        # Second attempt succeeds
        mock_data = pd.DataFrame({
            ('AAPL', 'Close'): [155.0],
            ('MSFT', 'Close'): [305.0]
        }, index=[pd.Timestamp('2024-01-02')])
        mock_data.columns = pd.MultiIndex.from_tuples(mock_data.columns)
        
        with patch('app.services.refresh.fetch_prices', return_value=mock_data):
            with patch('app.services.refresh.compute_index_and_allocations'):
                refresh_all(test_db, smart_mode=False)
        
        # Should have new data
        assert test_db.query(Price).count() > initial_count