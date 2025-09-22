"""
Configuración completa de la aplicación usando Pydantic Settings.
Maneja todas las variables de entorno y configuraciones por defecto.
"""

import os
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuración completa de la aplicación.
    Maneja todas las variables de entorno y configuraciones por defecto.
    """
    
    # ==========================================
    # CONFIGURACIÓN GENERAL DE LA APLICACIÓN
    # ==========================================
    app_name: str = Field(default="API Auth Gateway", description="Nombre de la aplicación")
    app_version: str = Field(default="1.0.0", description="Versión de la aplicación")
    environment: str = Field(default="development", description="Entorno de ejecución")
    debug: bool = Field(default=True, description="Modo debug")
    timezone: str = Field(default="UTC", description="Timezone de la aplicación")
    default_language: str = Field(default="es", description="Idioma por defecto")
    
    # ==========================================
    # CONFIGURACIÓN DE BASE DE DATOS
    # ==========================================
    database_url: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/api_auth_games"),
        description="URL de conexión a PostgreSQL"
    )
    
    # ==========================================
    # CONFIGURACIÓN JWT
    # ==========================================
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
    
    # ==========================================
    # CONFIGURACIÓN DE API FLASK EXTERNA
    # ==========================================
    flask_api_url: str = Field(
        default="https://flaskapi-production-a966.up.railway.app",
        description="URL de la API Flask existente"
    )
    
    # ==========================================
    # CONFIGURACIÓN DE CORS
    # ==========================================
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000",
        description="Orígenes permitidos para CORS"
    )
    cors_allow_credentials: bool = Field(default=True, description="Permitir credenciales en CORS")
    cors_allow_methods: str = Field(
        default="GET,POST,PUT,DELETE,OPTIONS",
        description="Métodos HTTP permitidos"
    )
    cors_allow_headers: str = Field(default="*", description="Headers permitidos")
    
    # ==========================================
    # CONFIGURACIÓN DE LOGGING
    # ==========================================
    log_level: str = Field(default="INFO", description="Nivel de logging")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Formato de logs"
    )
    
    # ==========================================
    # CONFIGURACIÓN DE SEGURIDAD
    # ==========================================
    bcrypt_rounds: int = Field(default=12, description="Rounds de hashing para bcrypt")
    rate_limit_per_minute: int = Field(default=60, description="Rate limiting por minuto")
    http_timeout: int = Field(default=30, description="Timeout para requests HTTP")
    max_request_size: int = Field(default=10485760, description="Tamaño máximo de request body")
    
    # ==========================================
    # CONFIGURACIÓN DE SERVIDOR
    # ==========================================
    host: str = Field(default="0.0.0.0", description="Host del servidor")
    port: int = Field(default_factory=lambda: int(os.getenv("PORT", 8000)), description="Puerto del servidor")
    workers: int = Field(default=4, description="Número de workers para producción")
    
    # ==========================================
    # CONFIGURACIÓN DE MONITOREO
    # ==========================================
    enable_metrics: bool = Field(default=False, description="Habilitar métricas de Prometheus")
    enable_health_checks: bool = Field(default=True, description="Habilitar health checks avanzados")
    
    # ==========================================
    # VARIABLES DE DESARROLLO
    # ==========================================
    reload: bool = Field(default=True, description="Recargar automáticamente en desarrollo")
    show_docs: bool = Field(default=True, description="Mostrar documentación automática")
    
    # ==========================================
    # VALIDADORES
    # ==========================================
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
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validar nivel de logging."""
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed_levels:
            raise ValueError(f'Log level must be one of: {", ".join(allowed_levels)}')
        return v.upper()
    
    @validator('bcrypt_rounds')
    def validate_bcrypt_rounds(cls, v):
        """Validar rounds de bcrypt."""
        if v < 10:
            raise ValueError('Bcrypt rounds must be at least 10 for security')
        if v > 15:
            raise ValueError('Bcrypt rounds should not exceed 15 for performance')
        return v
    
    @validator('port')
    def validate_port(cls, v):
        """Validar puerto del servidor."""
        if v < 1 or v > 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    @validator('workers')
    def validate_workers(cls, v):
        """Validar número de workers."""
        if v < 1:
            raise ValueError('Workers must be at least 1')
        return v
    
    @validator('rate_limit_per_minute')
    def validate_rate_limit(cls, v):
        """Validar rate limit."""
        if v < 1:
            raise ValueError('Rate limit must be at least 1 request per minute')
        return v
    
    @validator('http_timeout')
    def validate_http_timeout(cls, v):
        """Validar timeout HTTP."""
        if v < 1:
            raise ValueError('HTTP timeout must be at least 1 second')
        return v
    
    @validator('max_request_size')
    def validate_max_request_size(cls, v):
        """Validar tamaño máximo de request."""
        if v < 1024:  # 1KB mínimo
            raise ValueError('Max request size must be at least 1024 bytes')
        return v
    
    # ==========================================
    # PROPIEDADES CALCULADAS
    # ==========================================
    @property
    def is_development(self) -> bool:
        """Verificar si está en modo desarrollo."""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Verificar si está en modo producción."""
        return self.environment == "production"
    
    @property
    def is_staging(self) -> bool:
        """Verificar si está en modo staging."""
        return self.environment == "staging"
    
    @property
    def database_url_sync(self) -> str:
        """URL de base de datos síncrona (para migraciones)."""
        return self.database_url.replace("+asyncpg", "")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Lista de orígenes CORS."""
        if isinstance(self.cors_origins, str):
            if not self.cors_origins.strip():
                return ["http://localhost:3000", "http://localhost:8000"]
            return [origin.strip() for origin in self.cors_origins.split(',') if origin.strip()]
        return []
        
    @property
    def cors_allow_methods_list(self) -> List[str]:
        """Lista de métodos CORS permitidos."""
        if isinstance(self.cors_allow_methods, str):
            if not self.cors_allow_methods.strip():
                return ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
            return [method.strip().upper() for method in self.cors_allow_methods.split(',') if method.strip()]
        return []
        
    @property
    def cors_allow_headers_list(self) -> List[str]:
        """Lista de headers CORS permitidos."""
        if isinstance(self.cors_allow_headers, str):
            if self.cors_allow_headers.strip() == "*":
                return ["*"]
            if not self.cors_allow_headers.strip():
                return ["*"]
            return [header.strip() for header in self.cors_allow_headers.split(',') if header.strip()]
        return ["*"]
    
    # ==========================================
    # CONFIGURACIÓN DE PYDANTIC
    # ==========================================
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignorar campos extra en lugar de rechazarlos
        validate_assignment = True  # Validar al asignar valores


# ==========================================
# INSTANCIA GLOBAL Y FUNCIONES DE UTILIDAD
# ==========================================

# Instancia global de configuración
settings = Settings()


def get_settings() -> Settings:
    """
    Obtener instancia de configuración.
    
    Returns:
        Instancia de configuración global
    """
    return settings


def get_database_url() -> str:
    """
    Obtener URL de base de datos.
    
    Returns:
        URL de conexión a la base de datos
    """
    return settings.database_url


def get_flask_api_url() -> str:
    """
    Obtener URL de la API Flask.
    
    Returns:
        URL de la API Flask externa
    """
    return settings.flask_api_url


def get_jwt_settings() -> dict:
    """
    Obtener configuración JWT.
    
    Returns:
        Diccionario con configuración JWT
    """
    return {
        "secret_key": settings.jwt_secret_key,
        "algorithm": settings.jwt_algorithm,
        "access_token_expire_minutes": settings.jwt_access_token_expire_minutes,
        "refresh_token_expire_days": settings.jwt_refresh_token_expire_days,
    }


def get_cors_settings() -> dict:
    """
    Obtener configuración CORS.
    
    Returns:
        Diccionario con configuración CORS
    """
    return {
        "allow_origins": settings.cors_origins_list,
        "allow_credentials": settings.cors_allow_credentials,
        "allow_methods": settings.cors_allow_methods_list,
        "allow_headers": settings.cors_allow_headers_list,
    }


def is_production() -> bool:
    """
    Verificar si está en modo producción.
    
    Returns:
        True si está en producción
    """
    return settings.is_production


def is_development() -> bool:
    """
    Verificar si está en modo desarrollo.
    
    Returns:
        True si está en desarrollo
    """
    return settings.is_development


def get_server_config() -> dict:
    """
    Obtener configuración del servidor.
    
    Returns:
        Diccionario con configuración del servidor
    """
    return {
        "host": settings.host,
        "port": settings.port,
        "workers": settings.workers,
        "reload": settings.reload and settings.is_development,
        "debug": settings.debug and settings.is_development,
    }

