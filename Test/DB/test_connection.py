"""
Script simple para probar la conexión a la base de datos.
"""

import os
from src.config.settings import get_settings

def main():
    settings = get_settings()
    print(f"Database URL: {settings.database_url}")
    print(f"Environment: {settings.environment}")
    print(f"Debug: {settings.debug}")

if __name__ == "__main__":
    main()
