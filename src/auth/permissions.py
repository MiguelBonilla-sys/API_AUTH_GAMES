"""
Sistema de permisos y autorización.
Implementa decoradores y funciones para verificar permisos de usuario.
"""

from typing import Callable, List, Union
from functools import wraps
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User, Role
from src.config import get_db


class Permission:
    """
    Clase para definir permisos específicos.
    """
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    def __str__(self) -> str:
        return self.name
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Permission):
            return self.name == other.name
        return False


# Permisos predefinidos
class Permissions:
    """Permisos disponibles en el sistema."""
    
    # Permisos de autenticación
    AUTH_LOGIN = Permission("auth:login", "Iniciar sesión")
    AUTH_LOGOUT = Permission("auth:logout", "Cerrar sesión")
    AUTH_REFRESH = Permission("auth:refresh", "Renovar token")
    AUTH_CHANGE_PASSWORD = Permission("auth:change_password", "Cambiar contraseña")
    
    # Permisos de usuarios
    USER_READ = Permission("user:read", "Leer usuarios")
    USER_CREATE = Permission("user:create", "Crear usuarios")
    USER_UPDATE = Permission("user:update", "Actualizar usuarios")
    USER_DELETE = Permission("user:delete", "Eliminar usuarios")
    
    # Permisos de roles
    ROLE_READ = Permission("role:read", "Leer roles")
    ROLE_CREATE = Permission("role:create", "Crear roles")
    ROLE_UPDATE = Permission("role:update", "Actualizar roles")
    ROLE_DELETE = Permission("role:delete", "Eliminar roles")
    
    # Permisos de videojuegos (proxy)
    VIDEOJUEGO_READ = Permission("videojuego:read", "Leer videojuegos")
    VIDEOJUEGO_CREATE = Permission("videojuego:create", "Crear videojuegos")
    VIDEOJUEGO_UPDATE = Permission("videojuego:update", "Actualizar videojuegos")
    VIDEOJUEGO_DELETE = Permission("videojuego:delete", "Eliminar videojuegos")
    
    # Permisos de desarrolladoras (proxy)
    DESARROLLADORA_READ = Permission("desarrolladora:read", "Leer desarrolladoras")
    DESARROLLADORA_CREATE = Permission("desarrolladora:create", "Crear desarrolladoras")
    DESARROLLADORA_UPDATE = Permission("desarrolladora:update", "Actualizar desarrolladoras")
    DESARROLLADORA_DELETE = Permission("desarrolladora:delete", "Eliminar desarrolladoras")


# Constantes para mensajes de error
UNAUTHENTICATED_MESSAGE = "Usuario no autenticado"

# Mapeo de roles a permisos
ROLE_PERMISSIONS = {
    "desarrolladora": [
        # Permisos de autenticación
        Permissions.AUTH_LOGIN,
        Permissions.AUTH_LOGOUT,
        Permissions.AUTH_REFRESH,
        Permissions.AUTH_CHANGE_PASSWORD,
        
        # Permisos de videojuegos (lectura de todos, CRUD de propios)
        Permissions.VIDEOJUEGO_READ,
        Permissions.VIDEOJUEGO_CREATE,
        Permissions.VIDEOJUEGO_UPDATE,
        Permissions.VIDEOJUEGO_DELETE,
        
        # Permisos de desarrolladoras (lectura de todas, CRUD de propia)
        Permissions.DESARROLLADORA_READ,
        Permissions.DESARROLLADORA_CREATE,
        Permissions.DESARROLLADORA_UPDATE,
        Permissions.DESARROLLADORA_DELETE,
    ],
    "editor": [
        # Permisos de autenticación
        Permissions.AUTH_LOGIN,
        Permissions.AUTH_LOGOUT,
        Permissions.AUTH_REFRESH,
        Permissions.AUTH_CHANGE_PASSWORD,
        
        # Permisos de videojuegos (CRUD completo)
        Permissions.VIDEOJUEGO_READ,
        Permissions.VIDEOJUEGO_CREATE,
        Permissions.VIDEOJUEGO_UPDATE,
        Permissions.VIDEOJUEGO_DELETE,
        
        # Permisos de desarrolladoras (solo lectura)
        Permissions.DESARROLLADORA_READ,
    ],
    "superadmin": [
        # Permisos de autenticación
        Permissions.AUTH_LOGIN,
        Permissions.AUTH_LOGOUT,
        Permissions.AUTH_REFRESH,
        Permissions.AUTH_CHANGE_PASSWORD,
        
        # Permisos de usuarios
        Permissions.USER_READ,
        Permissions.USER_CREATE,
        Permissions.USER_UPDATE,
        Permissions.USER_DELETE,
        
        # Permisos de roles
        Permissions.ROLE_READ,
        Permissions.ROLE_CREATE,
        Permissions.ROLE_UPDATE,
        Permissions.ROLE_DELETE,
        
        # Permisos de videojuegos (CRUD completo)
        Permissions.VIDEOJUEGO_READ,
        Permissions.VIDEOJUEGO_CREATE,
        Permissions.VIDEOJUEGO_UPDATE,
        Permissions.VIDEOJUEGO_DELETE,
        
        # Permisos de desarrolladoras (CRUD completo)
        Permissions.DESARROLLADORA_READ,
        Permissions.DESARROLLADORA_CREATE,
        Permissions.DESARROLLADORA_UPDATE,
        Permissions.DESARROLLADORA_DELETE,
    ]
}


def has_permission(user: User, permission: Permission) -> bool:
    """
    Verificar si un usuario tiene un permiso específico.
    
    Args:
        user: Usuario a verificar
        permission: Permiso a verificar
        
    Returns:
        True si el usuario tiene el permiso, False en caso contrario
    """
    if not user or not user.role:
        return False
    
    user_permissions = ROLE_PERMISSIONS.get(user.role.name, [])
    return permission in user_permissions


def has_any_permission(user: User, permissions: List[Permission]) -> bool:
    """
    Verificar si un usuario tiene al menos uno de los permisos especificados.
    
    Args:
        user: Usuario a verificar
        permissions: Lista de permisos a verificar
        
    Returns:
        True si el usuario tiene al menos un permiso, False en caso contrario
    """
    if not user or not user.role:
        return False
    
    user_permissions = ROLE_PERMISSIONS.get(user.role.name, [])
    return any(permission in user_permissions for permission in permissions)


def has_all_permissions(user: User, permissions: List[Permission]) -> bool:
    """
    Verificar si un usuario tiene todos los permisos especificados.
    
    Args:
        user: Usuario a verificar
        permissions: Lista de permisos a verificar
        
    Returns:
        True si el usuario tiene todos los permisos, False en caso contrario
    """
    if not user or not user.role:
        return False
    
    user_permissions = ROLE_PERMISSIONS.get(user.role.name, [])
    return all(permission in user_permissions for permission in permissions)


def require_permission(permission: Permission):
    """
    Decorador para requerir un permiso específico.
    
    Args:
        permission: Permiso requerido
        
    Returns:
        Decorador de función
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Buscar el usuario en los argumentos
            user = None
            for arg in args:
                if isinstance(arg, User):
                    user = arg
                    break
            
            for key, value in kwargs.items():
                if isinstance(value, User):
                    user = value
                    break
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=UNAUTHENTICATED_MESSAGE
                )
            
            if not has_permission(user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permiso requerido: {permission.name}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(permissions: List[Permission]):
    """
    Decorador para requerir al menos uno de los permisos especificados.
    
    Args:
        permissions: Lista de permisos requeridos
        
    Returns:
        Decorador de función
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Buscar el usuario en los argumentos
            user = None
            for arg in args:
                if isinstance(arg, User):
                    user = arg
                    break
            
            for key, value in kwargs.items():
                if isinstance(value, User):
                    user = value
                    break
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=UNAUTHENTICATED_MESSAGE
                )
            
            if not has_any_permission(user, permissions):
                permission_names = [p.name for p in permissions]
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Se requiere al menos uno de estos permisos: {', '.join(permission_names)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_all_permissions(permissions: List[Permission]):
    """
    Decorador para requerir todos los permisos especificados.
    
    Args:
        permissions: Lista de permisos requeridos
        
    Returns:
        Decorador de función
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Buscar el usuario en los argumentos
            user = None
            for arg in args:
                if isinstance(arg, User):
                    user = arg
                    break
            
            for key, value in kwargs.items():
                if isinstance(value, User):
                    user = value
                    break
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=UNAUTHENTICATED_MESSAGE
                )
            
            if not has_all_permissions(user, permissions):
                permission_names = [p.name for p in permissions]
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Se requieren todos estos permisos: {', '.join(permission_names)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role_name: str):
    """
    Decorador para requerir un rol específico.
    
    Args:
        role_name: Nombre del rol requerido
        
    Returns:
        Decorador de función
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Buscar el usuario en los argumentos
            user = None
            for arg in args:
                if isinstance(arg, User):
                    user = arg
                    break
            
            for key, value in kwargs.items():
                if isinstance(value, User):
                    user = value
                    break
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=UNAUTHENTICATED_MESSAGE
                )
            
            if not user.role or user.role.name != role_name:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Rol requerido: {role_name}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_desarrolladora(func: Callable):
    """
    Decorador para requerir rol de desarrolladora.
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada
    """
    return require_role("desarrolladora")(func)


def require_editor(func: Callable):
    """
    Decorador para requerir rol de editor.
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada
    """
    return require_role("editor")(func)


def require_superadmin(func: Callable):
    """
    Decorador para requerir rol de superadministrador.
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada
    """
    return require_role("superadmin")(func)


def get_user_permissions(user: User) -> List[Permission]:
    """
    Obtener todos los permisos de un usuario.
    
    Args:
        user: Usuario
        
    Returns:
        Lista de permisos del usuario
    """
    if not user or not user.role:
        return []
    
    return ROLE_PERMISSIONS.get(user.role.name, [])


def get_user_permission_names(user: User) -> List[str]:
    """
    Obtener nombres de todos los permisos de un usuario.
    
    Args:
        user: Usuario
        
    Returns:
        Lista de nombres de permisos del usuario
    """
    permissions = get_user_permissions(user)
    return [permission.name for permission in permissions]
