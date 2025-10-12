"""
Script para limpiar la base de datos.
Elimina todos los usuarios y roles, dejando la BD limpia.
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import AsyncSessionLocal, init_db
from src.models import User, Role, Token


async def clean_database():
    """Limpiar completamente la base de datos."""
    async with AsyncSessionLocal() as session:
        try:
            print("🧹 Limpiando base de datos...")
            
            # Eliminar todos los tokens
            print("🗑️  Eliminando tokens...")
            await session.execute("DELETE FROM tokens")
            
            # Eliminar todos los usuarios
            print("🗑️  Eliminando usuarios...")
            await session.execute("DELETE FROM users")
            
            # Eliminar todos los roles
            print("🗑️  Eliminando roles...")
            await session.execute("DELETE FROM roles")
            
            await session.commit()
            print("✅ Base de datos limpiada correctamente")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error al limpiar base de datos: {e}")
            raise


async def reset_database():
    """Reiniciar completamente la base de datos."""
    try:
        print("🔄 Reiniciando base de datos...")
        
        # Limpiar datos
        await clean_database()
        
        # Recrear tablas
        print("📊 Recreando tablas...")
        await init_db()
        
        print("\n🎉 Base de datos reiniciada correctamente!")
        print("💡 Ejecuta 'python Test/Inits/init_database.py' para crear usuarios de prueba")
        
    except Exception as e:
        print(f"❌ Error durante el reinicio: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def main():
    """Función principal."""
    print("⚠️  ADVERTENCIA: Este script eliminará TODOS los datos de la base de datos!")
    
    # Confirmar acción
    confirm = input("¿Estás seguro? Escribe 'SI' para continuar: ")
    if confirm != "SI":
        print("❌ Operación cancelada")
        return
    
    await reset_database()


if __name__ == "__main__":
    asyncio.run(main())
