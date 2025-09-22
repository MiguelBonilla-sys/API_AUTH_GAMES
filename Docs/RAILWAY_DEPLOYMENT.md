# Despliegue en Railway

Esta guía te ayudará a desplegar el API Auth Gateway en Railway.

## Archivos de Configuración

### Archivos Principales
- `app.py` - Aplicación FastAPI (funciona en desarrollo y Railway)
- `railway.json` - Configuración de despliegue de Railway
- `Procfile` - Comando de inicio para Railway
- `env.example` - Variables de entorno de ejemplo

### Archivos de Dependencias
- `requirements.txt` - Dependencias de Python (ya configurado)

## Pasos para el Despliegue

### 1. Preparar el Repositorio
```bash
# Asegúrate de que todos los archivos estén en el repositorio
git add .
git commit -m "Preparar proyecto para Railway"
git push origin main
```

### 2. Crear Proyecto en Railway
1. Ve a [Railway.app](https://railway.app)
2. Inicia sesión con tu cuenta de GitHub
3. Haz clic en "New Project"
4. Selecciona "Deploy from GitHub repo"
5. Elige tu repositorio `API_AUTH`

### 3. Configurar Base de Datos
1. En tu proyecto de Railway, haz clic en "New"
2. Selecciona "Database" → "PostgreSQL"
3. Railway creará automáticamente la variable `DATABASE_URL`

### 4. Configurar Variables de Entorno
En la pestaña "Variables" de tu servicio, configura:

#### Variables Obligatorias
```env
ENVIRONMENT=production
DEBUG=false
JWT_SECRET_KEY=tu-clave-secreta-muy-larga-y-segura-para-jwt-2024
```

#### Variables Opcionales
```env
CORS_ORIGINS=https://tu-dominio-frontend.vercel.app,https://tu-dominio-frontend.netlify.app
LOG_LEVEL=INFO
BCRYPT_ROUNDS=12
RATE_LIMIT_PER_MINUTE=60
HTTP_TIMEOUT=30
```

### 5. Configurar Dominio (Opcional)
1. En la pestaña "Settings" de tu servicio
2. Haz clic en "Generate Domain" para obtener un dominio público
3. O configura un dominio personalizado

## Configuración Automática

Railway detectará automáticamente:
- **Python** como runtime
- **requirements.txt** para dependencias
- **Procfile** para el comando de inicio
- **railway.json** para configuración específica

## Variables de Entorno Automáticas

Railway proporciona automáticamente:
- `PORT` - Puerto donde debe ejecutarse la aplicación
- `DATABASE_URL` - URL de conexión a PostgreSQL (si tienes una base de datos)

## Estructura de Archivos para Railway

```
API_AUTH/
├── app.py                # Aplicación principal (desarrollo + Railway)
├── railway.json          # Configuración de despliegue
├── Procfile             # Comando de inicio
├── requirements.txt     # Dependencias
├── env.example         # Variables de entorno de ejemplo
├── src/                # Código fuente
└── Docs/
    └── RAILWAY_DEPLOYMENT.md  # Esta documentación
```

## Comandos de Inicio

Railway usará uno de estos comandos (en orden de prioridad):
1. `startCommand` en `railway.json`
2. `web` en `Procfile`
3. Detección automática de `app.py` o `main.py`

## Health Checks

Railway configurará automáticamente health checks en:
- `GET /health` - Health check detallado
- `GET /` - Health check básico

## Monitoreo y Logs

- **Logs**: Disponibles en la pestaña "Deployments" → "View Logs"
- **Métricas**: Disponibles en la pestaña "Metrics"
- **Health Checks**: Automáticos cada 30 segundos

## Troubleshooting

### Error de Base de Datos
```bash
# Verificar que DATABASE_URL esté configurada
echo $DATABASE_URL
```

### Error de Puerto
```bash
# Railway proporciona PORT automáticamente
# No configures PORT manualmente
```

### Error de Dependencias
```bash
# Verificar requirements.txt
pip install -r requirements.txt
```

### Error de CORS
```bash
# Configurar CORS_ORIGINS con tu dominio frontend
CORS_ORIGINS=https://tu-dominio.vercel.app
```

## URLs de la API

Una vez desplegado, tu API estará disponible en:
- `https://tu-proyecto.railway.app/` - Health check
- `https://tu-proyecto.railway.app/health` - Health check detallado
- `https://tu-proyecto.railway.app/docs` - Documentación (solo en desarrollo)
- `https://tu-proyecto.railway.app/auth/` - Endpoints de autenticación
- `https://tu-proyecto.railway.app/api/` - Endpoints de la API

## Seguridad en Producción

### Variables de Entorno Críticas
- `JWT_SECRET_KEY` - Debe ser una cadena larga y aleatoria
- `ENVIRONMENT=production` - Para deshabilitar debug
- `DEBUG=false` - Para deshabilitar modo debug

### Configuración CORS
- Configura `CORS_ORIGINS` con solo los dominios que necesites
- No uses `*` en producción

### Base de Datos
- Railway proporciona `DATABASE_URL` automáticamente
- No expongas credenciales de base de datos

## Actualizaciones

Para actualizar tu aplicación:
1. Haz push a tu repositorio
2. Railway detectará los cambios automáticamente
3. Se ejecutará un nuevo despliegue

## Rollback

Si necesitas hacer rollback:
1. Ve a "Deployments" en Railway
2. Selecciona una versión anterior
3. Haz clic en "Redeploy"

## Costos

Railway ofrece:
- **Plan Gratuito**: $5 de crédito mensual
- **Plan Pro**: $20/mes por servicio
- **Base de datos**: Incluida en el plan

Consulta [Railway Pricing](https://railway.app/pricing) para más detalles.
