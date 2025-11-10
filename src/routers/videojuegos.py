"""
Proxy router para videojuegos.
Reenvía requests autenticados a la API Flask existente con restricciones por rol.
"""

from typing import Optional, Dict, Any, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from fastapi.responses import JSONResponse

from src.auth import (
    CurrentUser,
    CurrentSuperadminUser,
    OptionalCurrentUser,
    get_current_user,
    get_current_superadmin_user,
    get_optional_current_user,
    has_permission,
    Permissions
)
from src.auth.utils import verify_resource_ownership
from src.services import get_proxy_service, ProxyService
from src.schemas.videojuegos import (
    VideojuegoCreateRequest,
    VideojuegoUpdateRequest,
    VideojuegoFilterRequest,
    VideojuegoListResponse,
    VideojuegoDetailResponse,
    VideojuegoCreateResponse,
    VideojuegoUpdateResponse,
    VideojuegoDeleteResponse,
    CategoriasResponse,
    EstadisticasResponse,
    VideojuegoErrorResponse,
    VideojuegoNotFoundResponse
)

# Configurar router
router = APIRouter(prefix="/api/videojuegos", tags=["videojuegos"])

# Constantes para mensajes de error
NO_PERMISSION_VIDEOJUEGOS_MESSAGE = "No tienes permisos para leer videojuegos"
VIDEOJUEGO_ID_DESCRIPTION = "ID del videojuego"


# ===== ENDPOINTS DE LECTURA (Admin y User) =====

@router.get(
    "/",
    summary="Listar videojuegos",
    description="""Obtiene la lista de videojuegos con filtros opcionales.
    
    **Filtros disponibles:**
    - `categoria`: Filtrar por categoría específica (ej: RPG, Acción, Aventura)
    - `desarrolladora`: Filtrar por nombre de desarrolladora
    - `buscar`: Búsqueda de texto en nombre, categoría y desarrolladora
    - `precio_min` y `precio_max`: Rango de precios
    - `valoracion_min` y `valoracion_max`: Rango de valoraciones (0-10)
    - `desarrolladora_id`: ID específico de desarrolladora
    
    **Paginación:**
    - `page`: Número de página (por defecto: 1)
    - `per_page`: Elementos por página (por defecto: 10, máximo: 100)
    
    **Ordenamiento:**
    - `ordenar`: Campo para ordenar (nombre, precio, valoracion, categoria)
    - `direccion`: Dirección de ordenamiento (asc/desc)
    
    **Ejemplo de uso:**
    ```
    GET /api/videojuegos?categoria=RPG&precio_min=20&precio_max=60&page=1&per_page=5
    ```
    """,
    response_model=VideojuegoListResponse,
    responses={
        200: {
            "description": "Lista de videojuegos obtenida exitosamente",
            "model": VideojuegoListResponse
        },
        403: {
            "description": "No tienes permisos para leer videojuegos",
            "model": VideojuegoErrorResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": VideojuegoErrorResponse
        }
    }
)
async def list_videojuegos(
    current_user: OptionalCurrentUser,
    page: Optional[int] = Query(default=1, ge=1, description="Número de página", example=1),
    per_page: Optional[int] = Query(default=10, ge=1, le=100, description="Elementos por página", example=10),
    categoria: Optional[str] = Query(default=None, description="Filtrar por categoría", example="RPG"),
    desarrolladora: Optional[str] = Query(default=None, description="Filtrar por desarrolladora", example="Nintendo"),
    buscar: Optional[str] = Query(default=None, description="Búsqueda de texto", example="zelda"),
    ordenar: Optional[str] = Query(default="nombre", description="Campo para ordenar", example="nombre"),
    direccion: Optional[str] = Query(default="asc", description="Dirección de ordenamiento", example="asc"),
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Listar videojuegos con filtros opcionales.
    Acceso público - no requiere autenticación.
    """
    try:
        # Endpoint público - no requiere verificación de permisos
        
        # Preparar parámetros
        params = {
            "page": page,
            "per_page": per_page
        }
        
        if categoria:
            params["categoria"] = categoria
        if desarrolladora:
            params["desarrolladora"] = desarrolladora
        if buscar:
            params["buscar"] = buscar
        if ordenar:
            params["ordenar"] = ordenar
        if direccion:
            params["direccion"] = direccion
        
        # Reenviar request a la API Flask
        return await proxy_service.get(
            endpoint="api/videojuegos",
            params=params,
            user_email=current_user.email if current_user else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/{videojuego_id}",
    summary="Obtener videojuego por ID",
    description="""Obtiene los detalles de un videojuego específico por su ID.
    
    **Parámetros:**
    - `videojuego_id`: ID único del videojuego (entero positivo)
    
    **Ejemplo de uso:**
    ```
    GET /api/videojuegos/1
    ```
    """,
    response_model=VideojuegoDetailResponse,
    responses={
        200: {
            "description": "Videojuego obtenido exitosamente",
            "model": VideojuegoDetailResponse
        },
        403: {
            "description": "No tienes permisos para leer videojuegos",
            "model": VideojuegoErrorResponse
        },
        404: {
            "description": "Videojuego no encontrado",
            "model": VideojuegoNotFoundResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": VideojuegoErrorResponse
        }
    }
)
async def get_videojuego(
    current_user: OptionalCurrentUser,
    videojuego_id: int = Path(description=VIDEOJUEGO_ID_DESCRIPTION, example=1),
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Obtener videojuego por ID.
    Acceso público - no requiere autenticación.
    """
    try:
        # Endpoint público - no requiere verificación de permisos
        
        # Reenviar request a la API Flask
        return await proxy_service.get(
            endpoint=f"api/videojuegos/{videojuego_id}",
            user_email=current_user.email if current_user else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/categorias/",
    summary="Listar categorías",
    description="""Obtiene la lista de todas las categorías únicas de videojuegos.
    
    **Ejemplo de uso:**
    ```
    GET /api/videojuegos/categorias/
    ```
    
    **Respuesta esperada:**
    ```json
    {
        "success": true,
        "message": "Categorías obtenidas exitosamente",
        "data": ["RPG", "Acción", "Aventura", "Deportes"],
        "count": 4,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    ```
    """,
    response_model=CategoriasResponse,
    responses={
        200: {
            "description": "Categorías obtenidas exitosamente",
            "model": CategoriasResponse
        },
        403: {
            "description": "No tienes permisos para leer videojuegos",
            "model": VideojuegoErrorResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": VideojuegoErrorResponse
        }
    }
)
async def list_categorias(
    current_user: OptionalCurrentUser,
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Listar categorías de videojuegos.
    Acceso público - no requiere autenticación.
    """
    try:
        # Endpoint público - no requiere verificación de permisos
        
        # Reenviar request a la API Flask
        return await proxy_service.get(
            endpoint="api/videojuegos/categorias",
            user_email=current_user.email if current_user else None
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
    summary="Estadísticas de videojuegos",
    description="""Obtiene estadísticas generales de los videojuegos en el sistema.
    
    **Ejemplo de uso:**
    ```
    GET /api/videojuegos/estadisticas/
    ```
    
    **Respuesta esperada:**
    ```json
    {
        "success": true,
        "message": "Estadísticas obtenidas exitosamente",
        "data": {
            "total_videojuegos": 15,
            "categorias_unicas": 5,
            "precio_promedio": 45.99,
            "valoracion_promedio": 8.2
        },
        "timestamp": "2024-01-15T10:30:00Z"
    }
    ```
    """,
    response_model=EstadisticasResponse,
    responses={
        200: {
            "description": "Estadísticas obtenidas exitosamente",
            "model": EstadisticasResponse
        },
        403: {
            "description": "No tienes permisos para leer videojuegos",
            "model": VideojuegoErrorResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": VideojuegoErrorResponse
        }
    }
)
async def get_estadisticas(
    current_user: OptionalCurrentUser,
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Obtener estadísticas de videojuegos.
    Acceso público - no requiere autenticación.
    """
    try:
        # Endpoint público - no requiere verificación de permisos
        
        # Reenviar request a la API Flask
        return await proxy_service.get(
            endpoint="api/videojuegos/estadisticas",
            user_email=current_user.email if current_user else None
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
    summary="Crear videojuego",
    description="""Crea un nuevo videojuego en el sistema (solo administradores).
    
    **Campos requeridos:**
    - `nombre`: Nombre del videojuego (1-255 caracteres)
    - `categoria`: Categoría del videojuego (1-100 caracteres)
    - `precio`: Precio en USD (mayor o igual a 0)
    - `valoracion`: Valoración del 0 al 10
    
    **Campos opcionales:**
    - `desarrolladora_id`: ID de la desarrolladora (usar GET /api/desarrolladoras para ver opciones)
    
    **Ejemplo de body:**
    ```json
    {
        "nombre": "The Witcher 3: Wild Hunt",
        "categoria": "RPG",
        "precio": 39.99,
        "valoracion": 9.3,
        "desarrolladora_id": 1
    }
    ```
    """,
    response_model=VideojuegoCreateResponse,
    responses={
        201: {
            "description": "Videojuego creado exitosamente",
            "model": VideojuegoCreateResponse
        },
        400: {
            "description": "Error en la validación de datos",
            "model": VideojuegoErrorResponse
        },
        403: {
            "description": "No tienes permisos para crear videojuegos",
            "model": VideojuegoErrorResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": VideojuegoErrorResponse
        }
    }
)
async def create_videojuego(
    videojuego_data: VideojuegoCreateRequest,
    current_user: CurrentUser,
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Crear nuevo videojuego.
    Solo accesible para editores y superadministradores.
    """
    try:
        # Verificar permiso de creación
        if not has_permission(current_user, Permissions.VIDEOJUEGO_CREATE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para crear videojuegos"
            )
        
        # Reenviar request a la API Flask
        return await proxy_service.post(
            endpoint="api/videojuegos",
            json_data=videojuego_data.dict(),
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
    "/{videojuego_id}",
    summary="Actualizar videojuego",
    description="""Actualiza un videojuego existente (solo administradores).
    
    **Parámetros:**
    - `videojuego_id`: ID del videojuego a actualizar
    
    **Campos opcionales (todos los campos son opcionales para actualización):**
    - `nombre`: Nombre del videojuego (1-255 caracteres)
    - `categoria`: Categoría del videojuego (1-100 caracteres)
    - `precio`: Precio en USD (mayor o igual a 0)
    - `valoracion`: Valoración del 0 al 10
    - `desarrolladora_id`: ID de la desarrolladora
    
    **Ejemplo de body:**
    ```json
    {
        "nombre": "The Witcher 3: Wild Hunt - Complete Edition",
        "categoria": "RPG",
        "precio": 29.99,
        "valoracion": 9.5,
        "desarrolladora_id": 1
    }
    ```
    """,
    response_model=VideojuegoUpdateResponse,
    responses={
        200: {
            "description": "Videojuego actualizado exitosamente",
            "model": VideojuegoUpdateResponse
        },
        400: {
            "description": "Error en la validación de datos",
            "model": VideojuegoErrorResponse
        },
        403: {
            "description": "No tienes permisos para actualizar videojuegos",
            "model": VideojuegoErrorResponse
        },
        404: {
            "description": "Videojuego no encontrado",
            "model": VideojuegoNotFoundResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": VideojuegoErrorResponse
        }
    }
)
async def update_videojuego(
    current_user: CurrentUser,
    videojuego_id: int = Path(description=VIDEOJUEGO_ID_DESCRIPTION, example=1),
    videojuego_data: VideojuegoUpdateRequest = None,
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Actualizar videojuego existente.
    Accesible para editores, superadministradores y desarrolladoras (solo propios).
    """
    try:
        # Verificar permiso de actualización
        if not has_permission(current_user, Permissions.VIDEOJUEGO_UPDATE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para actualizar videojuegos"
            )
        
        # Si es desarrolladora, verificar que sea propietaria del videojuego
        if current_user.role and current_user.role.name == "desarrolladora":
            is_owner = await verify_resource_ownership(
                resource_type="videojuego",
                resource_id=videojuego_id,
                user=current_user,
                proxy_service=proxy_service
            )
            if not is_owner:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Solo puedes actualizar tus propios videojuegos"
                )
        
        # Reenviar request a la API Flask
        return await proxy_service.put(
            endpoint=f"api/videojuegos/{videojuego_id}",
            json_data=videojuego_data.dict() if videojuego_data else {},
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
    "/{videojuego_id}",
    summary="Eliminar videojuego",
    description="""Elimina un videojuego del sistema (solo administradores).
    
    **Parámetros:**
    - `videojuego_id`: ID del videojuego a eliminar
    
    **Ejemplo de uso:**
    ```
    DELETE /api/videojuegos/1
    ```
    
    **⚠️ Advertencia:** Esta acción es irreversible.
    """,
    response_model=VideojuegoDeleteResponse,
    responses={
        200: {
            "description": "Videojuego eliminado exitosamente",
            "model": VideojuegoDeleteResponse
        },
        403: {
            "description": "No tienes permisos para eliminar videojuegos",
            "model": VideojuegoErrorResponse
        },
        404: {
            "description": "Videojuego no encontrado",
            "model": VideojuegoNotFoundResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": VideojuegoErrorResponse
        }
    }
)
async def delete_videojuego(
    current_user: CurrentUser,
    videojuego_id: int = Path(description=VIDEOJUEGO_ID_DESCRIPTION, example=1),
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Eliminar videojuego.
    Accesible para editores, superadministradores y desarrolladoras (solo propios).
    """
    try:
        # Verificar permiso de eliminación
        if not has_permission(current_user, Permissions.VIDEOJUEGO_DELETE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para eliminar videojuegos"
            )
        
        # Si es desarrolladora, verificar que sea propietaria del videojuego
        if current_user.role and current_user.role.name == "desarrolladora":
            is_owner = await verify_resource_ownership(
                resource_type="videojuego",
                resource_id=videojuego_id,
                user=current_user,
                proxy_service=proxy_service
            )
            if not is_owner:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Solo puedes eliminar tus propios videojuegos"
                )
        
        # Reenviar request a la API Flask
        return await proxy_service.delete(
            endpoint=f"api/videojuegos/{videojuego_id}",
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
    summary="Búsqueda híbrida (local + RAWG)",
    description="""Búsqueda híbrida de videojuegos en la base de datos local y opcionalmente en RAWG API.
    
    **Parámetros requeridos:**
    - `q`: Término de búsqueda (requerido)
    
    **Parámetros opcionales:**
    - `include_external`: Incluir resultados de RAWG (default: true)
    
    **Ejemplo de uso:**
    ```
    GET /api/videojuegos/buscar/?q=zelda&include_external=true
    ```
    
    **Respuesta esperada:**
    ```json
    {
        "success": true,
        "message": "Búsqueda completada: 2 locales, 5 externos",
        "data": {
            "local": [...],
            "external": [...]
        },
        "count": 7
    }
    ```
    """,
    response_model=VideojuegoListResponse,
    responses={
        200: {
            "description": "Búsqueda híbrida realizada exitosamente",
            "model": VideojuegoListResponse
        },
        400: {
            "description": "Error en los parámetros de búsqueda (q es requerido)",
            "model": VideojuegoErrorResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": VideojuegoErrorResponse
        }
    }
)
async def buscar_videojuegos(
    current_user: OptionalCurrentUser,
    q: str = Query(..., description="Término de búsqueda", example="zelda"),
    include_external: Optional[bool] = Query(default=True, description="Incluir resultados de RAWG", example=True),
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Búsqueda híbrida de videojuegos (local + RAWG).
    Acceso público - no requiere autenticación.
    """
    try:
        # Endpoint público - no requiere verificación de permisos
        
        # Preparar parámetros
        params = {
            "q": q,
            "include_external": include_external
        }
        
        # Reenviar request a la API Flask
        return await proxy_service.get(
            endpoint="api/videojuegos/buscar",
            params=params,
            user_email=current_user.email if current_user else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post(
    "/importar-batch/",
    summary="Importar videojuegos desde RAWG",
    description="""Importa videojuegos desde RAWG API. Si no se proporcionan juegos en el body, importa automáticamente juegos populares evitando los que ya existen.
    
    **Query parameters:**
    - `count`: Cantidad de juegos populares a importar (default: 6, min: 1, max: 50). Solo aplica si no se proporcionan juegos en el body.
    
    **Body opcional:**
    ```json
    {
        "games": [
            {"external_id": "3328"},
            {"external_id": "3498"}
        ]
    }
    ```
    
    **Ejemplos de uso:**
    - Sin parámetros (importa 6 juegos populares): `POST /api/videojuegos/importar-batch/` con body `{}`
    - Con count: `POST /api/videojuegos/importar-batch/?count=10` con body `{}`
    - Con juegos específicos: `POST /api/videojuegos/importar-batch/` con body `{"games": [{"external_id": "3328"}]}`
    
    **Respuesta:**
    ```json
    {
        "success": true,
        "message": "Importación completada: 5 exitosos, 1 fallidos, 0 omitidos",
        "data": {
            "success": [...],
            "failed": [...],
            "skipped": [...]
        }
    }
    ```
    """,
    responses={
        201: {
            "description": "Juegos importados exitosamente",
        },
        207: {
            "description": "Multi-Status: algunos exitosos, algunos fallidos",
        },
        400: {
            "description": "Error en la validación de datos",
            "model": VideojuegoErrorResponse
        },
        403: {
            "description": "No tienes permisos para importar videojuegos",
            "model": VideojuegoErrorResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": VideojuegoErrorResponse
        }
    }
)
async def importar_batch_videojuegos(
    current_user: CurrentUser,
    count: Optional[int] = Query(default=6, ge=1, le=50, description="Cantidad de juegos populares a importar", example=6),
    body: Optional[Dict[str, Any]] = Body(default=None, description="Lista de juegos a importar (opcional)"),
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Importar videojuegos desde RAWG API.
    Solo accesible para editores y superadministradores.
    """
    try:
        # Verificar permiso de creación
        if not has_permission(current_user, Permissions.VIDEOJUEGO_CREATE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para importar videojuegos"
            )
        
        # Preparar body (si no se proporciona, usar objeto vacío)
        json_data = body if body else {}
        
        # Agregar count como query param en la URL
        params = {"count": count}
        
        # Reenviar request a la API Flask
        return await proxy_service.forward_request(
            method="POST",
            endpoint="api/videojuegos/importar-batch",
            params=params,
            json_data=json_data,
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
    "/{videojuego_id}/enriquecido/",
    summary="Obtener videojuego enriquecido",
    description="""Obtiene un videojuego con datos adicionales de RAWG (screenshots, plataformas, tags).
    
    **Parámetros:**
    - `videojuego_id`: ID del videojuego (entero positivo)
    
    **Ejemplo de uso:**
    ```
    GET /api/videojuegos/1/enriquecido/
    ```
    
    **Respuesta esperada:**
    ```json
    {
        "success": true,
        "message": "Juego enriquecido obtenido exitosamente",
        "data": {
            "id": 1,
            "nombre": "The Legend of Zelda: Breath of the Wild",
            "plataformas": ["Nintendo Switch", "Wii U"],
            "screenshots": ["url1", "url2"],
            "tags": ["Action", "Adventure", "RPG"]
        }
    }
    ```
    """,
    response_model=VideojuegoDetailResponse,
    responses={
        200: {
            "description": "Videojuego enriquecido obtenido exitosamente",
            "model": VideojuegoDetailResponse
        },
        404: {
            "description": "Videojuego no encontrado",
            "model": VideojuegoNotFoundResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": VideojuegoErrorResponse
        }
    }
)
async def get_videojuego_enriquecido(
    current_user: OptionalCurrentUser,
    videojuego_id: int = Path(description=VIDEOJUEGO_ID_DESCRIPTION, example=1),
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Obtener videojuego con datos enriquecidos de RAWG.
    Acceso público - no requiere autenticación.
    """
    try:
        # Endpoint público - no requiere verificación de permisos
        
        # Reenviar request a la API Flask
        return await proxy_service.get(
            endpoint=f"api/videojuegos/{videojuego_id}/enriquecido",
            user_email=current_user.email if current_user else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/sync-status/{task_id}/",
    summary="Estado de sincronización",
    description="""Consulta el estado de una tarea de sincronización asíncrona.
    
    **Parámetros:**
    - `task_id`: ID de la tarea de Celery (string)
    
    **Ejemplo de uso:**
    ```
    GET /api/videojuegos/sync-status/abc123-def456-ghi789/
    ```
    
    **Respuesta esperada:**
    ```json
    {
        "success": true,
        "message": "Task en cola",
        "data": {
            "status": "pending",
            "message": "Task en cola"
        }
    }
    ```
    
    **Estados posibles:**
    - `pending`: Tarea en cola
    - `running`: Sincronización en progreso
    - `completed`: Sincronización completada exitosamente
    - `failed`: Sincronización fallida
    """,
    responses={
        200: {
            "description": "Estado de sincronización obtenido exitosamente",
        },
        404: {
            "description": "Tarea no encontrada",
            "model": VideojuegoErrorResponse
        },
        500: {
            "description": "Error interno del servidor",
            "model": VideojuegoErrorResponse
        }
    }
)
async def get_sync_status(
    current_user: OptionalCurrentUser,
    task_id: str = Path(description="ID de la tarea de sincronización", example="abc123-def456-ghi789"),
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    Consultar estado de sincronización.
    Acceso público - no requiere autenticación.
    """
    try:
        # Endpoint público - no requiere verificación de permisos
        
        # Reenviar request a la API Flask
        return await proxy_service.get(
            endpoint=f"api/videojuegos/sync-status/{task_id}",
            user_email=current_user.email if current_user else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
