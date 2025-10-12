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
    Crea los roles 'desarrolladora', 'editor' y 'superadmin' si no existen.
    """
    async with AsyncSessionLocal() as session:
        # Verificar si ya existen roles
        result = await session.execute(select(Role))
        existing_roles = result.scalars().all()
        
        if existing_roles:
            print("Roles ya existen en la base de datos")
            return
        
        # Crear roles por defecto
        desarrolladora_role = Role(
            name="desarrolladora",
            description="Desarrolladora que puede gestionar sus propios videojuegos y desarrolladora"
        )
        
        editor_role = Role(
            name="editor", 
            description="Editor que puede gestionar todos los videojuegos y leer desarrolladoras"
        )
        
        superadmin_role = Role(
            name="superadmin",
            description="Superadministrador con acceso completo a todas las operaciones del sistema"
        )
        
        session.add(desarrolladora_role)
        session.add(editor_role)
        session.add(superadmin_role)
        
        await session.commit()
        print("Roles por defecto creados exitosamente:")
        print(f"- {desarrolladora_role.name}: {desarrolladora_role.description}")
        print(f"- {editor_role.name}: {editor_role.description}")
        print(f"- {superadmin_role.name}: {superadmin_role.description}")


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
