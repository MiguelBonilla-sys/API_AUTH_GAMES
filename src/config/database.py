"""
Configuración de base de datos PostgreSQL para el gateway de autenticación.
Utiliza SQLAlchemy async con psycopg para conexiones a Railway PostgreSQL.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
import os
import logging
from typing import AsyncGenerator

# Importar configuración
from .settings import get_settings

# Obtener configuración
settings = get_settings()
DATABASE_URL = settings.database_url

# Configurar logging de SQLAlchemy
def configure_sqlalchemy_logging():
    """Configurar el nivel de logging de SQLAlchemy."""
    # Silenciar logs verbosos de SQLAlchemy siempre, excepto en debug explícito
    logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
    logging.getLogger('sqlalchemy.dialects').setLevel(logging.ERROR)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.ERROR)
    logging.getLogger('sqlalchemy.orm').setLevel(logging.ERROR)
    
    # Solo permitir logs SQL si está explícitamente habilitado el debug
    if settings.debug and settings.environment == "development":
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Configurar logging al importar
configure_sqlalchemy_logging()

# Crear engine async para PostgreSQL
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Deshabilitado para evitar logs verbosos
    pool_pre_ping=True,  # Verificar conexiones antes de usar
    pool_recycle=300,  # Reciclar conexiones cada 5 minutos
)

# Crear session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class para todos los modelos
Base = declarative_base()
Base.metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency para obtener sesión de base de datos.
    Usado en FastAPI dependency injection.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Inicializar la base de datos creando todas las tablas.
    Debe ser llamado al inicio de la aplicación.
    """
    async with engine.begin() as conn:
        # Importar todos los modelos para que se registren
        from src.models import user, role, token
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Cerrar conexiones de base de datos.
    Debe ser llamado al cerrar la aplicación.
    """
    try:
        await engine.dispose()
    except Exception:
        # Silenciar errores durante el cierre, especialmente en hot reload
        pass
