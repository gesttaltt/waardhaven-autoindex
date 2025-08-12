from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Date, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    sector = Column(String, nullable=True)

class Price(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    close = Column(Float, nullable=False)
    __table_args__ = (UniqueConstraint('asset_id', 'date', name='_asset_date_uc'),)

class IndexValue(Base):
    __tablename__ = "index_values"
    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, index=True, nullable=False)
    value = Column(Float, nullable=False)  # base = 100

class Allocation(Base):
    __tablename__ = "allocations"
    id = Column(Integer, primary_key=True)
    date = Column(Date, index=True, nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True, nullable=False)
    weight = Column(Float, nullable=False)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    asset_symbol = Column(String, nullable=False)
    type = Column(String, nullable=False)  # "BUY" / "SELL"
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, nullable=True)
