"""
Script para inicializar la base de datos con datos de prueba.
Crea roles por defecto y usuarios de ejemplo.
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import AsyncSessionLocal, init_db
from src.models import User, Role
from src.auth import hash_password
from src.config.init_roles import init_default_roles


async def create_test_users():
    """Crear usuarios de prueba."""
    async with AsyncSessionLocal() as session:
        try:
            # Obtener roles
            from sqlalchemy import select
            admin_role_result = await session.execute(
                select(Role).where(Role.name == "admin")
            )
            admin_role = admin_role_result.scalar_one_or_none()
            
            user_role_result = await session.execute(
                select(Role).where(Role.name == "user")
            )
            user_role = user_role_result.scalar_one_or_none()
            
            if not admin_role or not user_role:
                print("❌ Roles no encontrados. Ejecutando init_default_roles...")
                await init_default_roles()
                
                # Obtener roles nuevamente
                admin_role_result = await session.execute(
                    select(Role).where(Role.name == "admin")
                )
                admin_role = admin_role_result.scalar_one_or_none()
                
                user_role_result = await session.execute(
                    select(Role).where(Role.name == "user")
                )
                user_role = user_role_result.scalar_one_or_none()
            
            # Crear usuario administrador
            admin_user = User(
                email="admin@example.com",
                password_hash=hash_password("AdminPassword123!"),
                role_id=admin_role.id,
                is_active=True
            )
            
            # Crear usuario regular
            regular_user = User(
                email="user@example.com",
                password_hash=hash_password("UserPassword123!"),
                role_id=user_role.id,
                is_active=True
            )
            
            # Verificar si los usuarios ya existen
            from sqlalchemy import select
            existing_admin = await session.execute(
                select(User).where(User.email == "admin@example.com")
            )
            if existing_admin.scalar_one_or_none():
                print("ℹ️  Usuario admin ya existe")
            else:
                session.add(admin_user)
                print("✅ Usuario admin creado: admin@example.com / AdminPassword123!")
            
            existing_user = await session.execute(
                select(User).where(User.email == "user@example.com")
            )
            if existing_user.scalar_one_or_none():
                print("ℹ️  Usuario regular ya existe")
            else:
                session.add(regular_user)
                print("✅ Usuario regular creado: user@example.com / UserPassword123!")
            
            await session.commit()
            print("✅ Base de datos inicializada correctamente")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error al inicializar base de datos: {e}")
            raise


async def main():
    """Función principal."""
    print("🗄️  Inicializando base de datos...")
    
    try:
        # Inicializar base de datos
        print("📊 Creando tablas...")
        await init_db()
        print("✅ Base de datos creada")
        
        # Crear usuarios de prueba
        print("👥 Creando usuarios de prueba...")
        await create_test_users()
        
        print("\n🎉 Inicialización completada!")
        print("\nUsuarios de prueba creados:")
        print("👑 Admin: admin@example.com / AdminPassword123!")
        print("👤 User:  user@example.com / UserPassword123!")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
