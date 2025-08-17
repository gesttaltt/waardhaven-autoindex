"""
Admin setup router for initial database configuration.
TEMPORARY - Should be removed after initial setup.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..core.database import get_db
from ..models.user import User
from ..models.strategy import StrategyConfig
from ..utils.security import get_password_hash
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/setup-admin")
def setup_admin_user(
    email: str = "admin@waardhaven.com",
    password: str = "changeme123",
    db: Session = Depends(get_db)
):
    """
    Create initial admin user and strategy configuration.
    This endpoint should be called once during initial setup and then removed.
    
    WARNING: This is for development/initial setup only!
    """
    
    # Check if running in production
    if os.getenv("RENDER") and not os.getenv("ALLOW_ADMIN_SETUP"):
        raise HTTPException(
            status_code=403,
            detail="Admin setup is disabled in production. Set ALLOW_ADMIN_SETUP=true to enable temporarily."
        )
    
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "steps": []
    }
    
    # Step 1: Create admin user if doesn't exist
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        results["steps"].append({
            "step": "create_admin_user",
            "status": "skipped",
            "message": f"User {email} already exists"
        })
    else:
        admin_user = User(
            email=email,
            password_hash=get_password_hash(password)
        )
        db.add(admin_user)
        db.commit()
        results["steps"].append({
            "step": "create_admin_user", 
            "status": "success",
            "message": f"Admin user {email} created successfully"
        })
    
    # Step 2: Create default strategy config if doesn't exist
    existing_config = db.query(StrategyConfig).first()
    if existing_config:
        results["steps"].append({
            "step": "create_strategy_config",
            "status": "skipped",
            "message": "Strategy configuration already exists"
        })
    else:
        default_config = StrategyConfig(
            momentum_weight=0.4,
            market_cap_weight=0.3,
            risk_parity_weight=0.3,
            daily_drop_threshold=-0.01,
            max_daily_return=0.5,
            min_daily_return=-0.5,
            min_price_threshold=1.0,
            rebalance_frequency="weekly",
            max_forward_fill_days=2,
            outlier_std_threshold=3.0
        )
        db.add(default_config)
        db.commit()
        results["steps"].append({
            "step": "create_strategy_config",
            "status": "success",
            "message": "Default strategy configuration created"
        })
    
    # Step 3: Provide connection info
    results["connection_info"] = {
        "login_endpoint": "/api/v1/auth/login",
        "credentials": {
            "email": email,
            "password": "***" if existing_user else password
        },
        "note": "Use these credentials to login and get an access token"
    }
    
    results["warning"] = "REMOVE THIS ENDPOINT FROM PRODUCTION CODE!"
    
    return results

@router.delete("/cleanup-test-data")
def cleanup_test_data(
    confirm: bool = False,
    db: Session = Depends(get_db)
):
    """
    Clean up test data from the database.
    Use with caution - this will delete data!
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Set confirm=true to proceed with cleanup"
        )
    
    # Only allow in development
    if os.getenv("RENDER"):
        raise HTTPException(
            status_code=403,
            detail="Cleanup is not allowed in production"
        )
    
    # Implement cleanup logic here if needed
    return {"message": "Cleanup not implemented yet"}