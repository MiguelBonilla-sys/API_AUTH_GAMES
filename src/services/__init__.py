"""
Módulo de servicios para el gateway de autenticación.
Contiene servicios auxiliares como proxy y utilidades.
"""

from .proxy_service import ProxyService, proxy_service, get_proxy_service

__all__ = [
    "ProxyService",
    "proxy_service", 
    "get_proxy_service"
]

