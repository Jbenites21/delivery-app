from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación usando variables de entorno"""
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # Aplicación
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = True
    
    # Seguridad
    secret_key: str = "default-secret-key-change-in-production"
    token_expire_hours: int = 24
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()
