"""
Endpoints de administración para el gateway.
Implementa endpoints que requieren permisos de administrador.
"""

from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.config import get_db
from src.models import User, Role
from src.auth import (
    CurrentAdminUser,
    has_permission,
    Permissions,
    get_user_permissions
)
from src.schemas import (
    ApiResponse,
    UserListResponse,
    UserDetailResponse,
    RoleResponse
)

# Configurar router
router = APIRouter(prefix="/admin", tags=["administration"])


@router.get(
    "/users",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar todos los usuarios",
    description="Obtiene la lista de todos los usuarios (solo administradores)"
)
async def list_users(
    current_user: CurrentAdminUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Listar todos los usuarios del sistema.
    
    Args:
        current_user: Usuario administrador autenticado
        db: Sesión de base de datos
        
    Returns:
        Lista de usuarios
    """
    try:
        # Verificar permiso específico
        if not has_permission(current_user, Permissions.USER_READ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para leer usuarios"
            )
        
        # Obtener usuarios con sus roles
        result = await db.execute(
            select(User)
            .options(selectinload(User.role))
            .order_by(User.created_at.desc())
        )
        users = result.scalars().all()
        
        # Preparar respuesta
        user_list = [
            UserListResponse(
                id=user.id,
                email=user.email,
                role=user.role.name if user.role else "sin_rol",
                is_active=user.is_active,
                created_at=user.created_at
            )
            for user in users
        ]
        
        return ApiResponse(
            success=True,
            message="Usuarios obtenidos exitosamente",
            data=user_list,
            count=len(user_list),
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/users/{user_id}",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener usuario por ID",
    description="Obtiene los detalles de un usuario específico (solo administradores)"
)
async def get_user(
    user_id: int,
    current_user: CurrentAdminUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener detalles de un usuario específico.
    
    Args:
        user_id: ID del usuario
        current_user: Usuario administrador autenticado
        db: Sesión de base de datos
        
    Returns:
        Detalles del usuario
    """
    try:
        # Verificar permiso específico
        if not has_permission(current_user, Permissions.USER_READ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para leer usuarios"
            )
        
        # Obtener usuario con su rol
        result = await db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Preparar respuesta
        user_detail = UserDetailResponse(
            id=user.id,
            email=user.email,
            role=user.role.name if user.role else "sin_rol",
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=None  # Tracking de último login no implementado aún
        )
        
        return ApiResponse(
            success=True,
            message="Usuario obtenido exitosamente",
            data=user_detail,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/roles",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar todos los roles",
    description="Obtiene la lista de todos los roles (solo administradores)"
)
async def list_roles(
    current_user: CurrentAdminUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Listar todos los roles del sistema.
    
    Args:
        current_user: Usuario administrador autenticado
        db: Sesión de base de datos
        
    Returns:
        Lista de roles
    """
    try:
        # Verificar permiso específico
        if not has_permission(current_user, Permissions.ROLE_READ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para leer roles"
            )
        
        # Obtener roles con sus usuarios
        result = await db.execute(
            select(Role)
            .options(selectinload(Role.users))
            .order_by(Role.name)
        )
        roles = result.scalars().all()
        
        # Preparar respuesta
        role_list = [
            RoleResponse(
                id=role.id,
                name=role.name,
                description=role.description,
                created_at=role.created_at,
                user_count=len(role.users) if role.users else 0
            )
            for role in roles
        ]
        
        return ApiResponse(
            success=True,
            message="Roles obtenidos exitosamente",
            data=role_list,
            count=len(role_list),
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/stats",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Estadísticas del sistema",
    description="Obtiene estadísticas generales del sistema (solo administradores)"
)
async def get_system_stats(
    current_user: CurrentAdminUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener estadísticas del sistema.
    
    Args:
        current_user: Usuario administrador autenticado
        db: Sesión de base de datos
        
    Returns:
        Estadísticas del sistema
    """
    try:
        # Verificar permiso específico
        if not has_permission(current_user, Permissions.USER_READ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver estadísticas"
            )
        
        # Obtener estadísticas
        total_users_result = await db.execute(select(func.count(User.id)))
        total_users = total_users_result.scalar()
        
        active_users_result = await db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        active_users = active_users_result.scalar()
        
        total_roles_result = await db.execute(select(func.count(Role.id)))
        total_roles = total_roles_result.scalar()
        
        # Preparar respuesta
        stats = {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "total_roles": total_roles,
            "admin_users": 0,  # Conteo por rol no implementado aún
            "regular_users": 0,  # Conteo por rol no implementado aún
        }
        
        return ApiResponse(
            success=True,
            message="Estadísticas obtenidas exitosamente",
            data=stats,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/my-permissions",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener mis permisos",
    description="Obtiene los permisos del usuario autenticado"
)
async def get_my_permissions(
    current_user: CurrentAdminUser
):
    """
    Obtener permisos del usuario autenticado.
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        Lista de permisos del usuario
    """
    try:
        # Obtener permisos del usuario
        permissions = get_user_permissions(current_user)
        
        # Preparar respuesta
        permission_data = {
            "user_id": current_user.id,
            "user_email": current_user.email,
            "user_role": current_user.role.name if current_user.role else "sin_rol",
            "permissions": [
                {
                    "name": permission.name,
                    "description": permission.description
                }
                for permission in permissions
            ],
            "total_permissions": len(permissions)
        }
        
        return ApiResponse(
            success=True,
            message="Permisos obtenidos exitosamente",
            data=permission_data,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
