"""
Trading and order execution models.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from datetime import datetime
from ..core.database import Base


class Order(Base):
    """Trading order model."""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    asset_symbol = Column(String, nullable=False)
    type = Column(String, nullable=False)  # "BUY" / "SELL"
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<Order(id={self.id}, symbol='{self.asset_symbol}', type='{self.type}', amount={self.amount})>"