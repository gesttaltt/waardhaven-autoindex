from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from ..core.database import get_db
from ..models.asset import Asset, Price
from ..models.index import IndexValue, Allocation
from ..models.user import User
from ..utils.cache_utils import CacheManager
from ..core.redis_client import get_redis_client
import traceback

router = APIRouter()

@router.get("/database-status")
def check_database_status(db: Session = Depends(get_db)):
    """Check the current state of the database tables."""
    try:
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "tables": {}
        }
        
        # Check each table
        tables = [
            ("users", User),
            ("assets", Asset),
            ("prices", Price),
            ("index_values", IndexValue),
            ("allocations", Allocation)
        ]
        
        for table_name, model in tables:
            try:
                count = db.query(func.count()).select_from(model).scalar()
                
                # Get date range for time-series tables
                date_info = {}
                if hasattr(model, 'date'):
                    min_date = db.query(func.min(model.date)).scalar()
                    max_date = db.query(func.max(model.date)).scalar()
                    date_info = {
                        "earliest_date": str(min_date) if min_date else None,
                        "latest_date": str(max_date) if max_date else None
                    }
                
                status["tables"][table_name] = {
                    "count": count,
                    "status": "OK" if count > 0 else "EMPTY",
                    **date_info
                }
            except Exception as e:
                status["tables"][table_name] = {
                    "count": 0,
                    "status": "ERROR",
                    "error": str(e)
                }
        
        # Check if we have enough data for simulation
        index_count = status["tables"]["index_values"]["count"]
        status["simulation_ready"] = index_count > 0
        status["message"] = "Database is ready for simulation" if index_count > 0 else "No index data available - refresh needed"
        
        return status
        
    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "ERROR",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@router.get("/refresh-status")
def check_refresh_requirements(db: Session = Depends(get_db)):
    """Check what needs to be refreshed."""
    try:
        # Check assets
        assets = db.query(Asset).all()
        asset_symbols = [a.symbol for a in assets]
        
        # Check for S&P 500 benchmark
        has_benchmark = "^GSPC" in asset_symbols
        
        # Check price data freshness
        latest_price_date = db.query(func.max(Price.date)).scalar()
        days_old = (datetime.now().date() - latest_price_date).days if latest_price_date else None
        
        return {
            "assets": {
                "count": len(assets),
                "symbols": asset_symbols,
                "has_benchmark": has_benchmark
            },
            "prices": {
                "latest_date": str(latest_price_date) if latest_price_date else None,
                "days_old": days_old,
                "needs_update": days_old > 1 if days_old is not None else True
            },
            "recommendation": "Run refresh to populate data" if latest_price_date is None else (
                "Data is up to date" if days_old <= 1 else f"Data is {days_old} days old, consider refreshing"
            )
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@router.get("/cache-status")
def check_cache_status():
    """Check Redis cache status and statistics."""
    try:
        redis_client = get_redis_client()
        
        # Basic connection check
        is_connected = redis_client.health_check()
        
        if not is_connected:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "status": "disconnected",
                "message": "Redis cache is not available. Running without cache.",
                "stats": {}
            }
        
        # Get detailed stats
        stats = CacheManager.get_cache_stats()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "connected",
            "stats": stats,
            "message": f"Cache is operational with {stats.get('total_entries', 0)} entries"
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@router.post("/cache-invalidate")
def invalidate_cache(pattern: str = "*"):
    """Invalidate cache entries matching pattern."""
    try:
        if pattern == "*":
            count = CacheManager.invalidate_all()
            message = f"Invalidated all {count} cache entries"
        elif pattern == "index":
            count = CacheManager.invalidate_index_data()
            message = f"Invalidated {count} index-related cache entries"
        elif pattern == "market":
            count = CacheManager.invalidate_market_data()
            message = f"Invalidated {count} market data cache entries"
        else:
            from ..utils.cache_utils import invalidate_pattern
            count = invalidate_pattern(pattern)
            message = f"Invalidated {count} entries matching pattern: {pattern}"
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "invalidated_count": count,
            "message": message
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@router.post("/test-refresh")
def test_refresh_process(db: Session = Depends(get_db)):
    """Test the refresh process with detailed error reporting."""
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "steps": []
    }
    
    try:
        # Step 1: Test asset creation
        from ..services.refresh import ensure_assets
        results["steps"].append({"step": "ensure_assets", "status": "starting"})
        ensure_assets(db)
        asset_count = db.query(func.count()).select_from(Asset).scalar()
        results["steps"].append({
            "step": "ensure_assets", 
            "status": "success",
            "asset_count": asset_count
        })
        
        # Step 2: Test price fetching for one symbol
        from ..services.twelvedata import fetch_prices
        import pandas as pd
        from datetime import date, timedelta
        
        results["steps"].append({"step": "fetch_prices", "status": "starting"})
        test_symbol = "AAPL"
        start_date = date.today() - timedelta(days=30)
        
        try:
            price_df = fetch_prices([test_symbol], start=start_date)
            results["steps"].append({
                "step": "fetch_prices",
                "status": "success",
                "symbol": test_symbol,
                "rows": len(price_df),
                "columns": list(price_df.columns.levels[0]) if hasattr(price_df.columns, 'levels') else list(price_df.columns)
            })
        except Exception as e:
            results["steps"].append({
                "step": "fetch_prices",
                "status": "failed",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            
        # Step 3: Check database connectivity
        results["steps"].append({"step": "database_write", "status": "starting"})
        try:
            # Try to write a test record
            test_asset = db.query(Asset).filter(Asset.symbol == "AAPL").first()
            if test_asset and not price_df.empty:
                # Just test, don't actually write
                results["steps"].append({
                    "step": "database_write",
                    "status": "ready",
                    "message": "Database is writable"
                })
            else:
                results["steps"].append({
                    "step": "database_write",
                    "status": "skipped",
                    "message": "No test data to write"
                })
        except Exception as e:
            results["steps"].append({
                "step": "database_write",
                "status": "failed",
                "error": str(e)
            })
            
        results["overall_status"] = "PARTIAL_SUCCESS"
        
    except Exception as e:
        results["overall_status"] = "FAILED"
        results["error"] = str(e)
        results["traceback"] = traceback.format_exc()
    
    return results

@router.post("/recalculate-index")
def recalculate_autoindex(db: Session = Depends(get_db)):
    """Recalculate the AutoIndex with proper normalization."""
    try:
        from ..services.strategy import compute_index_and_allocations
        
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "starting"
        }
        
        # Get counts before
        before_index_count = db.query(func.count()).select_from(IndexValue).scalar()
        before_allocation_count = db.query(func.count()).select_from(Allocation).scalar()
        
        # Recalculate
        compute_index_and_allocations(db)
        
        # Get counts after
        after_index_count = db.query(func.count()).select_from(IndexValue).scalar()
        after_allocation_count = db.query(func.count()).select_from(Allocation).scalar()
        
        # Get sample values
        sample_values = db.query(IndexValue).order_by(IndexValue.date.desc()).limit(5).all()
        
        result.update({
            "status": "success",
            "before": {
                "index_values": before_index_count,
                "allocations": before_allocation_count
            },
            "after": {
                "index_values": after_index_count,
                "allocations": after_allocation_count
            },
            "sample_recent_values": [
                {"date": str(iv.date), "value": iv.value} for iv in sample_values
            ]
        })
        
        return result
        
    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }