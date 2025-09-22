"""
Script de despliegue para producción.
Automatiza la configuración y validación para entornos de producción.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


def check_production_requirements() -> bool:
    """
    Verificar requisitos para despliegue en producción.
    
    Returns:
        True si cumple todos los requisitos
    """
    print("🔍 Verificando requisitos de producción...")
    
    checks = []
    
    # Verificar archivo .env
    env_file = Path(".env")
    checks.append(("Archivo .env", env_file.exists(), "Crear archivo .env con configuración de producción"))
    
    # Verificar variables críticas
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        critical_vars = [
            ("DATABASE_URL", "postgresql+asyncpg://" in env_content),
            ("JWT_SECRET_KEY", "your-super-secret-jwt-key" not in env_content),
            ("ENVIRONMENT=production", "ENVIRONMENT=production" in env_content),
            ("DEBUG=false", "DEBUG=false" in env_content),
        ]
        
        for var_name, is_present in critical_vars:
            checks.append((
                f"Variable {var_name}",
                is_present,
                f"Configurar {var_name} correctamente"
            ))
    
    # Verificar dependencias de producción
    try:
        import gunicorn
        checks.append(("Gunicorn", True, ""))
    except ImportError:
        checks.append(("Gunicorn", False, "Instalar: pip install gunicorn"))
    
    # Mostrar resultados
    all_ok = True
    for check_name, is_ok, fix_msg in checks:
        if is_ok:
            print(f"  ✅ {check_name}: OK")
        else:
            print(f"  ❌ {check_name}: {fix_msg}")
            all_ok = False
    
    return all_ok


def create_gunicorn_config() -> None:
    """Crear archivo de configuración para Gunicorn."""
    print("📝 Creando configuración de Gunicorn...")
    
    config_content = '''"""
Configuración de Gunicorn para API Auth Gateway.
"""

import os
from src.config.settings_complete import get_settings

# Obtener configuración
settings = get_settings()

# Configuración del servidor
bind = f"{settings.host}:{settings.port}"
workers = settings.workers
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Configuración de logging
loglevel = settings.log_level.lower()
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configuración de proceso
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# Configuración de seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configuración de timeout
timeout = 30
keepalive = 5
graceful_timeout = 30

# Configuración de reinicio
preload_app = True
reload = False

# Hooks
def on_starting(server):
    """Hook ejecutado al iniciar el servidor."""
    server.log.info("🚀 Iniciando API Auth Gateway...")

def on_reload(server):
    """Hook ejecutado al recargar el servidor."""
    server.log.info("🔄 Recargando API Auth Gateway...")

def worker_int(worker):
    """Hook ejecutado cuando un worker recibe SIGINT."""
    worker.log.info("🛑 Worker interrumpido")

def on_exit(server):
    """Hook ejecutado al salir del servidor."""
    server.log.info("👋 API Auth Gateway detenido")
'''
    
    with open("gunicorn.conf.py", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print("✅ Configuración de Gunicorn creada: gunicorn.conf.py")


def create_systemd_service() -> None:
    """Crear archivo de servicio systemd."""
    print("📝 Creando servicio systemd...")
    
    current_dir = os.path.abspath(".")
    python_path = sys.executable
    
    service_content = f'''[Unit]
Description=API Auth Gateway
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory={current_dir}
Environment=PATH={os.path.dirname(python_path)}
ExecStart={python_path} -m gunicorn -c gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
'''
    
    with open("api-auth-gateway.service", "w", encoding="utf-8") as f:
        f.write(service_content)
    
    print("✅ Servicio systemd creado: api-auth-gateway.service")
    print("Para instalar:")
    print("  sudo cp api-auth-gateway.service /etc/systemd/system/")
    print("  sudo systemctl daemon-reload")
    print("  sudo systemctl enable api-auth-gateway")
    print("  sudo systemctl start api-auth-gateway")


def create_docker_files() -> None:
    """Crear archivos Docker para containerización."""
    print("🐳 Creando archivos Docker...")
    
    # Dockerfile
    dockerfile_content = '''FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \\
    gcc \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Configurar directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copiar código de la aplicación
COPY . .

# Crear usuario no-root
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["python", "-m", "gunicorn", "-c", "gunicorn.conf.py", "app:app"]
'''
    
    with open("Dockerfile", "w", encoding="utf-8") as f:
        f.write(dockerfile_content)
    
    # docker-compose.yml
    compose_content = '''version: '3.8'

services:
  api-auth-gateway:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/api_auth_games
      - ENVIRONMENT=production
      - DEBUG=false
    depends_on:
      - db
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
    networks:
      - api-network

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=api_auth_games
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped
    networks:
      - api-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api-auth-gateway
    restart: unless-stopped
    networks:
      - api-network

volumes:
  postgres_data:

networks:
  api-network:
    driver: bridge
'''
    
    with open("docker-compose.yml", "w", encoding="utf-8") as f:
        f.write(compose_content)
    
    # .dockerignore
    dockerignore_content = '''.git
.gitignore
README.md
Dockerfile
docker-compose.yml
.env
.env.*
__pycache__
*.pyc
*.pyo
*.pyd
.Python
.pytest_cache
.coverage
htmlcov
.venv
venv
.DS_Store
*.log
logs/
'''
    
    with open(".dockerignore", "w", encoding="utf-8") as f:
        f.write(dockerignore_content)
    
    print("✅ Archivos Docker creados:")
    print("  - Dockerfile")
    print("  - docker-compose.yml")
    print("  - .dockerignore")


def create_nginx_config() -> None:
    """Crear configuración de nginx."""
    print("🌐 Creando configuración de nginx...")
    
    nginx_content = '''events {
    worker_connections 1024;
}

http {
    upstream api_backend {
        server api-auth-gateway:8000;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                   '$status $body_bytes_sent "$http_referer" '
                   '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain application/json application/javascript text/css;
    
    server {
        listen 80;
        server_name localhost;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        
        # API routes
        location / {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
        
        # Health check
        location /health {
            proxy_pass http://api_backend/health;
            access_log off;
        }
    }
}
'''
    
    with open("nginx.conf", "w", encoding="utf-8") as f:
        f.write(nginx_content)
    
    print("✅ Configuración de nginx creada: nginx.conf")


def create_deployment_info() -> None:
    """Crear archivo con información del despliegue."""
    deployment_info = {
        "deployment_date": datetime.now().isoformat(),
        "version": "1.0.0",
        "environment": "production",
        "python_version": sys.version,
        "files_created": [
            "gunicorn.conf.py",
            "api-auth-gateway.service",
            "Dockerfile",
            "docker-compose.yml",
            ".dockerignore",
            "nginx.conf"
        ]
    }
    
    with open("deployment-info.json", "w", encoding="utf-8") as f:
        json.dump(deployment_info, f, indent=2, ensure_ascii=False)
    
    print("✅ Información de despliegue guardada: deployment-info.json")


def main():
    """Función principal del script de despliegue."""
    print("🚀 Script de Despliegue - API Auth Gateway")
    print("=" * 50)
    
    # Verificar requisitos
    if not check_production_requirements():
        print("\n❌ No se cumplen todos los requisitos de producción")
        print("Corrija los errores antes de continuar")
        sys.exit(1)
    
    print("\n✅ Requisitos de producción verificados")
    print("\n📦 Creando archivos de despliegue...")
    
    # Crear archivos de configuración
    create_gunicorn_config()
    create_systemd_service()
    create_docker_files()
    create_nginx_config()
    create_deployment_info()
    
    print("\n🎉 Archivos de despliegue creados exitosamente!")
    print("\n📋 Opciones de despliegue:")
    print("1. Despliegue con systemd:")
    print("   - Copiar api-auth-gateway.service a /etc/systemd/system/")
    print("   - sudo systemctl enable api-auth-gateway")
    print("   - sudo systemctl start api-auth-gateway")
    print("\n2. Despliegue con Docker:")
    print("   - docker-compose up -d")
    print("\n3. Despliegue manual:")
    print("   - python -m gunicorn -c gunicorn.conf.py app:app")
    
    print("\n⚠️  Recordatorios importantes:")
    print("- Configurar SSL/TLS en nginx para HTTPS")
    print("- Configurar firewall para permitir solo puertos necesarios")
    print("- Configurar backup de la base de datos")
    print("- Configurar monitoreo y alertas")
    print("- Revisar logs regularmente")


if __name__ == "__main__":
    main()
