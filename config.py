"""Configuration management for PhysioSOAP MVP."""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model_gpt: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL_GPT")
    openai_model_whisper: str = Field(default="whisper-1", env="OPENAI_MODEL_WHISPER")
    max_tokens: int = Field(default=2048, env="MAX_TOKENS")
    
    # Directory Configuration
    pdf_output_dir: Path = Field(default=Path("./output"), env="PDF_OUTPUT_DIR")
    audio_input_dir: Path = Field(default=Path("./audio"), env="AUDIO_INPUT_DIR")
    
    # HIPAA Configuration
    hipaa_mode: bool = Field(default=True, env="HIPAA_MODE")
    
    # MCP Server Configuration
    transcribe_server_port: int = Field(default=8001, env="TRANSCRIBE_SERVER_PORT")
    extract_server_port: int = Field(default=8002, env="EXTRACT_SERVER_PORT")
    render_server_port: int = Field(default=8003, env="RENDER_SERVER_PORT")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    class Config:
        env_file = ".env"
        

    def __post_init__(self):
        """Create necessary directories if they don't exist."""
        self.pdf_output_dir.mkdir(parents=True, exist_ok=True)
        self.audio_input_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings() 