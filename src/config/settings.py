from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Database
    database_url: str = Field(..., description="PostgreSQL database URL")
    database_min_connections: int = Field(default=5, description="Minimum database connections")
    database_max_connections: int = Field(default=20, description="Maximum database connections")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379", description="Redis URL for caching")
    
    # ChatGroq API
    groq_api_key: str = Field(..., description="ChatGroq API key")
    groq_model: str = Field(default="llama3-70b-8192", description="ChatGroq model to use")
    groq_max_retries: int = Field(default=3, description="Max retries for ChatGroq API")
    groq_timeout: int = Field(default=60, description="Timeout for ChatGroq API calls")
    
    # Security
    secret_key: str = Field(..., description="Secret key for JWT tokens")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration")
    
    # Application
    app_name: str = Field(default="EA Code Evolution Platform", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    host: str = Field(default="0.0.0.0", description="Host to bind to")
    port: int = Field(default=8000, description="Port to bind to")
    
    # Evolution
    max_evolution_iterations: int = Field(default=10, description="Maximum evolution iterations")
    default_population_size: int = Field(default=50, description="Default DEAP population size")
    max_context_tokens: int = Field(default=4000, description="Maximum context tokens for LLM")
    
    # Chat
    max_chat_history: int = Field(default=100, description="Maximum chat messages to retain")
    context_compression_threshold: int = Field(default=80, description="When to compress context (% of max)")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()