"""
Módulo de routers para el gateway de autenticación.
Contiene todos los endpoints de la API.
"""

from .auth import router as auth_router
from .admin import router as admin_router

__all__ = ["auth_router", "admin_router"]
