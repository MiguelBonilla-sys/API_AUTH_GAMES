"""
Dependencies de autenticación para FastAPI.
Implementa dependency injection para validar JWT y verificar roles.
"""

from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.config import get_db
from src.models import User, Role
from src.auth import (
    verify_token,
    get_user_by_id,
    JWTError
)

# Esquema de seguridad para Bearer tokens
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Obtener el usuario actual desde el token JWT.
    
    Args:
        credentials: Credenciales de autorización
        db: Sesión de base de datos
        
    Returns:
        Usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    try:
        # Verificar token JWT
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: ID de usuario no encontrado"
            )
        
        # Obtener usuario de la base de datos con su rol
        result = await db.execute(
            select(User).options(selectinload(User.role)).where(User.id == int(user_id))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado"
            )
        
        # Verificar que el usuario esté activo
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo"
            )
        
        return user
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}"
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: ID de usuario no válido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Obtener usuario activo (alias para get_current_user).
    
    Args:
        current_user: Usuario actual
        
    Returns:
        Usuario activo
    """
    return current_user


def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Obtener usuario actual y verificar que sea administrador.
    
    Args:
        current_user: Usuario actual
        
    Returns:
        Usuario administrador
        
    Raises:
        HTTPException: Si el usuario no es administrador
    """
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requieren permisos de administrador"
        )
    
    return current_user


def get_current_regular_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Obtener usuario actual y verificar que sea usuario regular.
    
    Args:
        current_user: Usuario actual
        
    Returns:
        Usuario regular
        
    Raises:
        HTTPException: Si el usuario no es usuario regular
    """
    if not current_user.role or current_user.role.name != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requieren permisos de usuario regular"
        )
    
    return current_user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Obtener usuario actual de forma opcional (para endpoints que pueden ser públicos o privados).
    
    Args:
        credentials: Credenciales de autorización (opcional)
        db: Sesión de base de datos
        
    Returns:
        Usuario autenticado o None si no hay token
    """
    if not credentials:
        return None
    
    try:
        # Verificar token JWT
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if not user_id:
            return None
        
        # Obtener usuario de la base de datos
        result = await db.execute(
            select(User).where(User.id == int(user_id))
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            return None
        
        return user
        
    except (JWTError, ValueError):
        return None
    except Exception:
        return None


# Type aliases para facilitar el uso
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
CurrentAdminUser = Annotated[User, Depends(get_current_admin_user)]
CurrentRegularUser = Annotated[User, Depends(get_current_regular_user)]
OptionalCurrentUser = Annotated[Optional[User], Depends(get_optional_current_user)]
