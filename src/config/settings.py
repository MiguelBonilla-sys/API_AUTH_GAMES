"""
Configuración de la aplicación usando Pydantic Settings.
Maneja variables de entorno y configuraciones por defecto.
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """
    Configuración de la aplicación.
    """
    
    # Configuración de la aplicación
    app_name: str = Field(default="API Auth Gateway", description="Nombre de la aplicación")
    app_version: str = Field(default="1.0.0", description="Versión de la aplicación")
    environment: str = Field(default="development", description="Entorno de ejecución")
    debug: bool = Field(default=True, description="Modo debug")
    
    # Configuración de base de datos
    database_url: str = Field(
        default="postgresql+psycopg://user:password@localhost:5432/api_auth_games",
        description="URL de conexión a PostgreSQL"
    )
    
    # Configuración JWT
    jwt_secret_key: str = Field(
        default="your-super-secret-jwt-key-change-in-production-2024",
        description="Clave secreta para firmar tokens JWT"
    )
    jwt_algorithm: str = Field(default="HS256", description="Algoritmo JWT")
    jwt_access_token_expire_minutes: int = Field(
        default=30, 
        description="Tiempo de expiración del token de acceso en minutos"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7,
        description="Tiempo de expiración del token de renovación en días"
    )
    
    # Configuración de la API Flask
    flask_api_url: str = Field(
        default="https://flaskapi-production-a966.up.railway.app",
        description="URL de la API Flask existente"
    )
    
    # Configuración de CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Orígenes permitidos para CORS"
    )
    
    # Configuración de logging
    log_level: str = Field(default="INFO", description="Nivel de logging")
    
    # Configuración de bcrypt
    bcrypt_rounds: int = Field(default=12, description="Rounds de bcrypt para hash de contraseñas")
    
    # Configuración de rate limiting
    rate_limit_requests: int = Field(default=100, description="Número de requests por minuto")
    rate_limit_window: int = Field(default=60, description="Ventana de tiempo para rate limiting en segundos")
    
    @validator('environment')
    def validate_environment(cls, v):
        """Validar entorno de ejecución."""
        allowed_environments = ['development', 'staging', 'production']
        if v not in allowed_environments:
            raise ValueError(f'Environment must be one of: {", ".join(allowed_environments)}')
        return v
    
    @validator('jwt_secret_key')
    def validate_jwt_secret(cls, v):
        """Validar clave secreta JWT."""
        if len(v) < 32:
            raise ValueError('JWT secret key must be at least 32 characters long')
        return v
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        """Parsear orígenes CORS desde string separado por comas."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validar nivel de logging."""
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed_levels:
            raise ValueError(f'Log level must be one of: {", ".join(allowed_levels)}')
        return v.upper()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()


def get_settings() -> Settings:
    """
    Obtener instancia de configuración.
    
    Returns:
        Configuración de la aplicación
    """
    return settings


def is_development() -> bool:
    """
    Verificar si estamos en entorno de desarrollo.
    
    Returns:
        True si es desarrollo, False en caso contrario
    """
    return settings.environment == "development"


def is_production() -> bool:
    """
    Verificar si estamos en entorno de producción.
    
    Returns:
        True si es producción, False en caso contrario
    """
    return settings.environment == "production"


def get_database_url() -> str:
    """
    Obtener URL de base de datos.
    
    Returns:
        URL de conexión a la base de datos
    """
    return settings.database_url


def get_jwt_secret() -> str:
    """
    Obtener clave secreta JWT.
    
    Returns:
        Clave secreta para firmar tokens JWT
    """
    return settings.jwt_secret_key


def get_flask_api_url() -> str:
    """
    Obtener URL de la API Flask.
    
    Returns:
        URL de la API Flask existente
    """
    return settings.flask_api_url
