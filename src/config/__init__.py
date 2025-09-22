"""
Módulo de configuración para el gateway de autenticación.
Contiene configuración de base de datos, settings y utilidades.
"""

from .database import (
    Base,
    engine,
    AsyncSessionLocal,
    get_db,
    init_db,
    close_db
)

from .settings_complete import (
    Settings,
    settings,
    get_settings,
    is_development,
    is_production,
    get_database_url,
    get_flask_api_url,
    get_jwt_settings,
    get_cors_settings,
    get_server_config
)

__all__ = [
    # Database
    "Base",
    "engine", 
    "AsyncSessionLocal",
    "get_db",
    "init_db",
    "close_db",
    
    # Settings
    "Settings",
    "settings",
    "get_settings",
    "is_development",
    "is_production",
    "get_database_url",
    "get_flask_api_url",
    "get_jwt_settings",
    "get_cors_settings",
    "get_server_config"
]
