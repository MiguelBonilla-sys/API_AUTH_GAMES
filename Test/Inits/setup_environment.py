"""
Script para configurar el entorno de desarrollo y producción.
Ayuda a generar archivos de configuración y validar la configuración.
"""

import os
import sys
import secrets
import subprocess
from pathlib import Path
from typing import Dict, Any


def generate_secret_key() -> str:
    """Generar una clave secreta segura."""
    return secrets.token_hex(32)


def create_env_file(environment: str = "development") -> None:
    """
    Crear archivo .env basado en el template.
    
    Args:
        environment: Entorno (development, staging, production)
    """
    print(f"🔧 Creando archivo .env para entorno: {environment}")
    
    # Leer template
    template_path = Path("env.template")
    if not template_path.exists():
        print("❌ Error: No se encuentra el archivo env.template")
        return
    
    # Generar valores específicos del entorno
    config_values = {
        "development": {
            "DATABASE_URL": "postgresql+asyncpg://postgres:password@localhost:5432/api_auth_games",
            "ENVIRONMENT": "development",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
            "RELOAD": "true",
            "SHOW_DOCS": "true",
        },
        "staging": {
            "DATABASE_URL": "postgresql+asyncpg://postgres:password@staging-host:5432/api_auth_games_staging",
            "ENVIRONMENT": "staging",
            "DEBUG": "false",
            "LOG_LEVEL": "INFO",
            "RELOAD": "false",
            "SHOW_DOCS": "true",
        },
        "production": {
            "DATABASE_URL": "postgresql+asyncpg://postgres:password@prod-host:5432/api_auth_games_prod",
            "ENVIRONMENT": "production",
            "DEBUG": "false",
            "LOG_LEVEL": "WARNING",
            "RELOAD": "false",
            "SHOW_DOCS": "false",
            "BCRYPT_ROUNDS": "14",
            "RATE_LIMIT_PER_MINUTE": "30",
        }
    }
    
    # Leer template
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazar valores específicos del entorno
    env_config = config_values.get(environment, config_values["development"])
    
    # Generar nueva clave secreta
    new_secret = generate_secret_key()
    content = content.replace(
        "JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production-2024",
        f"JWT_SECRET_KEY={new_secret}"
    )
    
    # Aplicar configuraciones específicas del entorno
    for key, value in env_config.items():
        # Buscar la línea en el template y reemplazarla
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}"
                break
        content = '\n'.join(lines)
    
    # Escribir archivo .env
    env_path = Path(".env")
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Archivo .env creado exitosamente")
    print(f"🔑 Nueva clave JWT generada: {new_secret[:20]}...")


def validate_environment() -> bool:
    """
    Validar la configuración del entorno.
    
    Returns:
        True si la configuración es válida
    """
    print("🔍 Validando configuración del entorno...")
    
    try:
        # Importar configuración
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from src.config.settings_complete import get_settings
        
        settings = get_settings()
        
        # Validaciones básicas
        validations = [
            ("JWT Secret Key", len(settings.jwt_secret_key) >= 32, "La clave JWT debe tener al menos 32 caracteres"),
            ("Database URL", settings.database_url.startswith("postgresql"), "La URL de base de datos debe usar PostgreSQL"),
            ("Flask API URL", settings.flask_api_url.startswith("http"), "La URL de la API Flask debe ser válida"),
            ("CORS Origins", len(settings.cors_origins) > 0, "Debe haber al menos un origen CORS configurado"),
            ("Log Level", settings.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], "Nivel de log inválido"),
            ("Bcrypt Rounds", 10 <= settings.bcrypt_rounds <= 15, "Rounds de bcrypt debe estar entre 10 y 15"),
            ("Server Port", 1 <= settings.port <= 65535, "Puerto del servidor debe estar entre 1 y 65535"),
        ]
        
        all_valid = True
        for name, is_valid, error_msg in validations:
            if is_valid:
                print(f"  ✅ {name}: OK")
            else:
                print(f"  ❌ {name}: {error_msg}")
                all_valid = False
        
        # Validaciones específicas del entorno
        if settings.is_production:
            prod_validations = [
                ("Production Debug", not settings.debug, "Debug debe estar deshabilitado en producción"),
                ("Production Docs", not settings.show_docs, "Documentación debe estar deshabilitada en producción"),
                ("Production Reload", not settings.reload, "Reload debe estar deshabilitado en producción"),
                ("Production Bcrypt", settings.bcrypt_rounds >= 12, "Bcrypt rounds debe ser al menos 12 en producción"),
            ]
            
            for name, is_valid, error_msg in prod_validations:
                if is_valid:
                    print(f"  ✅ {name}: OK")
                else:
                    print(f"  ⚠️  {name}: {error_msg}")
        
        if all_valid:
            print("✅ Configuración del entorno válida")
        else:
            print("❌ Se encontraron errores en la configuración")
        
        return all_valid
        
    except Exception as e:
        print(f"❌ Error al validar configuración: {e}")
        return False


def check_dependencies() -> bool:
    """
    Verificar que todas las dependencias estén instaladas.
    
    Returns:
        True si todas las dependencias están disponibles
    """
    print("📦 Verificando dependencias...")
    
    required_packages = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("sqlalchemy", "sqlalchemy"),
        ("asyncpg", "asyncpg"),
        ("pydantic", "pydantic"),
        ("pydantic-settings", "pydantic_settings"),
        ("python-jose", "jose"),
        ("bcrypt", "bcrypt"),
        ("httpx", "httpx"),
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"  ✅ {package_name}: OK")
        except ImportError:
            print(f"  ❌ {package_name}: No instalado")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n❌ Faltan paquetes: {', '.join(missing_packages)}")
        print("Instalar con: pip install " + " ".join(missing_packages))
        return False
    else:
        print("✅ Todas las dependencias están instaladas")
        return True


def setup_database() -> bool:
    """
    Configurar la base de datos.
    
    Returns:
        True si la configuración fue exitosa
    """
    print("🗄️  Configurando base de datos...")
    
    try:
        # Ejecutar script de inicialización
        result = subprocess.run([sys.executable, "init_database.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Base de datos configurada exitosamente")
            return True
        else:
            print(f"❌ Error al configurar base de datos: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"❌ Error al ejecutar configuración de base de datos: {e}")
        return False


def main():
    """Función principal del script de configuración."""
    print("🚀 Configurador del entorno API Auth Gateway")
    print("=" * 50)
    
    # Verificar argumentos
    environment = "development"
    if len(sys.argv) > 1:
        environment = sys.argv[1].lower()
        if environment not in ["development", "staging", "production"]:
            print("❌ Entorno inválido. Use: development, staging, o production")
            sys.exit(1)
    
    print(f"🎯 Configurando para entorno: {environment}")
    print()
    
    # Paso 1: Verificar dependencias
    if not check_dependencies():
        print("\n❌ Instale las dependencias faltantes antes de continuar")
        sys.exit(1)
    
    print()
    
    # Paso 2: Crear archivo .env
    create_env_file(environment)
    print()
    
    # Paso 3: Validar configuración
    if not validate_environment():
        print("\n⚠️  La configuración tiene errores, pero puede continuar")
    
    print()
    
    # Paso 4: Configurar base de datos (solo en development)
    if environment == "development":
        if setup_database():
            print("✅ Configuración completada exitosamente")
        else:
            print("⚠️  Configuración completada con errores en la base de datos")
    else:
        print("ℹ️  En entornos no-development, configure la base de datos manualmente")
        print("✅ Configuración completada exitosamente")
    
    print()
    print("🎉 ¡Configuración terminada!")
    print()
    print("Próximos pasos:")
    print("1. Revisar el archivo .env generado")
    print("2. Ajustar la configuración según sus necesidades")
    print("3. Ejecutar: python app.py")
    print("4. Probar la API en: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
