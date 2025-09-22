"""
Script de inicialización para crear roles por defecto en la base de datos.
Se ejecuta al inicializar la aplicación para asegurar que existan los roles necesarios.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import Role
from src.config import AsyncSessionLocal


async def init_default_roles() -> None:
    """
    Inicializar roles por defecto en la base de datos.
    Crea los roles 'admin' y 'user' si no existen.
    """
    async with AsyncSessionLocal() as session:
        # Verificar si ya existen roles
        result = await session.execute(select(Role))
        existing_roles = result.scalars().all()
        
        if existing_roles:
            print("Roles ya existen en la base de datos")
            return
        
        # Crear roles por defecto
        admin_role = Role(
            name="admin",
            description="Administrador con acceso completo a todas las operaciones CRUD"
        )
        
        user_role = Role(
            name="user", 
            description="Usuario con acceso de solo lectura (GET operations únicamente)"
        )
        
        session.add(admin_role)
        session.add(user_role)
        
        await session.commit()
        print("Roles por defecto creados exitosamente:")
        print(f"- {admin_role.name}: {admin_role.description}")
        print(f"- {user_role.name}: {user_role.description}")


async def get_role_by_name(session: AsyncSession, role_name: str) -> Role | None:
    """
    Obtener un rol por su nombre.
    
    Args:
        session: Sesión de base de datos
        role_name: Nombre del rol a buscar
        
    Returns:
        Role object o None si no se encuentra
    """
    result = await session.execute(
        select(Role).where(Role.name == role_name)
    )
    return result.scalar_one_or_none()
