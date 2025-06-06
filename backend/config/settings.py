"""
Configuration Settings for AI Data Analyst v0.1 Backend
"""

import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Server settings
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False
    
    # OpenAI settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    
    # Canvas settings
    default_canvas_width: int = 800
    default_canvas_height: int = 600
    
    # Chatbot settings
    max_conversation_history: int = 20
    max_function_calls_per_turn: int = 5
    function_call_timeout: int = 30
    
    # WebSocket settings
    websocket_ping_interval: int = 30
    websocket_ping_timeout: int = 10
    
    # CORS settings
    cors_origins: list = ["*"]
    cors_allow_credentials: bool = True
    
    # Logging settings
    log_level: str = "info"
    
    class Config:
        env_file = ".env"
        env_prefix = "AI_DATA_ANALYST_"


# Global settings instance
settings = Settings() 