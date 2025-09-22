"""
Manejador de tokens JWT para autenticación.
Implementa generación, validación y decodificación de tokens JWT.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, DecodeError
from src.models import User


# Configuración JWT desde variables de entorno
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))


class JWTError(Exception):
    """Excepción personalizada para errores JWT."""
    pass


def create_access_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crear token de acceso JWT para un usuario.
    
    Args:
        user: Usuario para el cual crear el token
        expires_delta: Tiempo de expiración personalizado
        
    Returns:
        Token JWT codificado
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Payload del token
    payload = {
        "sub": str(user.id),  # Subject (ID del usuario)
        "email": user.email,
        "role": user.role.name if user.role else "user",
        "is_active": user.is_active,
        "exp": expire,  # Expiration time
        "iat": datetime.now(timezone.utc),  # Issued at
        "type": "access"  # Tipo de token
    }
    
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crear token de renovación JWT para un usuario.
    
    Args:
        user: Usuario para el cual crear el token
        expires_delta: Tiempo de expiración personalizado
        
    Returns:
        Token JWT de renovación codificado
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Payload del token de renovación
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"  # Tipo de token
    }
    
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    Verificar y decodificar un token JWT.
    
    Args:
        token: Token JWT a verificar
        token_type: Tipo de token esperado ("access" o "refresh")
        
    Returns:
        Payload decodificado del token
        
    Raises:
        JWTError: Si el token es inválido, expirado o del tipo incorrecto
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Verificar tipo de token
        if payload.get("type") != token_type:
            raise JWTError(f"Token type mismatch. Expected {token_type}, got {payload.get('type')}")
        
        # Verificar que el token no esté expirado (jwt.decode ya lo hace, pero por seguridad)
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise JWTError("Token has expired")
        
        return payload
        
    except ExpiredSignatureError:
        raise JWTError("Token has expired")
    except DecodeError:
        raise JWTError("Invalid token format")
    except InvalidTokenError as e:
        raise JWTError(f"Invalid token: {str(e)}")


def get_token_payload(token: str) -> Dict[str, Any]:
    """
    Obtener payload de un token sin verificar la firma.
    Útil para debugging o análisis de tokens.
    
    WARNING: Esta función no verifica la firma del token.
    Solo debe usarse para debugging o análisis, nunca para autenticación.
    
    Args:
        token: Token JWT
        
    Returns:
        Payload decodificado (sin verificar firma)
        
    Raises:
        JWTError: Si el token no se puede decodificar
    """
    try:
        # WARNING: No verificar firma - solo para debugging
        return jwt.decode(token, options={"verify_signature": False, "verify_exp": False})
    except DecodeError:
        raise JWTError("Invalid token format")


def is_token_expired(token: str) -> bool:
    """
    Verificar si un token está expirado sin validar la firma.
    
    Args:
        token: Token JWT
        
    Returns:
        True si el token está expirado, False en caso contrario
    """
    try:
        payload = get_token_payload(token)
        exp = payload.get("exp")
        if exp:
            return datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc)
        return True  # Si no hay exp, considerar expirado
    except JWTError:
        return True


def get_user_id_from_token(token: str) -> Optional[int]:
    """
    Extraer el ID del usuario de un token JWT.
    
    Args:
        token: Token JWT
        
    Returns:
        ID del usuario o None si no se puede extraer
    """
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        return int(user_id) if user_id else None
    except JWTError:
        return None


def get_user_role_from_token(token: str) -> Optional[str]:
    """
    Extraer el rol del usuario de un token JWT.
    
    Args:
        token: Token JWT
        
    Returns:
        Rol del usuario o None si no se puede extraer
    """
    try:
        payload = verify_token(token)
        return payload.get("role")
    except JWTError:
        return None
