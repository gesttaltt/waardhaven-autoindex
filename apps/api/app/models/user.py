"""
User authentication and authorization models.
"""
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from ..core.database import Base


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(email='{self.email}')>"