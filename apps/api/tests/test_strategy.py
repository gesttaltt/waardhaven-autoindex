"""Unit tests for strategy service."""
import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np

from app.services.strategy import (
    compute_index_and_allocations,
    calculate_momentum_scores,
    calculate_risk_parity_weights,
    apply_data_quality_filters
)
from app.models import Asset, Price, IndexValue, Allocation


class TestStrategyService:
    """Test strategy computation functions."""
    
    @pytest.mark.unit
    def test_compute_index_no_delete_on_failure(self, test_db, sample_assets, sample_prices):
        """Test that index computation doesn't delete data on failure."""
        # Add some existing index values
        existing_value = IndexValue(date=date(2023, 12, 31), value=100.0)
        test_db.add(existing_value)
        test_db.commit()
        
        # Mock a failure during computation
        with patch('app.services.strategy.calculate_momentum_scores') as mock_momentum:
            mock_momentum.side_effect = Exception("Computation failed")
            
            # Attempt computation (should fail)
            with pytest.raises(Exception):
                compute_index_and_allocations(test_db)
            
            # Verify existing data wasn't deleted
            remaining = test_db.query(IndexValue).filter(
                IndexValue.date == date(2023, 12, 31)
            ).first()
            assert remaining is not None
            assert remaining.value == 100.0
    
    @pytest.mark.unit
    def test_upsert_index_values(self, test_db, sample_assets, sample_prices):
        """Test that index values are upserted, not replaced."""
        # Add initial index value
        initial_value = IndexValue(date=date(2024, 1, 1), value=100.0)
        test_db.add(initial_value)
        test_db.commit()
        
        # Mock successful computation with overlapping date
        with patch('app.services.strategy.calculate_momentum_scores') as mock_momentum:
            mock_momentum.return_value = pd.Series([0.5] * len(sample_assets))
            
            with patch('app.services.strategy.calculate_risk_parity_weights') as mock_risk:
                mock_risk.return_value = pd.Series([0.2] * len(sample_assets))
                
                # Run computation
                compute_index_and_allocations(test_db, {
                    'momentum_weight': 0.5,
                    'risk_parity_weight': 0.5,
                    'market_cap_weight': 0.0
                })
        
        # Check that the value was updated, not duplicated
        values = test_db.query(IndexValue).filter(
            IndexValue.date == date(2024, 1, 1)
        ).all()
        assert len(values) == 1
        # Value should be updated (not the original 100.0)
        assert values[0].value != 100.0
    
    @pytest.mark.unit
    def test_backup_creation_on_update(self, test_db, sample_assets, sample_prices, caplog):
        """Test that backup is created before modifying data."""
        # Add existing data
        existing_value = IndexValue(date=date(2024, 1, 1), value=100.0)
        existing_allocation = Allocation(
            date=date(2024, 1, 1),
            asset_id=sample_assets[0].id,
            weight=0.25
        )
        test_db.add(existing_value)
        test_db.add(existing_allocation)
        test_db.commit()
        
        # Run computation
        with patch('app.services.strategy.calculate_momentum_scores') as mock_momentum:
            mock_momentum.return_value = pd.Series([0.5] * len(sample_assets))
            
            compute_index_and_allocations(test_db)
        
        # Check that backup was logged
        assert "Backed up" in caplog.text
        assert "index values" in caplog.text
        assert "allocations" in caplog.text
    
    @pytest.mark.unit
    def test_transaction_rollback_on_error(self, test_db, sample_assets, sample_prices):
        """Test that transaction is rolled back on error."""
        initial_count = test_db.query(IndexValue).count()
        
        # Mock an error during the commit phase
        original_commit = test_db.commit
        
        def failing_commit():
            # Restore original to avoid affecting other tests
            test_db.commit = original_commit
            raise Exception("Database error during commit")
        
        with patch('app.services.strategy.calculate_momentum_scores') as mock_momentum:
            mock_momentum.return_value = pd.Series([0.5] * len(sample_assets))
            
            test_db.commit = failing_commit
            
            # Should raise exception
            with pytest.raises(Exception, match="Database error"):
                compute_index_and_allocations(test_db)
        
        # Verify no new data was added (rollback successful)
        final_count = test_db.query(IndexValue).count()
        assert final_count == initial_count
    
    @pytest.mark.unit
    def test_data_quality_filters(self):
        """Test data quality filtering functions."""
        # Create sample data with outliers and gaps
        dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
        prices = pd.DataFrame({
            'AAPL': [150, 151, 152, 300, 153, 154, np.nan, 155, 10, 156],  # Outliers and NaN
            'MSFT': [300, 301, 302, 303, 304, 305, 306, 307, 308, 309]  # Clean data
        }, index=dates)
        
        # Apply filters
        config = {
            'min_price': 50.0,
            'max_daily_return': 0.1,
            'min_daily_return': -0.1,
            'outlier_std_threshold': 2.0
        }
        
        filtered = apply_data_quality_filters(prices, config)
        
        # Check that outliers were handled
        assert filtered['AAPL'].iloc[3] != 300  # Spike should be smoothed
        assert filtered['AAPL'].iloc[8] != 10   # Drop should be smoothed
        assert not filtered['AAPL'].isna().any()  # NaN should be filled
        
        # Clean data should be unchanged
        assert (filtered['MSFT'] == prices['MSFT']).all()
    
    @pytest.mark.unit
    def test_momentum_calculation(self):
        """Test momentum score calculation."""
        # Create price data with clear momentum
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        prices = pd.DataFrame({
            'AAPL': np.linspace(150, 180, 30),  # Strong upward momentum
            'MSFT': np.linspace(300, 290, 30),  # Downward momentum
            'GOOGL': [140] * 30,  # No momentum
        }, index=dates)
        
        # Calculate momentum scores
        scores = calculate_momentum_scores(prices, lookback_days=20)
        
        # AAPL should have highest momentum
        assert scores['AAPL'] > scores['GOOGL']
        assert scores['AAPL'] > scores['MSFT']
        # MSFT should have negative momentum
        assert scores['MSFT'] < 0
        # GOOGL should have near-zero momentum
        assert abs(scores['GOOGL']) < 0.01
    
    @pytest.mark.unit
    def test_risk_parity_weights(self):
        """Test risk parity weight calculation."""
        # Create returns with different volatilities
        np.random.seed(42)
        returns = pd.DataFrame({
            'AAPL': np.random.normal(0.001, 0.02, 100),   # High volatility
            'BONDS': np.random.normal(0.0005, 0.005, 100), # Low volatility
            'GOLD': np.random.normal(0.0007, 0.01, 100),   # Medium volatility
        })
        
        # Calculate risk parity weights
        weights = calculate_risk_parity_weights(returns)
        
        # Weights should sum to 1
        assert abs(weights.sum() - 1.0) < 0.001
        
        # Lower volatility assets should have higher weights
        assert weights['BONDS'] > weights['GOLD']
        assert weights['GOLD'] > weights['AAPL']
        
        # All weights should be positive
        assert (weights > 0).all()


class TestDataIntegrity:
    """Test data integrity during operations."""
    
    @pytest.mark.integration
    def test_concurrent_updates(self, test_db, sample_assets, sample_prices):
        """Test that concurrent updates don't corrupt data."""
        from threading import Thread
        import time
        
        def update_strategy():
            """Run strategy update in thread."""
            try:
                compute_index_and_allocations(test_db)
            except Exception:
                pass  # Expected to fail due to concurrent access
        
        # Start multiple threads
        threads = [Thread(target=update_strategy) for _ in range(3)]
        for t in threads:
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join(timeout=5)
        
        # Verify data integrity
        index_values = test_db.query(IndexValue).all()
        allocations = test_db.query(Allocation).all()
        
        # Should have consistent data (no duplicates for same date)
        dates = [iv.date for iv in index_values]
        assert len(dates) == len(set(dates)), "Duplicate dates found in index values"
    
    @pytest.mark.integration
    def test_old_data_cleanup(self, test_db, sample_assets):
        """Test that very old data is cleaned up properly."""
        # Add very old data
        old_date = date(2020, 1, 1)
        old_value = IndexValue(date=old_date, value=50.0)
        test_db.add(old_value)
        
        # Add recent data
        recent_date = date(2024, 1, 1)
        recent_value = IndexValue(date=recent_date, value=100.0)
        test_db.add(recent_value)
        test_db.commit()
        
        # Add price data for computation
        for asset in sample_assets:
            price = Price(
                asset_id=asset.id,
                date=recent_date,
                close=100.0,
                volume=1000000
            )
            test_db.add(price)
        test_db.commit()
        
        # Run computation
        with patch('app.services.strategy.calculate_momentum_scores') as mock_momentum:
            mock_momentum.return_value = pd.Series([0.5] * len(sample_assets))
            compute_index_and_allocations(test_db)
        
        # Old data (>1 year before new data) should be cleaned up
        old_remaining = test_db.query(IndexValue).filter(
            IndexValue.date == old_date
        ).first()
        assert old_remaining is None
        
        # Recent data should remain
        recent_remaining = test_db.query(IndexValue).filter(
            IndexValue.date == recent_date
        ).first()
        assert recent_remaining is not None