import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    SECRET_KEY: str = Field(..., env="SECRET_KEY")  # Required in production
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    DATABASE_URL: str = Field(..., env="DATABASE_URL")  # Required in production
    
    # Port configuration for Render
    PORT: int = Field(default=10000, env="PORT")

    ADMIN_TOKEN: str = ""
    DAILY_DROP_THRESHOLD: float = -0.01

    ASSET_DEFAULT_START: str = "2018-01-01"
    SP500_TICKER: str = "^GSPC"
    
    # TwelveData API configuration
    TWELVEDATA_API_KEY: str = Field(default="", env="TWELVEDATA_API_KEY")
    TWELVEDATA_PLAN: str = Field(default="free", env="TWELVEDATA_PLAN")  # free, grow, pro, etc.
    TWELVEDATA_RATE_LIMIT: int = Field(default=8, env="TWELVEDATA_RATE_LIMIT")  # Credits per minute
    ENABLE_MARKET_DATA_CACHE: bool = Field(default=True, env="ENABLE_MARKET_DATA_CACHE")
    REFRESH_MODE: str = Field(default="auto", env="REFRESH_MODE")  # auto, full, minimal, cached

    class Config:
        env_file = ".env"

settings = Settings()
