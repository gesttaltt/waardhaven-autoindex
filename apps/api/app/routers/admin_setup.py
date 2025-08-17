"""
Temporary admin endpoint to set up database indexes.
DELETE THIS FILE after running once in production!
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from ..core.database import engine
from ..utils.token_dep import get_current_user
from ..models import User
import os

router = APIRouter()

@router.post("/setup-indexes")
def setup_indexes(
    admin_token: str,
    user: User = Depends(get_current_user)
):
    """
    One-time setup to create database indexes.
    Requires admin token from environment variable.
    """
    
    # Check admin token
    if admin_token != os.getenv("ADMIN_TOKEN", "change-me-in-production"):
        raise HTTPException(status_code=403, detail="Invalid admin token")
    
    indexes_created = []
    errors = []
    
    index_queries = [
        ("idx_prices_asset_date", 
         "CREATE INDEX IF NOT EXISTS idx_prices_asset_date ON prices(asset_id, date DESC)"),
        
        ("idx_allocations_date",
         "CREATE INDEX IF NOT EXISTS idx_allocations_date ON allocations(date DESC)"),
        
        ("idx_index_values_date",
         "CREATE INDEX IF NOT EXISTS idx_index_values_date ON index_values(date DESC)"),
        
        ("idx_risk_metrics_date",
         "CREATE INDEX IF NOT EXISTS idx_risk_metrics_date ON risk_metrics(date DESC)"),
        
        ("idx_users_email_lower",
         "CREATE INDEX IF NOT EXISTS idx_users_email_lower ON users(LOWER(email))"),
    ]
    
    with engine.connect() as conn:
        for index_name, query in index_queries:
            try:
                conn.execute(text(query))
                conn.commit()
                indexes_created.append(index_name)
            except Exception as e:
                errors.append(f"{index_name}: {str(e)}")
        
        # Update statistics
        try:
            conn.execute(text("ANALYZE prices"))
            conn.execute(text("ANALYZE allocations"))
            conn.execute(text("ANALYZE index_values"))
            conn.execute(text("ANALYZE assets"))
            conn.commit()
            indexes_created.append("statistics_updated")
        except Exception as e:
            errors.append(f"statistics: {str(e)}")
    
    return {
        "success": len(errors) == 0,
        "indexes_created": indexes_created,
        "errors": errors,
        "message": "Delete the admin_setup.py file after running this!"
    }