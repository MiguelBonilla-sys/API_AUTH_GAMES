# 🐳 Configuración Completa con Docker para Railway

## ✅ Archivos Agregados

### 🐳 **Docker:**
1. **`Dockerfile`** - Imagen Docker optimizada para Railway
2. **`.dockerignore`** - Archivos a ignorar en Docker
3. **`docker-compose.yml`** - Desarrollo local con Docker
4. **`build.sh`** / **`build.bat`** - Scripts de build

### 🏥 **Health Checks Mejorados:**
- **`/health`** - Health check detallado con verificación de DB y API externa
- **`/ready`** - Readiness check para Kubernetes/Docker
- **`/`** - Health check básico

## 🚀 Configuración para Railway

### 1. **Dockerfile Optimizado:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y gcc g++ libpq-dev
# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copiar código fuente
COPY . .
# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app
# Health check integrado
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health', timeout=10)"
# Comando de inicio
CMD ["gunicorn", "app:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### 2. **Health Checks Mejorados:**

#### `/health` - Health Check Detallado:
```json
{
  "success": true,
  "message": "Servicio funcionando correctamente",
  "data": {
    "service": "API Auth Gateway",
    "version": "1.0.0",
    "environment": "production",
    "status": "healthy",
    "checks": {
      "database": "connected",
      "flask_api": "connected",
      "uptime": "running"
    }
  }
}
```

#### `/ready` - Readiness Check:
```json
{
  "success": true,
  "message": "Application is ready",
  "data": {
    "service": "API Auth Gateway",
    "version": "1.0.0",
    "status": "ready"
  }
}
```

## 🛠️ Comandos de Desarrollo

### Desarrollo Local:
```bash
# Opción 1: Python directo
python app.py

# Opción 2: Docker Compose
docker-compose up --build

# Opción 3: Docker manual
docker build -t api-auth-gateway .
docker run -p 8000:8000 api-auth-gateway
```

### Build y Deploy:
```bash
# Windows
build.bat

# Linux/Mac
./build.sh

# Railway (automático)
git push origin main
```

## 🔧 Configuración de Railway

### Variables de Entorno:
```env
ENVIRONMENT=production
DEBUG=false
JWT_SECRET_KEY=tu-clave-secreta-muy-larga-y-segura
CORS_ORIGINS=https://tu-dominio-frontend.vercel.app
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
```

### Railway.json:
```json
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30
  }
}
```

## 🏥 Health Checks

### Endpoints Disponibles:
- **`GET /`** - Health check básico
- **`GET /health`** - Health check detallado (usado por Railway)
- **`GET /ready`** - Readiness check (usado por Docker/Kubernetes)

### Verificaciones Incluidas:
- ✅ Estado de la base de datos
- ✅ Conectividad con API Flask externa
- ✅ Estado general de la aplicación
- ✅ Información de versión y entorno

## 🐳 Docker Features

### Seguridad:
- ✅ Usuario no-root
- ✅ Imagen base minimalista (python:3.11-slim)
- ✅ Dependencias del sistema mínimas

### Performance:
- ✅ Multi-stage build (opcional)
- ✅ Cache de dependencias
- ✅ Health checks integrados
- ✅ Gunicorn con 4 workers

### Monitoreo:
- ✅ Health checks automáticos
- ✅ Logs estructurados
- ✅ Métricas de rendimiento
- ✅ Timeouts configurados

## 🚀 Despliegue en Railway

### 1. **Preparar Repositorio:**
```bash
git add .
git commit -m "Agregar configuración Docker y health checks"
git push origin main
```

### 2. **Crear Proyecto en Railway:**
1. Ve a [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub repo"
3. Selecciona tu repositorio
4. Railway detectará automáticamente el Dockerfile

### 3. **Configurar Variables:**
```env
ENVIRONMENT=production
JWT_SECRET_KEY=tu-clave-secreta-muy-larga-y-segura
CORS_ORIGINS=https://tu-dominio-frontend.vercel.app
```

### 4. **¡Listo!**
Railway:
- ✅ Detectará el Dockerfile automáticamente
- ✅ Construirá la imagen Docker
- ✅ Configurará health checks en `/health`
- ✅ Desplegará con Gunicorn

## 🎯 URLs Después del Despliegue

- `https://tu-proyecto.railway.app/` - Health check básico
- `https://tu-proyecto.railway.app/health` - Health check detallado
- `https://tu-proyecto.railway.app/ready` - Readiness check
- `https://tu-proyecto.railway.app/docs` - Documentación (solo en desarrollo)
- `https://tu-proyecto.railway.app/auth/` - Endpoints de autenticación
- `https://tu-proyecto.railway.app/api/` - Endpoints de la API

## 🔍 Troubleshooting

### Docker Build Fails:
```bash
# Verificar Dockerfile
docker build -t api-auth-gateway . --no-cache

# Ver logs detallados
docker build -t api-auth-gateway . --progress=plain
```

### Health Check Fails:
```bash
# Verificar localmente
curl http://localhost:8000/health

# Ver logs de Railway
# En Railway dashboard → Deployments → View Logs
```

### Database Connection Issues:
```bash
# Verificar DATABASE_URL
echo $DATABASE_URL

# Probar conexión
python -c "from src.config.database import engine; print('DB OK')"
```

¡Tu proyecto está **100% listo** para Railway con Docker y health checks completos! 🚀🐳
