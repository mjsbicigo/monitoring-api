import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    API_KEY: str = "default-insecure-key" 
    MONGODB_URIS: Optional[str] = None
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

# Security warning for default API key
if settings.API_KEY == "default-insecure-key":
    logging.warning("\nWARNING: Running with default API_KEY. Please set the API_KEY environment variable for production environments!")
    
if not settings.MONGODB_URIS:
    logging.info("\nINFO: MONGODB_URIS not set. Mongo health checks will return disabled status.")