"""
Proxy router para desarrolladoras.
Reenvía requests autenticados a la API Flask existente con restricciones por rol.
"""

from typing import Optional, Dict, Any, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.responses import JSONResponse

from src.auth import (
    CurrentUser,
    CurrentSuperadminUser,
    get_current_user,
    get_current_superadmin_user,
    has_permission,
    Permissions
)
from src.services import get_proxy_service, ProxyService

# Configurar router
router = APIRouter(prefix="/api/desarrolladoras", tags=["desarrolladoras"])

# Constantes para mensajes de error
NO_PERMISSION_DESARROLLADORAS_MESSAGE = "No tienes permisos para leer desarrolladoras"
DESARROLLADORA_ID_DESCRIPTION = "ID de la desarrolladora"


# ===== ENDPOINTS DE LECTURA (Admin y User) =====

@router.get(
    "/",
    summary="Listar desarrolladoras",
    description="Obtiene la lista de desarrolladoras con filtros opcionales"
)
async def list_desarrolladoras(
    current_user: CurrentUser,
    page: Optional[int] = Query(default=1, ge=1, description="Número de página"),
    per_page: Optional[int] = Query(default=10, ge=1, le=100, description="Elementos por página"),
    pais: Optional[str] = Query(default=None, description="Filtrar por país"),
    buscar: Optional[str] = Query(default=None, description="Búsqueda de texto"),
    ordenar: Optional[str] = Query(default="nombre", description="Campo para ordenar"),
    direccion: Optional[str] = Query(default="asc", description="Dirección de ordenamiento"),
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Listar desarrolladoras con filtros opcionales.
    Accesible para usuarios admin y user.
    """
    try:
        # Verificar permiso de lectura
        if not has_permission(current_user, Permissions.DESARROLLADORA_READ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=NO_PERMISSION_DESARROLLADORAS_MESSAGE
            )
        
        # Preparar parámetros
        params = {
            "page": page,
            "per_page": per_page
        }
        
        if pais:
            params["pais"] = pais
        if buscar:
            params["buscar"] = buscar
        if ordenar:
            params["ordenar"] = ordenar
        if direccion:
            params["direccion"] = direccion
        
        # Reenviar request a la API Flask
        return await proxy_service.get(
            endpoint="api/desarrolladoras",
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
    "/{desarrolladora_id}",
    summary="Obtener desarrolladora por ID",
    description="Obtiene los detalles de una desarrolladora específica"
)
async def get_desarrolladora(
    current_user: CurrentUser,
    desarrolladora_id: int = Path(description=DESARROLLADORA_ID_DESCRIPTION),
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Obtener desarrolladora por ID.
    Accesible para usuarios admin y user.
    """
    try:
        # Verificar permiso de lectura
        if not has_permission(current_user, Permissions.DESARROLLADORA_READ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=NO_PERMISSION_DESARROLLADORAS_MESSAGE
            )
        
        # Reenviar request a la API Flask
        return await proxy_service.get(
            endpoint=f"api/desarrolladoras/{desarrolladora_id}",
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
    "/paises/",
    summary="Listar países",
    description="Obtiene la lista de países de desarrolladoras"
)
async def list_paises(
    current_user: CurrentUser,
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Listar países de desarrolladoras.
    Accesible para usuarios admin y user.
    """
    try:
        # Verificar permiso de lectura
        if not has_permission(current_user, Permissions.DESARROLLADORA_READ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=NO_PERMISSION_DESARROLLADORAS_MESSAGE
            )
        
        # Reenviar request a la API Flask
        return await proxy_service.get(
            endpoint="/api/desarrolladoras/paises/",
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
    "/estadisticas/",
    summary="Estadísticas de desarrolladoras",
    description="Obtiene estadísticas de desarrolladoras"
)
async def get_estadisticas(
    current_user: CurrentUser,
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Obtener estadísticas de desarrolladoras.
    Accesible para usuarios admin y user.
    """
    try:
        # Verificar permiso de lectura
        if not has_permission(current_user, Permissions.DESARROLLADORA_READ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=NO_PERMISSION_DESARROLLADORAS_MESSAGE
            )
        
        # Reenviar request a la API Flask
        return await proxy_service.get(
            endpoint="/api/desarrolladoras/estadisticas/",
            user_email=current_user.email
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


# ===== ENDPOINTS DE ESCRITURA (Solo Admin) =====

@router.post(
    "/",
    summary="Crear desarrolladora",
    description="Crea una nueva desarrolladora (solo administradores)"
)
async def create_desarrolladora(
    desarrolladora_data: Dict[str, Any],
    current_user: CurrentUser,
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Crear nueva desarrolladora.
    Accesible para desarrolladoras, editores y superadministradores.
    """
    try:
        # Verificar permiso de creación
        if not has_permission(current_user, Permissions.DESARROLLADORA_CREATE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para crear desarrolladoras"
            )
        
        # Reenviar request a la API Flask
        return await proxy_service.post(
            endpoint="/api/desarrolladoras/",
            json_data=desarrolladora_data,
            user_email=current_user.email
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.put(
    "/{desarrolladora_id}",
    summary="Actualizar desarrolladora",
    description="Actualiza una desarrolladora existente (solo administradores)"
)
async def update_desarrolladora(
    current_user: CurrentUser,
    desarrolladora_id: int = Path(description=DESARROLLADORA_ID_DESCRIPTION),
    desarrolladora_data: Dict[str, Any] = None,
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Actualizar desarrolladora existente.
    Accesible para desarrolladoras (solo propia), editores y superadministradores.
    """
    try:
        # Verificar permiso de actualización
        if not has_permission(current_user, Permissions.DESARROLLADORA_UPDATE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para actualizar desarrolladoras"
            )
        
        # Reenviar request a la API Flask
        return await proxy_service.put(
            endpoint=f"/api/desarrolladoras/{desarrolladora_id}",
            json_data=desarrolladora_data,
            user_email=current_user.email
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.delete(
    "/{desarrolladora_id}",
    summary="Eliminar desarrolladora",
    description="Elimina una desarrolladora (solo administradores)"
)
async def delete_desarrolladora(
    current_user: CurrentUser,
    desarrolladora_id: int = Path(description=DESARROLLADORA_ID_DESCRIPTION),
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Eliminar desarrolladora.
    Accesible para desarrolladoras (solo propia), editores y superadministradores.
    """
    try:
        # Verificar permiso de eliminación
        if not has_permission(current_user, Permissions.DESARROLLADORA_DELETE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para eliminar desarrolladoras"
            )
        
        # Reenviar request a la API Flask
        return await proxy_service.delete(
            endpoint=f"/api/desarrolladoras/{desarrolladora_id}",
            user_email=current_user.email
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


# ===== ENDPOINTS DE BÚSQUEDA AVANZADA (Admin y User) =====

@router.get(
    "/buscar/",
    summary="Búsqueda avanzada",
    description="Búsqueda avanzada de desarrolladoras con múltiples criterios"
)
async def buscar_desarrolladoras(
    current_user: CurrentUser,
    nombre: Optional[str] = Query(default=None, description="Nombre de la desarrolladora"),
    pais: Optional[str] = Query(default=None, description="País"),
    fundacion_desde: Optional[int] = Query(default=None, ge=1800, description="Año de fundación desde"),
    fundacion_hasta: Optional[int] = Query(default=None, ge=1800, description="Año de fundación hasta"),
    empleados_min: Optional[int] = Query(default=None, ge=0, description="Número mínimo de empleados"),
    empleados_max: Optional[int] = Query(default=None, ge=0, description="Número máximo de empleados"),
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Búsqueda avanzada de desarrolladoras.
    Accesible para usuarios admin y user.
    """
    try:
        # Verificar permiso de lectura
        if not has_permission(current_user, Permissions.DESARROLLADORA_READ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=NO_PERMISSION_DESARROLLADORAS_MESSAGE
            )
        
        # Preparar parámetros
        params = {}
        
        if nombre:
            params["nombre"] = nombre
        if pais:
            params["pais"] = pais
        if fundacion_desde is not None:
            params["fundacion_desde"] = fundacion_desde
        if fundacion_hasta is not None:
            params["fundacion_hasta"] = fundacion_hasta
        if empleados_min is not None:
            params["empleados_min"] = empleados_min
        if empleados_max is not None:
            params["empleados_max"] = empleados_max
        
        # Reenviar request a la API Flask
        return await proxy_service.get(
            endpoint="/api/desarrolladoras/buscar/",
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


# ===== ENDPOINTS DE RELACIONES (Admin y User) =====

@router.get(
    "/{desarrolladora_id}/videojuegos/",
    summary="Videojuegos de desarrolladora",
    description="Obtiene los videojuegos de una desarrolladora específica"
)
async def get_videojuegos_desarrolladora(
    current_user: CurrentUser,
    desarrolladora_id: int = Path(description=DESARROLLADORA_ID_DESCRIPTION),
    page: Optional[int] = Query(default=1, ge=1, description="Número de página"),
    per_page: Optional[int] = Query(default=10, ge=1, le=100, description="Elementos por página"),
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Obtener videojuegos de una desarrolladora.
    Accesible para usuarios admin y user.
    """
    try:
        # Verificar permiso de lectura
        if not has_permission(current_user, Permissions.DESARROLLADORA_READ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=NO_PERMISSION_DESARROLLADORAS_MESSAGE
            )
        
        # Preparar parámetros
        params = {
            "page": page,
            "per_page": per_page
        }
        
        # Reenviar request a la API Flask
        return await proxy_service.get(
            endpoint=f"/api/desarrolladoras/{desarrolladora_id}/videojuegos/",
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
    "/{desarrolladora_id}/estadisticas/",
    summary="Estadísticas de desarrolladora",
    description="""Obtiene estadísticas específicas de una desarrolladora.
    
    **Parámetros:**
    - `desarrolladora_id`: ID de la desarrolladora (entero positivo)
    
    **Ejemplo de uso:**
    ```
    GET /api/desarrolladoras/1/estadisticas/
    ```
    
    **Respuesta esperada:**
    ```json
    {
        "success": true,
        "message": "Estadísticas de la desarrolladora obtenidas exitosamente",
        "data": {
            "desarrolladora": {...},
            "total_videojuegos": 5,
            "precio_promedio": 45.99,
            "valoracion_promedio": 8.5,
            "categorias_desarrolladas": ["RPG", "Aventura", "Acción"]
        }
    }
    ```
    """
)
async def get_estadisticas_desarrolladora(
    current_user: CurrentUser,
    desarrolladora_id: int = Path(description=DESARROLLADORA_ID_DESCRIPTION),
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Obtener estadísticas específicas de una desarrolladora.
    Accesible para usuarios admin y user.
    """
    try:
        # Verificar permiso de lectura
        if not has_permission(current_user, Permissions.DESARROLLADORA_READ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=NO_PERMISSION_DESARROLLADORAS_MESSAGE
            )
        
        # Reenviar request a la API Flask
        return await proxy_service.get(
            endpoint=f"/api/desarrolladoras/{desarrolladora_id}/estadisticas/",
            user_email=current_user.email
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )