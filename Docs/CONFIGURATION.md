# 🔧 Configuración del API Auth Gateway

Este documento explica cómo configurar el API Auth Gateway para diferentes entornos.

## 📋 Tabla de Contenidos

- [Configuración Rápida](#configuración-rápida)
- [Variables de Entorno](#variables-de-entorno)
- [Configuración por Entorno](#configuración-por-entorno)
- [Configuración Avanzada](#configuración-avanzada)
- [Despliegue](#despliegue)
- [Troubleshooting](#troubleshooting)

## 🚀 Configuración Rápida

### Para Desarrollo

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd API_AUTH

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar entorno automáticamente
python setup_environment.py development

# 5. Inicializar base de datos
python init_database.py

# 6. Ejecutar servidor
python app.py
```

### Para Producción

```bash
# 1. Configurar entorno de producción
python setup_environment.py production

# 2. Crear archivos de despliegue
python deploy.py

# 3. Desplegar con Docker
docker-compose up -d

# O desplegar con systemd
sudo systemctl start api-auth-gateway
```

## 🔐 Variables de Entorno

### Variables Críticas (Requeridas)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | URL de conexión a PostgreSQL | `postgresql+asyncpg://user:pass@host:5432/db` |
| `JWT_SECRET_KEY` | Clave secreta para JWT (min 32 chars) | `a1b2c3d4e5f6...` |
| `FLASK_API_URL` | URL de la API Flask externa | `https://api.example.com` |

### Variables de Aplicación

| Variable | Tipo | Defecto | Descripción |
|----------|------|---------|-------------|
| `APP_NAME` | string | `"API Auth Gateway"` | Nombre de la aplicación |
| `APP_VERSION` | string | `"1.0.0"` | Versión de la aplicación |
| `ENVIRONMENT` | enum | `"development"` | Entorno: `development`, `staging`, `production` |
| `DEBUG` | boolean | `true` | Modo debug (solo desarrollo) |
| `TIMEZONE` | string | `"UTC"` | Zona horaria |
| `DEFAULT_LANGUAGE` | string | `"es"` | Idioma por defecto |

### Variables JWT

| Variable | Tipo | Defecto | Descripción |
|----------|------|---------|-------------|
| `JWT_ALGORITHM` | string | `"HS256"` | Algoritmo de encriptación |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | int | `30` | Expiración token acceso (min) |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | int | `7` | Expiración token renovación (días) |

### Variables CORS

| Variable | Tipo | Defecto | Descripción |
|----------|------|---------|-------------|
| `CORS_ORIGINS` | string | `"http://localhost:3000,..."` | Orígenes permitidos (separados por coma) |
| `CORS_ALLOW_CREDENTIALS` | boolean | `true` | Permitir credenciales |
| `CORS_ALLOW_METHODS` | string | `"GET,POST,PUT,DELETE,OPTIONS"` | Métodos permitidos |
| `CORS_ALLOW_HEADERS` | string | `"*"` | Headers permitidos |

### Variables de Seguridad

| Variable | Tipo | Defecto | Descripción |
|----------|------|---------|-------------|
| `BCRYPT_ROUNDS` | int | `12` | Rounds de hashing bcrypt (10-15) |
| `RATE_LIMIT_PER_MINUTE` | int | `60` | Límite de requests por minuto |
| `HTTP_TIMEOUT` | int | `30` | Timeout para requests HTTP (seg) |
| `MAX_REQUEST_SIZE` | int | `10485760` | Tamaño máximo request body (bytes) |

### Variables de Servidor

| Variable | Tipo | Defecto | Descripción |
|----------|------|---------|-------------|
| `HOST` | string | `"0.0.0.0"` | Host del servidor |
| `PORT` | int | `8000` | Puerto del servidor |
| `WORKERS` | int | `4` | Número de workers (producción) |

### Variables de Logging

| Variable | Tipo | Defecto | Descripción |
|----------|------|---------|-------------|
| `LOG_LEVEL` | enum | `"INFO"` | Nivel: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `LOG_FORMAT` | string | `"%(asctime)s - %(name)s..."` | Formato de logs |

## 🌍 Configuración por Entorno

### Development

```bash
# Configuración automática
python setup_environment.py development
```

**Características:**
- Debug habilitado
- Documentación automática visible
- Recarga automática de código
- Logs detallados (DEBUG)
- Base de datos local

### Staging

```bash
# Configuración automática
python setup_environment.py staging
```

**Características:**
- Debug deshabilitado
- Documentación visible para testing
- Sin recarga automática
- Logs informativos
- Base de datos de staging

### Production

```bash
# Configuración automática
python setup_environment.py production
```

**Características:**
- Debug deshabilitado
- Documentación oculta
- Sin recarga automática
- Logs de warning/error únicamente
- Bcrypt rounds aumentado (14)
- Rate limiting más estricto
- Base de datos de producción

## ⚙️ Configuración Avanzada

### Configuración de Base de Datos

#### PostgreSQL Local
```bash
# Instalar PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Crear base de datos
sudo -u postgres psql
CREATE DATABASE api_auth_games;
CREATE USER api_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE api_auth_games TO api_user;
```

#### PostgreSQL en Railway
```env
DATABASE_URL=postgresql+asyncpg://postgres:password@host.railway.app:5432/railway
```

#### PostgreSQL en Docker
```yaml
# docker-compose.yml
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: api_auth_games
      POSTGRES_USER: api_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
```

### Configuración JWT Avanzada

#### Generar Clave Secreta Segura
```python
import secrets
secret_key = secrets.token_hex(32)
print(f"JWT_SECRET_KEY={secret_key}")
```

#### Configuración de Múltiples Claves (Rotación)
```python
# Para implementar rotación de claves JWT
JWT_SECRET_KEYS = [
    "current_key_here",
    "previous_key_here"  # Para validar tokens antiguos
]
```

### Configuración CORS Avanzada

#### Desarrollo Local
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000
```

#### Producción con Dominios Específicos
```env
CORS_ORIGINS=https://myapp.com,https://www.myapp.com,https://admin.myapp.com
```

#### Configuración Restrictiva
```env
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE
CORS_ALLOW_HEADERS=Content-Type,Authorization,X-Requested-With
```

### Configuración de Logging Avanzada

#### Logging a Archivo
```python
# En settings_complete.py, agregar:
LOG_FILE = "/var/log/api-auth-gateway/app.log"
LOG_ROTATION = "daily"
LOG_RETENTION = "30 days"
```

#### Logging Estructurado (JSON)
```env
LOG_FORMAT={"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}
```

## 🚀 Despliegue

### Opción 1: Docker Compose (Recomendado)

```bash
# 1. Crear archivos de despliegue
python deploy.py

# 2. Configurar variables de entorno
cp env.template .env
# Editar .env con valores de producción

# 3. Desplegar
docker-compose up -d

# 4. Verificar
docker-compose logs -f api-auth-gateway
```

### Opción 2: Systemd Service

```bash
# 1. Crear archivos de despliegue
python deploy.py

# 2. Instalar servicio
sudo cp api-auth-gateway.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable api-auth-gateway

# 3. Iniciar servicio
sudo systemctl start api-auth-gateway

# 4. Verificar estado
sudo systemctl status api-auth-gateway
```

### Opción 3: Manual con Gunicorn

```bash
# 1. Instalar Gunicorn
pip install gunicorn

# 2. Crear configuración
python deploy.py

# 3. Ejecutar
python -m gunicorn -c gunicorn.conf.py app:app
```

### Nginx como Proxy Reverso

```nginx
# /etc/nginx/sites-available/api-auth-gateway
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔍 Troubleshooting

### Problemas Comunes

#### Error: "Database connection failed"
```bash
# Verificar URL de base de datos
python -c "from src.config.settings_complete import get_settings; print(get_settings().database_url)"

# Probar conexión
python -c "import asyncpg; asyncpg.connect('postgresql://...')"
```

#### Error: "JWT secret key too short"
```bash
# Generar nueva clave
python -c "import secrets; print(f'JWT_SECRET_KEY={secrets.token_hex(32)}')"
```

#### Error: "CORS policy"
```bash
# Verificar orígenes CORS
python -c "from src.config.settings_complete import get_settings; print(get_settings().cors_origins)"
```

#### Error: "Permission denied"
```bash
# Verificar permisos de archivos
chmod +x app.py setup_environment.py deploy.py

# Verificar usuario del servicio
sudo systemctl edit api-auth-gateway
# Agregar:
# [Service]
# User=your-user
# Group=your-group
```

### Logs y Debugging

#### Ver Logs del Servicio
```bash
# Systemd
sudo journalctl -u api-auth-gateway -f

# Docker
docker-compose logs -f api-auth-gateway

# Archivos de log
tail -f /var/log/api-auth-gateway/app.log
```

#### Debug Mode
```env
# Solo para desarrollo
DEBUG=true
LOG_LEVEL=DEBUG
```

#### Verificar Configuración
```bash
# Validar configuración
python setup_environment.py

# Probar endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

### Monitoreo

#### Health Checks
```bash
# Health check básico
curl http://localhost:8000/health

# Health check detallado
curl http://localhost:8000/health | jq
```

#### Métricas (Prometheus)
```env
ENABLE_METRICS=true
```

```bash
# Ver métricas
curl http://localhost:8000/metrics
```

## 📚 Referencias

- [FastAPI Configuration](https://fastapi.tiangolo.com/advanced/settings/)
- [Pydantic Settings](https://pydantic-docs.helpmanual.io/usage/settings/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [JWT Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Nginx Configuration](https://nginx.org/en/docs/)

## 🆘 Soporte

Si encuentras problemas:

1. Revisa este documento de configuración
2. Verifica los logs de la aplicación
3. Ejecuta el script de validación: `python setup_environment.py`
4. Consulta la documentación de la API: `http://localhost:8000/docs`
