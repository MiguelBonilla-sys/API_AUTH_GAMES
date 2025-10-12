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
    """Crear usuarios de prueba con los nuevos roles."""
    async with AsyncSessionLocal() as session:
        try:
            # Obtener roles
            from sqlalchemy import select
            superadmin_role_result = await session.execute(
                select(Role).where(Role.name == "superadmin")
            )
            superadmin_role = superadmin_role_result.scalar_one_or_none()
            
            editor_role_result = await session.execute(
                select(Role).where(Role.name == "editor")
            )
            editor_role = editor_role_result.scalar_one_or_none()
            
            desarrolladora_role_result = await session.execute(
                select(Role).where(Role.name == "desarrolladora")
            )
            desarrolladora_role = desarrolladora_role_result.scalar_one_or_none()
            
            if not superadmin_role or not editor_role or not desarrolladora_role:
                print("❌ Roles no encontrados. Ejecutando init_default_roles...")
                await init_default_roles()
                
                # Obtener roles nuevamente
                superadmin_role_result = await session.execute(
                    select(Role).where(Role.name == "superadmin")
                )
                superadmin_role = superadmin_role_result.scalar_one_or_none()
                
                editor_role_result = await session.execute(
                    select(Role).where(Role.name == "editor")
                )
                editor_role = editor_role_result.scalar_one_or_none()
                
                desarrolladora_role_result = await session.execute(
                    select(Role).where(Role.name == "desarrolladora")
                )
                desarrolladora_role = desarrolladora_role_result.scalar_one_or_none()
            
            # Crear usuario superadmin
            superadmin_user = User(
                email="superadmin@example.com",
                password_hash=hash_password("SuperAdmin123!"),
                role_id=superadmin_role.id,
                is_active=True
            )
            
            # Crear usuario editor
            editor_user = User(
                email="editor@example.com",
                password_hash=hash_password("EditorPassword123!"),
                role_id=editor_role.id,
                is_active=True
            )
            
            # Crear desarrolladora 1
            desarrolladora1_user = User(
                email="desarrolladora1@example.com",
                password_hash=hash_password("DevPassword123!"),
                role_id=desarrolladora_role.id,
                is_active=True
            )
            
            # Crear desarrolladora 2
            desarrolladora2_user = User(
                email="desarrolladora2@example.com",
                password_hash=hash_password("DevPassword123!"),
                role_id=desarrolladora_role.id,
                is_active=True
            )
            
            # Verificar si los usuarios ya existen y crearlos
            users_to_create = [
                (superadmin_user, "superadmin@example.com", "SuperAdmin123!"),
                (editor_user, "editor@example.com", "EditorPassword123!"),
                (desarrolladora1_user, "desarrolladora1@example.com", "DevPassword123!"),
                (desarrolladora2_user, "desarrolladora2@example.com", "DevPassword123!")
            ]
            
            for user, email, password in users_to_create:
                existing_user = await session.execute(
                    select(User).where(User.email == email)
                )
                if existing_user.scalar_one_or_none():
                    print(f"ℹ️  Usuario {email} ya existe")
                else:
                    session.add(user)
                    print(f"✅ Usuario creado: {email} / {password}")
            
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
        print("👑 Superadmin: superadmin@example.com / SuperAdmin123!")
        print("✏️  Editor:     editor@example.com / EditorPassword123!")
        print("🎮 Desarrolladora 1: desarrolladora1@example.com / DevPassword123!")
        print("🎮 Desarrolladora 2: desarrolladora2@example.com / DevPassword123!")
        print("\n📋 Roles disponibles:")
        print("   • superadmin: Acceso completo a todas las operaciones")
        print("   • editor: Gestiona todos los videojuegos y lee desarrolladoras")
        print("   • desarrolladora: Gestiona sus propios videojuegos y desarrolladora")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
