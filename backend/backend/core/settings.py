from pathlib import Path
from typing import Any
from pydantic import model_validator
from pydantic_settings import BaseSettings

from backend.core.logging import setup_logging

log = setup_logging("backend.llm_service")

class Settings(BaseSettings):
    
    # Configurações da API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Data Processor - Cleaning CSV Data with LLM"
    
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    UPLOAD_DIR: str = "uploads"
    PROCESSED_DIR: str = "processed"

    OPENAI_SECRET_KEY: str
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.1
    
    GEMINI_SECRET_KEY: str
    GEMINI_BASE_MODEL: str = "gemini-2.5-flash"
    GEMINI_MAX_TOKENS: int = 2000
    GEMINI_TEMPERATURE: float = 0.1
    
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_EXTENSIONS: set[str] = {".csv"}
    
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # execução de código
    EXECUTION_TIMEOUT: int = 30  # segundos
    MAX_SCRIPT_LENGTH: int = 10000  # caracteres



    @model_validator(mode='after')
    def setup_directories(self) -> 'Settings':
        log.info(f"Setting directories on base dir: {self.BASE_DIR}")
        self.UPLOAD_DIR = self.BASE_DIR / "upload"
        self.PROCESSED_DIR = self.BASE_DIR / "processed"
        
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        log.info(f"Base settings done")
        
        return self



    class Config:
        env_file = ".env"
        case_sensitive = True


# Instância global das configurações
settings = Settings()