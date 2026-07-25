"""
Arbiter AI — Configuration Module
Loads environment variables and provides app-wide configuration.
"""

import os
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
load_dotenv()  # Also try local .env

class Settings:
    """Application settings loaded from environment variables."""
    
    # AI Providers
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    XAI_API_KEY: str = os.getenv("XAI_API_KEY", "")
    
    # Models
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    XAI_MODEL: str = os.getenv("XAI_MODEL", "grok-beta")
    
    # Server
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "5173"))
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", os.path.join(
        os.path.dirname(__file__), "arbiter.db"
    ))
    
    # Pipeline Settings
    MAX_CLAIMS_PER_QUERY: int = int(os.getenv("MAX_CLAIMS_PER_QUERY", "15"))
    MAX_SOURCES_PER_CLAIM: int = int(os.getenv("MAX_SOURCES_PER_CLAIM", "5"))
    AGENT_TIMEOUT_SECONDS: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "120"))
    DEBATE_ROUNDS: int = int(os.getenv("DEBATE_ROUNDS", "2"))
    
    # Feature Flags
    ENABLE_MULTI_MODEL: bool = os.getenv("ENABLE_MULTI_MODEL", "true").lower() == "true"
    ENABLE_DEBATE_ARENA: bool = os.getenv("ENABLE_DEBATE_ARENA", "true").lower() == "true"
    ENABLE_CLAIM_DNA: bool = os.getenv("ENABLE_CLAIM_DNA", "true").lower() == "true"
    
    # Confidence Decay
    CONFIDENCE_DECAY_RATE: float = float(os.getenv("CONFIDENCE_DECAY_RATE", "0.01"))
    RECENCY_BOOST_DAYS: int = int(os.getenv("RECENCY_BOOST_DAYS", "30"))
    STALENESS_PENALTY_DAYS: int = int(os.getenv("STALENESS_PENALTY_DAYS", "365"))
    
    # Rate Limiting
    GEMINI_RPM: int = int(os.getenv("GEMINI_RPM", "15"))
    GROQ_RPM: int = int(os.getenv("GROQ_RPM", "30"))
    SEARCH_DELAY_SECONDS: float = float(os.getenv("SEARCH_DELAY_SECONDS", "1.0"))
    
    @property
    def has_gemini(self) -> bool:
        return bool(self.GEMINI_API_KEY)
    
    @property
    def has_groq(self) -> bool:
        return bool(self.GROQ_API_KEY)
    
    @property
    def available_providers(self) -> list:
        providers = []
        if self.has_gemini:
            providers.append("gemini")
        if self.has_groq:
            providers.append("groq")
        return providers


settings = Settings()
