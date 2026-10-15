from pydantic_settings import BaseSettings
from typing import List
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
BACKEND_ENV = os.path.join(BACKEND_DIR, ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "TruthWire API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./truthwire.db"
    ENVIRONMENT: str = "development"
    PILOT_COUNTRIES: str = "NP,US,CA"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "*"]
    
    @property
    def resolved_database_url(self) -> str:
        # If relative sqlite, always anchor to backend/ directory
        if self.DATABASE_URL.startswith("sqlite:///./"):
            rel_name = self.DATABASE_URL.replace("sqlite:///./", "")
            abs_db = os.path.join(BACKEND_DIR, rel_name).replace("\\", "/")
            return f"sqlite:///{abs_db}"
        return self.DATABASE_URL

    class Config:
        env_file = (BACKEND_ENV, ".env")
        extra = "allow"

settings = Settings()
