from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..core.database import get_db
from ..models import Order, User
from ..schemas import OrderRequest, OrderResponse
from ..utils.token_dep import get_current_user

router = APIRouter()

@router.post("/order", response_model=OrderResponse)
def place_order(req: OrderRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Mock: simply log an order for the entire index
    order = Order(user_id=user.id, asset_symbol="INDEX", type=req.type.upper(), amount=req.amount, details={"note": "Mock execution"})
    db.add(order)
    db.commit()
    db.refresh(order)
    return OrderResponse(id=order.id, created_at=order.created_at)
