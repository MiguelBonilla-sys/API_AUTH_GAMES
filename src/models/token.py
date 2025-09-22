"""
Modelo RefreshToken para el sistema de autenticación JWT.
Maneja tokens de renovación para mantener sesiones activas.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from src.config.database import Base


class RefreshToken(Base):
    """
    Modelo RefreshToken para manejo de tokens de renovación JWT.
    
    Campos:
    - id: Identificador único
    - user_id: Referencia al usuario propietario del token
    - token_hash: Hash del token de renovación
    - expires_at: Fecha de expiración del token
    - created_at: Fecha de creación del token
    """
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación con usuario
    user = relationship("User", back_populates="refresh_tokens")

    def __repr__(self) -> str:
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, expires_at='{self.expires_at}')>"

    def __str__(self) -> str:
        return f"RefreshToken for user {self.user_id}"
