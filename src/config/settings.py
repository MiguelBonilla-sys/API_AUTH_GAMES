"""
Configuración de la aplicación usando Pydantic Settings.
Maneja variables de entorno y configuraciones por defecto.
"""

import os
from typing import List, Optional, Union, Any
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Constantes para configuración por defecto
DEFAULT_CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8000"]


class Settings(BaseSettings):
    """
    Configuración de la aplicación.
    """
    
    # Configuración de la aplicación
    app_name: str = Field(default="API Auth Gateway", description="Nombre de la aplicación")
    app_version: str = Field(default="1.0.0", description="Versión de la aplicación")
    environment: str = Field(default="development", description="Entorno de ejecución")
    debug: bool = Field(default=False, description="Modo debug")
    
    # Configuración de base de datos
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:UZztcpwvymcUOjHbKLiHJCezPAmkpTON@metro.proxy.rlwy.net:43514/railway",
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
    cors_origins: str = Field(
        default=",".join(DEFAULT_CORS_ORIGINS),
        description="Orígenes permitidos para CORS"
    )
    
    # Configuración de logging
    log_level: str = Field(default="INFO", description="Nivel de logging")
    
    # Configuración de bcrypt
    bcrypt_rounds: int = Field(default=12, description="Rounds de bcrypt para hash de contraseñas")
    
    # Configuración de rate limiting
    rate_limit_requests: int = Field(default=100, description="Número de requests por minuto")
    rate_limit_window: int = Field(default=60, description="Ventana de tiempo para rate limiting en segundos")
    
    # Configuración de Keycloak
    keycloak_server_url: str = Field(
        default="https://keycloak-production-a4e7.up.railway.app",
        description="URL del servidor Keycloak"
    )
    keycloak_realm: str = Field(
        default="master",
        description="Realm de Keycloak"
    )
    keycloak_client_id: str = Field(
        default="api-gateway-2fa-service",
        description="Client ID de Keycloak"
    )
    keycloak_client_secret: str = Field(
        default="",
        description="Client Secret de Keycloak"
    )
    
    # Configuración 2FA
    two_factor_secret_key: str = Field(
        default="",
        description="Secret para tokens temporales de 2FA"
    )
    two_factor_token_expiry_minutes: int = Field(
        default=10,
        description="Expiración de token temporal 2FA en minutos"
    )
    two_factor_max_attempts: int = Field(
        default=5,
        description="Máximo de intentos fallidos de OTP"
    )
    
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
    
    @validator('two_factor_secret_key')
    def validate_two_factor_secret(cls, v):
        """Validar secret para tokens 2FA."""
        if v and len(v) < 32:
            raise ValueError('Two factor secret key must be at least 32 characters long')
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
        extra = "ignore"  # Ignorar campos extra en lugar de rechazarlos
        
    @property
    def cors_origins_list(self) -> List[str]:
        """Obtener la lista de orígenes CORS."""
        if isinstance(self.cors_origins, str):
            if not self.cors_origins.strip():
                return DEFAULT_CORS_ORIGINS
            origins = [origin.strip() for origin in self.cors_origins.split(',') if origin.strip()]
            return origins if origins else DEFAULT_CORS_ORIGINS
        return DEFAULT_CORS_ORIGINS


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
