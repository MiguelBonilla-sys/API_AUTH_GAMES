"""
Modelo User para el sistema de autenticación.
Maneja usuarios con roles y autenticación JWT.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from src.config.database import Base


class User(Base):
    """
    Modelo User para autenticación y autorización.
    
    Campos:
    - id: Identificador único
    - email: Email único del usuario
    - password_hash: Hash de la contraseña (bcrypt)
    - role_id: Referencia al rol del usuario
    - is_active: Estado activo/inactivo del usuario
    - created_at: Fecha de creación
    - updated_at: Fecha de última actualización
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    role = relationship("Role", back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role_id={self.role_id})>"

    def __str__(self) -> str:
        return self.email

    @property
    def is_admin(self) -> bool:
        """Verificar si el usuario tiene rol de administrador."""
        return self.role and self.role.name == "admin"

    @property
    def is_user(self) -> bool:
        """Verificar si el usuario tiene rol de usuario regular."""
        return self.role and self.role.name == "user"
