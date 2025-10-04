import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_tutor.db")
    
    # Application Configuration
    APP_NAME = os.getenv("APP_NAME", "AI Tutor Orchestrator")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # Educational Tools Configuration
    NOTE_MAKER_URL = os.getenv("NOTE_MAKER_URL", "http://localhost:8001")
    FLASHCARD_GENERATOR_URL = os.getenv("FLASHCARD_GENERATOR_URL", "http://localhost:8002")
    CONCEPT_EXPLAINER_URL = os.getenv("CONCEPT_EXPLAINER_URL", "http://localhost:8003")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
