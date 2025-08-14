"""
API endpoints for managing strategy configuration.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Optional
from datetime import datetime
from ..core.database import get_db
from ..models import User, StrategyConfig, RiskMetrics
from ..utils.token_dep import get_current_user
from ..services.refresh import refresh_all
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/config")
def get_strategy_config(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get current strategy configuration."""
    config = db.query(StrategyConfig).first()
    if not config:
        raise HTTPException(status_code=404, detail="Strategy configuration not found")
    
    return {
        "momentum_weight": config.momentum_weight,
        "market_cap_weight": config.market_cap_weight,
        "risk_parity_weight": config.risk_parity_weight,
        "min_price_threshold": config.min_price_threshold,
        "max_daily_return": config.max_daily_return,
        "min_daily_return": config.min_daily_return,
        "max_forward_fill_days": config.max_forward_fill_days,
        "outlier_std_threshold": config.outlier_std_threshold,
        "rebalance_frequency": config.rebalance_frequency,
        "daily_drop_threshold": config.daily_drop_threshold,
        "ai_adjusted": config.ai_adjusted,
        "ai_adjustment_reason": config.ai_adjustment_reason,
        "ai_confidence_score": config.ai_confidence_score,
        "last_rebalance": config.last_rebalance,
        "updated_at": config.updated_at
    }

@router.put("/config")
def update_strategy_config(
    updates: Dict,
    recompute: bool = True,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Update strategy configuration.
    
    Args:
        updates: Dictionary of configuration updates
        recompute: Whether to recompute the index after updating
    """
    config = db.query(StrategyConfig).first()
    if not config:
        # Create new config if it doesn't exist
        config = StrategyConfig()
        db.add(config)
    
    # Validate weights sum to 1.0 if provided
    weight_keys = ['momentum_weight', 'market_cap_weight', 'risk_parity_weight']
    weights_provided = [k for k in weight_keys if k in updates]
    
    if weights_provided:
        # Get current weights
        current_weights = {
            'momentum_weight': config.momentum_weight,
            'market_cap_weight': config.market_cap_weight,
            'risk_parity_weight': config.risk_parity_weight
        }
        
        # Apply updates
        for key in weights_provided:
            current_weights[key] = updates[key]
        
        # Check sum
        total_weight = sum(current_weights.values())
        if abs(total_weight - 1.0) > 0.001:  # Allow small floating point errors
            raise HTTPException(
                status_code=400,
                detail=f"Strategy weights must sum to 1.0, got {total_weight}"
            )
    
    # Update configuration
    allowed_fields = [
        'momentum_weight', 'market_cap_weight', 'risk_parity_weight',
        'min_price_threshold', 'max_daily_return', 'min_daily_return',
        'max_forward_fill_days', 'outlier_std_threshold', 'rebalance_frequency',
        'daily_drop_threshold', 'force_rebalance'
    ]
    
    for field, value in updates.items():
        if field in allowed_fields:
            setattr(config, field, value)
    
    config.updated_at = datetime.utcnow()
    
    # Store in adjustment history
    if config.adjustment_history is None:
        config.adjustment_history = []
    
    config.adjustment_history.append({
        "timestamp": datetime.utcnow().isoformat(),
        "updates": updates,
        "user_id": user.id
    })
    
    db.commit()
    
    # Recompute index if requested
    if recompute:
        try:
            logger.info("Recomputing index with new configuration...")
            refresh_all(db, smart_mode=True)
            return {"message": "Configuration updated and index recomputed", "config": updates}
        except Exception as e:
            logger.error(f"Failed to recompute index: {e}")
            return {"message": "Configuration updated but index recomputation failed", "config": updates, "error": str(e)}
    
    return {"message": "Configuration updated", "config": updates}

@router.post("/config/ai-adjust")
def ai_adjust_strategy(
    adjustments: Dict,
    reason: str,
    confidence: float,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Apply AI-suggested strategy adjustments.
    
    Args:
        adjustments: Dictionary of AI-suggested adjustments
        reason: Explanation for the adjustments
        confidence: AI confidence score (0-1)
    """
    if confidence < 0 or confidence > 1:
        raise HTTPException(status_code=400, detail="Confidence must be between 0 and 1")
    
    config = db.query(StrategyConfig).first()
    if not config:
        raise HTTPException(status_code=404, detail="Strategy configuration not found")
    
    # Apply adjustments
    for field, value in adjustments.items():
        if hasattr(config, field):
            setattr(config, field, value)
    
    # Update AI metadata
    config.ai_adjusted = True
    config.ai_adjustment_reason = reason
    config.ai_confidence_score = confidence
    config.updated_at = datetime.utcnow()
    
    # Store in adjustment history
    if config.adjustment_history is None:
        config.adjustment_history = []
    
    config.adjustment_history.append({
        "timestamp": datetime.utcnow().isoformat(),
        "type": "ai_adjustment",
        "adjustments": adjustments,
        "reason": reason,
        "confidence": confidence
    })
    
    db.commit()
    
    # Trigger recomputation
    try:
        refresh_all(db, smart_mode=True)
        return {
            "message": "AI adjustments applied and index recomputed",
            "adjustments": adjustments,
            "reason": reason,
            "confidence": confidence
        }
    except Exception as e:
        logger.error(f"Failed to recompute index after AI adjustment: {e}")
        return {
            "message": "AI adjustments applied but recomputation failed",
            "adjustments": adjustments,
            "error": str(e)
        }

@router.get("/risk-metrics")
def get_risk_metrics(
    limit: int = 30,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get recent risk metrics for the index."""
    metrics = db.query(RiskMetrics).order_by(RiskMetrics.date.desc()).limit(limit).all()
    
    if not metrics:
        return {"message": "No risk metrics available yet", "metrics": []}
    
    return {
        "metrics": [
            {
                "date": m.date,
                "total_return": m.total_return,
                "annualized_return": m.annualized_return,
                "sharpe_ratio": m.sharpe_ratio,
                "sortino_ratio": m.sortino_ratio,
                "max_drawdown": m.max_drawdown,
                "current_drawdown": m.current_drawdown,
                "volatility": m.volatility,
                "var_95": m.var_95,
                "var_99": m.var_99,
                "beta_sp500": m.beta_sp500,
                "correlation_sp500": m.correlation_sp500
            }
            for m in metrics
        ]
    }

@router.post("/rebalance")
def trigger_rebalance(
    force: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Trigger a rebalancing of the index."""
    config = db.query(StrategyConfig).first()
    if not config:
        raise HTTPException(status_code=404, detail="Strategy configuration not found")
    
    # Set force rebalance flag
    if force:
        config.force_rebalance = True
        db.commit()
    
    try:
        refresh_all(db, smart_mode=True)
        return {"message": "Rebalancing completed successfully"}
    except Exception as e:
        logger.error(f"Rebalancing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Rebalancing failed: {str(e)}")
    finally:
        # Reset force flag
        if force:
            config.force_rebalance = False
            db.commit()