"""
Servicio para manejo de tokens de renovación.
Implementa lógica de negocio para refresh tokens con rotación de seguridad.
"""

import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from src.models import User, RefreshToken
from src.auth.jwt_handler import create_refresh_token, verify_token
from src.auth.password import hash_password


class TokenService:
    """Servicio para manejo de tokens de renovación."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_refresh_token_for_user(self, user: User) -> tuple[str, RefreshToken]:
        """
        Crear un nuevo token de renovación para un usuario.
        
        Args:
            user: Usuario para el cual crear el token
            
        Returns:
            Tupla (token_plain, token_model)
        """
        # Generar token aleatorio seguro
        token_plain = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token_plain.encode()).hexdigest()
        
        # Calcular fecha de expiración
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)  # 7 días por defecto
        
        # Crear modelo de token
        refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        
        self.session.add(refresh_token)
        await self.session.commit()
        await self.session.refresh(refresh_token)
        
        return token_plain, refresh_token
    
    async def verify_refresh_token(self, token: str) -> Optional[User]:
        """
        Verificar un token de renovación y retornar el usuario asociado.
        
        Args:
            token: Token de renovación en texto plano
            
        Returns:
            Usuario asociado al token o None si es inválido
        """
        # Hash del token para buscar en la base de datos
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Buscar token en la base de datos
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.expires_at > datetime.now(timezone.utc)
            )
        )
        refresh_token = result.scalar_one_or_none()
        
        if not refresh_token:
            return None
        
        # Obtener usuario asociado
        result = await self.session.execute(
            select(User).where(User.id == refresh_token.user_id)
        )
        user = result.scalar_one_or_none()
        
        return user if user and user.is_active else None
    
    async def revoke_refresh_token(self, token: str) -> bool:
        """
        Revocar un token de renovación específico.
        
        Args:
            token: Token de renovación a revocar
            
        Returns:
            True si se revocó exitosamente, False si no se encontró
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        result = await self.session.execute(
            delete(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        
        await self.session.commit()
        return result.rowcount > 0
    
    async def revoke_all_user_tokens(self, user_id: int) -> int:
        """
        Revocar todos los tokens de renovación de un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Número de tokens revocados
        """
        result = await self.session.execute(
            delete(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        
        await self.session.commit()
        return result.rowcount
    
    async def cleanup_expired_tokens(self) -> int:
        """
        Limpiar tokens de renovación expirados de la base de datos.
        
        Returns:
            Número de tokens eliminados
        """
        result = await self.session.execute(
            delete(RefreshToken).where(
                RefreshToken.expires_at < datetime.now(timezone.utc)
            )
        )
        
        await self.session.commit()
        return result.rowcount
    
    async def get_user_active_tokens(self, user_id: int) -> List[RefreshToken]:
        """
        Obtener todos los tokens activos de un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Lista de tokens activos
        """
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.expires_at > datetime.now(timezone.utc)
            )
        )
        
        return result.scalars().all()
    
    async def rotate_refresh_token(self, old_token: str, user: User) -> tuple[str, RefreshToken]:
        """
        Rotar un token de renovación (invalidar el anterior y crear uno nuevo).
        Esto mejora la seguridad al limitar la ventana de uso de tokens comprometidos.
        
        Args:
            old_token: Token anterior a invalidar
            user: Usuario para el cual crear el nuevo token
            
        Returns:
            Tupla (nuevo_token_plain, nuevo_token_model)
        """
        # Revocar token anterior
        await self.revoke_refresh_token(old_token)
        
        # Crear nuevo token
        return await self.create_refresh_token_for_user(user)


# Funciones de conveniencia para uso en endpoints
async def create_user_refresh_token(session: AsyncSession, user: User) -> str:
    """
    Función de conveniencia para crear un token de renovación.
    
    Args:
        session: Sesión de base de datos
        user: Usuario
        
    Returns:
        Token de renovación en texto plano
    """
    token_service = TokenService(session)
    token_plain, _ = await token_service.create_refresh_token_for_user(user)
    return token_plain


async def verify_user_refresh_token(session: AsyncSession, token: str) -> Optional[User]:
    """
    Función de conveniencia para verificar un token de renovación.
    
    Args:
        session: Sesión de base de datos
        token: Token de renovación
        
    Returns:
        Usuario asociado o None
    """
    token_service = TokenService(session)
    return await token_service.verify_refresh_token(token)


async def revoke_user_refresh_token(session: AsyncSession, token: str) -> bool:
    """
    Función de conveniencia para revocar un token de renovación.
    
    Args:
        session: Sesión de base de datos
        token: Token de renovación
        
    Returns:
        True si se revocó exitosamente
    """
    token_service = TokenService(session)
    return await token_service.revoke_refresh_token(token)
