#!/usr/bin/env python3
"""
Script para verificar la configuración de la base de datos.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def check_database_config():
    """Verificar configuración de la base de datos."""
    print("🔍 Verificando configuración de base de datos...")
    
    # Verificar variables de entorno
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        print(f"✅ DATABASE_URL encontrada: {database_url[:50]}...")
        
        # Verificar que use asyncpg
        if "+asyncpg" in database_url:
            print("✅ URL usa asyncpg (correcto)")
        else:
            print("⚠️ URL no usa asyncpg, agregando...")
            if database_url.startswith("postgresql://"):
                database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
                print(f"✅ URL corregida: {database_url[:50]}...")
    else:
        print("❌ DATABASE_URL no encontrada")
        return False
    
    # Verificar imports
    try:
        import psycopg2
        print("✅ psycopg2 disponible")
    except ImportError:
        print("❌ psycopg2 no disponible")
        return False
    
    try:
        import asyncpg
        print("✅ asyncpg disponible")
    except ImportError:
        print("❌ asyncpg no disponible")
        return False
    
    try:
        from sqlalchemy import create_engine
        print("✅ SQLAlchemy disponible")
    except ImportError:
        print("❌ SQLAlchemy no disponible")
        return False
    
    # Probar conexión
    try:
        from src.config.database import engine
        print("✅ Engine de base de datos creado correctamente")
    except Exception as e:
        print(f"❌ Error creando engine: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if check_database_config():
        print("🎉 Configuración de base de datos OK")
        sys.exit(0)
    else:
        print("❌ Problemas con la configuración de base de datos")
        sys.exit(1)
