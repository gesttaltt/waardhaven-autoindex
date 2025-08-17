from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
import os

from .config import settings

# Connection pool configuration for production
pool_config = {}

if os.getenv("RENDER"):  # Production on Render
    pool_config = {
        "poolclass": QueuePool,
        "pool_size": 20,  # Number of connections to maintain in pool
        "max_overflow": 40,  # Maximum overflow connections
        "pool_timeout": 30,  # Timeout for getting connection from pool
        "pool_recycle": 3600,  # Recycle connections after 1 hour
        "pool_pre_ping": True,  # Test connections before using
    }
else:  # Local development
    pool_config = {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_pre_ping": True,
    }

# Create engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    **pool_config,
    echo=False,  # Set to True for SQL query debugging
    future=True  # Use SQLAlchemy 2.0 style
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
