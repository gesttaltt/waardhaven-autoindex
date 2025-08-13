import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    DATABASE_URL: str
    
    # Port configuration for Render
    PORT: int = Field(default=10000, env="PORT")

    ADMIN_TOKEN: str = ""
    DAILY_DROP_THRESHOLD: float = -0.01

    ASSET_DEFAULT_START: str = "2018-01-01"
    SP500_TICKER: str = "^GSPC"

    class Config:
        env_file = ".env"

settings = Settings()
