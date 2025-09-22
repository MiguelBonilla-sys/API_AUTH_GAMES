"""
Modelo Role para el sistema de autenticación.
Define los roles disponibles: admin (CRUD completo) y user (solo lectura).
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from src.config.database import Base


class Role(Base):
    """
    Modelo Role para control de acceso basado en roles.
    
    Roles disponibles:
    - admin: Acceso completo a todas las operaciones CRUD
    - user: Acceso de solo lectura (GET operations únicamente)
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación con usuarios
    users = relationship("User", back_populates="role")

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}')>"

    def __str__(self) -> str:
        return self.name
