from typing import List, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "sop-author-pharmaceutical-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Server Configuration
    BACKEND_PORT: int = 9000
    
    # Database - Using SQLite for development (no PostgreSQL installation required)
    DATABASE_URL: str = "sqlite:///./sop_author.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Ollama
    OLLAMA_HOST: str = "http://localhost:11434"  # Change this to your Google Colab ngrok URL
    OLLAMA_MODEL: str = "mistral:7b-instruct"  # Updated to match Colab setup
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    PDF_OUTPUT_DIR: str = "./pdfs"
    
    # FDA API Configuration
    FDA_API_BASE_URL: str = "https://api.fda.gov"
    FDA_API_KEY: Optional[str] = None
    
    # EPA CompTox API
    EPA_API_BASE_URL: str = "https://comptox.epa.gov/dashboard-api"
    
    # Hugging Face
    HUGGINGFACE_API_KEY: Optional[str] = None
    
    # Pharmaceutical Validation Settings
    MAX_SOP_LENGTH: int = 50000
    MIN_SOP_SECTIONS: int = 8
    REQUIRED_SECTIONS: List[str] = [
        "Purpose", "Scope", "Definitions", "Responsibilities", 
        "Materials", "Procedure", "Documentation", "References"
    ]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Security
    BCRYPT_ROUNDS: int = 12
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()