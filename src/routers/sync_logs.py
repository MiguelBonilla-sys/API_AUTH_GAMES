"""
Proxy router para logs de sincronización.
Reenvía requests autenticados a la API Flask existente.
Solo accesible para administradores, editores y superadministradores.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path

from src.auth import (
    CurrentUser,
    has_permission,
    Permissions
)
from src.services import get_proxy_service, ProxyService

# Configurar router
router = APIRouter(prefix="/api/sync-logs", tags=["sync-logs"])

# Constantes para mensajes de error
NO_PERMISSION_SYNC_LOGS_MESSAGE = "No tienes permisos para acceder a los logs de sincronización"
SYNC_LOG_ID_DESCRIPTION = "ID del log de sincronización"


def check_sync_log_permission(current_user: CurrentUser):
    """
    Verificar que el usuario tenga permisos para acceder a SyncLog.
    Solo admin, editor y superadmin pueden acceder.
    """
    # Verificar si es admin/editor/superadmin
    if not current_user.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=NO_PERMISSION_SYNC_LOGS_MESSAGE
        )
    
    role_name = current_user.role.name
    if role_name not in ["editor", "superadmin"]:
        # Desarrolladoras no tienen acceso a SyncLog
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=NO_PERMISSION_SYNC_LOGS_MESSAGE
        )


@router.get(
    "/",
    summary="Listar logs de sincronización",
    description="""Obtiene una lista paginada de todos los logs de sincronización con filtros opcionales.
    
    **Filtros disponibles:**
    - `page`: Número de página (default: 1, mínimo: 1)
    - `per_page`: Elementos por página (default: 10, mínimo: 1, máximo: 100)
    - `status`: Filtrar por estado (pending, success, failed)
    - `api_source`: Filtrar por fuente de API (rawg, steam, igdb)
    
    **Acceso:** Solo administradores, editores y superadministradores.
    """,
    responses={
        200: {
            "description": "Logs obtenidos exitosamente",
        },
        403: {
            "description": "No tienes permisos para acceder a los logs de sincronización",
        },
        500: {
            "description": "Error interno del servidor",
        }
    }
)
async def list_sync_logs(
    current_user: CurrentUser,
    page: Optional[int] = Query(default=1, ge=1, description="Número de página", example=1),
    per_page: Optional[int] = Query(default=10, ge=1, le=100, description="Elementos por página", example=10),
    status: Optional[str] = Query(default=None, description="Filtrar por estado", example="success"),
    api_source: Optional[str] = Query(default=None, description="Filtrar por fuente de API", example="rawg"),
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Listar logs de sincronización con paginación y filtros.
    Solo accesible para administradores, editores y superadministradores.
    """
    try:
        # Verificar permisos
        check_sync_log_permission(current_user)
        
        # Preparar parámetros
        params = {
            "page": page,
            "per_page": per_page
        }
        
        if status:
            params["status"] = status
        if api_source:
            params["api_source"] = api_source
        
        # Reenviar request a la API Flask
        return await proxy_service.get(
            endpoint="api/sync-logs",
            params=params,
            user_email=current_user.email
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/recent",
    summary="Obtener logs recientes",
    description="""Obtiene los logs de sincronización más recientes.
    
    **Parámetros:**
    - `limit`: Número máximo de logs (default: 50, mínimo: 1, máximo: 100)
    - `api_source`: Filtrar por fuente de API (rawg, steam, igdb)
    
    **Acceso:** Solo administradores, editores y superadministradores.
    """,
    responses={
        200: {
            "description": "Logs recientes obtenidos exitosamente",
        },
        403: {
            "description": "No tienes permisos para acceder a los logs de sincronización",
        },
        500: {
            "description": "Error interno del servidor",
        }
    }
)
async def get_recent_sync_logs(
    current_user: CurrentUser,
    limit: Optional[int] = Query(default=50, ge=1, le=100, description="Número máximo de logs", example=10),
    api_source: Optional[str] = Query(default=None, description="Filtrar por fuente de API", example="rawg"),
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Obtener logs de sincronización recientes.
    Solo accesible para administradores, editores y superadministradores.
    """
    try:
        # Verificar permisos
        check_sync_log_permission(current_user)
        
        # Preparar parámetros
        params = {
            "limit": limit
        }
        
        if api_source:
            params["api_source"] = api_source
        
        # Reenviar request a la API Flask
        return await proxy_service.get(
            endpoint="api/sync-logs/recent",
            params=params,
            user_email=current_user.email
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/statistics",
    summary="Estadísticas de sincronización",
    description="""Obtiene estadísticas agregadas de sincronizaciones.
    
    **Parámetros:**
    - `days`: Número de días a considerar (default: 7, mínimo: 1, máximo: 365)
    - `api_source`: Filtrar por fuente de API (rawg, steam, igdb)
    
    **Respuesta incluye:**
    - `total`: Total de sincronizaciones
    - `successful`: Sincronizaciones exitosas
    - `failed`: Sincronizaciones fallidas
    - `pending`: Sincronizaciones pendientes
    - `success_rate`: Tasa de éxito (porcentaje)
    
    **Acceso:** Solo administradores, editores y superadministradores.
    """,
    responses={
        200: {
            "description": "Estadísticas obtenidas exitosamente",
        },
        403: {
            "description": "No tienes permisos para acceder a los logs de sincronización",
        },
        500: {
            "description": "Error interno del servidor",
        }
    }
)
async def get_sync_statistics(
    current_user: CurrentUser,
    days: Optional[int] = Query(default=7, ge=1, le=365, description="Número de días a considerar", example=7),
    api_source: Optional[str] = Query(default=None, description="Filtrar por fuente de API", example="rawg"),
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Obtener estadísticas de sincronización.
    Solo accesible para administradores, editores y superadministradores.
    """
    try:
        # Verificar permisos
        check_sync_log_permission(current_user)
        
        # Preparar parámetros
        params = {
            "days": days
        }
        
        if api_source:
            params["api_source"] = api_source
        
        # Reenviar request a la API Flask
        return await proxy_service.get(
            endpoint="api/sync-logs/statistics",
            params=params,
            user_email=current_user.email
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/{sync_log_id}",
    summary="Obtener log por ID",
    description="""Obtiene un log de sincronización específico por su ID.
    
    **Parámetros:**
    - `sync_log_id`: ID del log de sincronización (entero positivo)
    
    **Acceso:** Solo administradores, editores y superadministradores.
    """,
    responses={
        200: {
            "description": "Log obtenido exitosamente",
        },
        403: {
            "description": "No tienes permisos para acceder a los logs de sincronización",
        },
        404: {
            "description": "Log de sincronización no encontrado",
        },
        500: {
            "description": "Error interno del servidor",
        }
    }
)
async def get_sync_log_by_id(
    current_user: CurrentUser,
    sync_log_id: int = Path(description=SYNC_LOG_ID_DESCRIPTION, example=1),
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Obtener log de sincronización por ID.
    Solo accesible para administradores, editores y superadministradores.
    """
    try:
        # Verificar permisos
        check_sync_log_permission(current_user)
        
        # Reenviar request a la API Flask
        return await proxy_service.get(
            endpoint=f"api/sync-logs/{sync_log_id}",
            user_email=current_user.email
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

