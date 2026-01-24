"""
Configuration settings for oh-my-astock backend
"""

import os
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseModel):
    """Application settings"""

    # Environment
    env: str = os.getenv("ENV", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Server
    port: int = int(os.getenv("PORT", "8000"))

    # Database
    database_path: str = os.getenv("DATABASE_PATH", "../data/stocks.duckdb")

    # CORS - parsed manually
    cors_origins_string: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://localhost:4142")

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from the string"""
        return [origin.strip() for origin in self.cors_origins_string.split(',') if origin.strip()]


settings = Settings()