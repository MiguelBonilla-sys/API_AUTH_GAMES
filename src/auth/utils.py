"""
Utilidades de autenticación y autorización.
Funciones auxiliares para validación, permisos y seguridad.
"""

import re
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import User, Role
from src.auth.jwt_handler import JWTError, verify_token


def validate_email(email: str) -> bool:
    """
    Validar formato de email usando regex.
    
    Args:
        email: Email a validar
        
    Returns:
        True si el email es válido, False en caso contrario
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_complexity(password: str) -> tuple[bool, List[str]]:
    """
    Validar complejidad de contraseña con múltiples criterios.
    
    Args:
        password: Contraseña a validar
        
    Returns:
        Tupla (es_válida, lista_de_errores)
    """
    errors = []
    
    if len(password) < 8:
        errors.append("La contraseña debe tener al menos 8 caracteres")
    
    if len(password) > 128:
        errors.append("La contraseña no puede tener más de 128 caracteres")
    
    if not re.search(r'[A-Z]', password):
        errors.append("La contraseña debe contener al menos una letra mayúscula")
    
    if not re.search(r'[a-z]', password):
        errors.append("La contraseña debe contener al menos una letra minúscula")
    
    if not re.search(r'\d', password):
        errors.append("La contraseña debe contener al menos un número")
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        errors.append("La contraseña debe contener al menos un carácter especial")
    
    # Verificar contraseñas comunes (lista básica)
    common_passwords = [
        "password", "123456", "123456789", "qwerty", "abc123",
        "password123", "admin", "letmein", "welcome", "monkey"
    ]
    
    if password.lower() in common_passwords:
        errors.append("La contraseña es demasiado común")
    
    return len(errors) == 0, errors


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    """
    Obtener usuario por email.
    
    Args:
        session: Sesión de base de datos
        email: Email del usuario
        
    Returns:
        Usuario encontrado o None
    """
    result = await session.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    """
    Obtener usuario por ID.
    
    Args:
        session: Sesión de base de datos
        user_id: ID del usuario
        
    Returns:
        Usuario encontrado o None
    """
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_role_by_name(session: AsyncSession, role_name: str) -> Optional[Role]:
    """
    Obtener rol por nombre.
    
    Args:
        session: Sesión de base de datos
        role_name: Nombre del rol
        
    Returns:
        Rol encontrado o None
    """
    result = await session.execute(
        select(Role).where(Role.name == role_name)
    )
    return result.scalar_one_or_none()


def check_user_permissions(user: User, required_role: str = None) -> bool:
    """
    Verificar permisos de un usuario.
    
    Args:
        user: Usuario a verificar
        required_role: Rol requerido (opcional)
        
    Returns:
        True si el usuario tiene permisos, False en caso contrario
    """
    if not user or not user.is_active:
        return False
    
    if not user.role:
        return False
    
    if required_role:
        return user.role.name == required_role
    
    return True


def is_superadmin_user(user: User) -> bool:
    """
    Verificar si un usuario es superadministrador.
    
    Args:
        user: Usuario a verificar
        
    Returns:
        True si es superadministrador, False en caso contrario
    """
    return check_user_permissions(user, "superadmin")


def is_editor_user(user: User) -> bool:
    """
    Verificar si un usuario es editor.
    
    Args:
        user: Usuario a verificar
        
    Returns:
        True si es editor, False en caso contrario
    """
    return check_user_permissions(user, "editor")


def is_desarrolladora_user(user: User) -> bool:
    """
    Verificar si un usuario es desarrolladora.
    
    Args:
        user: Usuario a verificar
        
    Returns:
        True si es desarrolladora, False en caso contrario
    """
    return check_user_permissions(user, "desarrolladora")


def extract_token_from_header(authorization: str) -> Optional[str]:
    """
    Extraer token JWT del header Authorization.
    
    Args:
        authorization: Header Authorization (formato: "Bearer <token>")
        
    Returns:
        Token extraído o None si no es válido
    """
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split(" ", 1)
        if scheme.lower() != "bearer":
            return None
        return token
    except ValueError:
        return None


def validate_token_format(token: str) -> bool:
    """
    Validar formato básico de token JWT.
    
    Args:
        token: Token a validar
        
    Returns:
        True si el formato es válido, False en caso contrario
    """
    if not token:
        return False
    
    # JWT debe tener 3 partes separadas por puntos
    parts = token.split(".")
    if len(parts) != 3:
        return False
    
    # Cada parte debe ser base64 válido
    import base64
    try:
        for part in parts:
            base64.urlsafe_b64decode(part + "==")  # Agregar padding si es necesario
        return True
    except Exception:
        return False


def get_user_info_from_token(token: str) -> Optional[dict]:
    """
    Obtener información del usuario desde un token JWT.
    
    Args:
        token: Token JWT
        
    Returns:
        Diccionario con información del usuario o None si es inválido
    """
    try:
        payload = verify_token(token)
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "is_active": payload.get("is_active"),
            "token_type": payload.get("type")
        }
    except JWTError:
        return None


def sanitize_user_data(user: User) -> dict:
    """
    Sanitizar datos de usuario para respuesta (sin información sensible).
    
    Args:
        user: Usuario a sanitizar
        
    Returns:
        Diccionario con datos seguros del usuario
    """
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role.name if user.role else None,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }


async def verify_resource_ownership(
    resource_type: str, 
    resource_id: int, 
    user: User,
    proxy_service=None
) -> bool:
    """
    Verificar si un usuario es propietario de un recurso específico.
    
    Args:
        resource_type: Tipo de recurso ('videojuego' o 'desarrolladora')
        resource_id: ID del recurso
        user: Usuario a verificar
        proxy_service: Servicio proxy para consultar API Flask
        
    Returns:
        True si el usuario es propietario, False en caso contrario
    """
    try:
        if not proxy_service:
            # Si no hay proxy service, permitir acceso (fallback)
            return True
        
        # Consultar API Flask para obtener información del recurso
        if resource_type == "videojuego":
            endpoint = f"api/videojuegos/{resource_id}"
        elif resource_type == "desarrolladora":
            endpoint = f"api/desarrolladoras/{resource_id}"
        else:
            return False
        
        # Hacer request a la API Flask
        response = await proxy_service.get(
            endpoint=endpoint,
            user_email=user.email
        )
        
        if not response or not response.get("success"):
            return False
        
        resource_data = response.get("data", {})
        
        # Verificar ownership por email o ID
        owner_email = resource_data.get("owner_email") or resource_data.get("created_by_email")
        owner_id = resource_data.get("owner_id") or resource_data.get("created_by_id")
        
        # Comparar con el usuario actual
        if owner_email and owner_email == user.email:
            return True
        
        if owner_id and str(owner_id) == str(user.id):
            return True
        
        return False
        
    except Exception as e:
        # En caso de error, denegar acceso por seguridad
        print(f"Error verificando ownership: {e}")
        return False


def create_authorization_error_response(
    message: str,
    error_code: str = "INSUFFICIENT_PERMISSIONS",
    required_permission: str = None,
    user_role: str = None
) -> dict:
    """
    Crear respuesta de error de autorización estandarizada.
    
    Args:
        message: Mensaje de error
        error_code: Código de error específico
        required_permission: Permiso requerido
        user_role: Rol del usuario actual
        
    Returns:
        Diccionario con respuesta de error estandarizada
    """
    from datetime import datetime
    return {
        "success": False,
        "message": message,
        "error_type": "authorization_error",
        "error_code": error_code,
        "required_permission": required_permission,
        "user_role": user_role,
        "timestamp": datetime.now().isoformat()
    }


def create_resource_ownership_error_response(
    message: str,
    resource_type: str,
    resource_id: int
) -> dict:
    """
    Crear respuesta de error de propiedad de recurso estandarizada.
    
    Args:
        message: Mensaje de error
        resource_type: Tipo de recurso
        resource_id: ID del recurso
        
    Returns:
        Diccionario con respuesta de error estandarizada
    """
    from datetime import datetime
    return {
        "success": False,
        "message": message,
        "error_type": "resource_ownership_error",
        "error_code": "NOT_RESOURCE_OWNER",
        "resource_type": resource_type,
        "resource_id": resource_id,
        "timestamp": datetime.now().isoformat()
    }


def create_role_validation_error_response(
    message: str,
    requested_role: str,
    allowed_roles: list = None,
    error_code: str = "INVALID_ROLE"
) -> dict:
    """
    Crear respuesta de error de validación de rol estandarizada.
    
    Args:
        message: Mensaje de error
        requested_role: Rol solicitado
        allowed_roles: Lista de roles permitidos
        error_code: Código de error específico
        
    Returns:
        Diccionario con respuesta de error estandarizada
    """
    from datetime import datetime
    return {
        "success": False,
        "message": message,
        "error_type": "role_validation_error",
        "error_code": error_code,
        "requested_role": requested_role,
        "allowed_roles": allowed_roles or ["desarrolladora", "editor"],
        "timestamp": datetime.now().isoformat()
    }
