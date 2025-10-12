# Guía de Despliegue en Railway - API Auth Gateway v2.0.0

## Resumen

Esta guía describe el proceso completo para desplegar el API Auth Gateway con sistema de roles personalizado en Railway.

## Prerrequisitos

- Cuenta en [Railway](https://railway.app)
- Repositorio Git con el código
- Base de datos PostgreSQL (Railway puede proporcionarla)

## Configuración Inicial

### 1. Preparar el Repositorio

```bash
# Asegurarse de estar en la rama main
git checkout main
git pull origin main

# Verificar que todos los tests pasen
pytest Test/ -v
```

### 2. Configurar Variables de Entorno

En Railway, configurar las siguientes variables de entorno:

#### Variables Obligatorias

```bash
# Entorno
ENVIRONMENT=production
DEBUG=false
RELOAD=false
SHOW_DOCS=false

# Base de datos (Railway la proporciona automáticamente)
# DATABASE_URL se configura automáticamente

# JWT
JWT_SECRET_KEY=<generar-clave-secreta-segura>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API Flask
FLASK_API_URL=https://tu-api-flask.railway.app

# CORS
CORS_ORIGINS=https://tu-frontend.vercel.app,https://tu-frontend.netlify.app

# Seguridad
BCRYPT_ROUNDS=12
RATE_LIMIT_PER_MINUTE=60
HTTP_TIMEOUT=30

# Servidor
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Logging
LOG_LEVEL=INFO
```

#### Variables Opcionales

```bash
# Monitoreo
ENABLE_METRICS=true
ENABLE_HEALTH_CHECKS=true

# Sentry (opcional)
SENTRY_DSN=https://tu-sentry-dsn
```

### 3. Generar Clave JWT Segura

```bash
# Generar clave secreta
python -c "import secrets; print(secrets.token_hex(32))"
```

## Proceso de Despliegue

### Opción 1: Despliegue desde GitHub

1. **Conectar Repositorio**:
   - Ir a Railway Dashboard
   - Click en "New Project"
   - Seleccionar "Deploy from GitHub repo"
   - Conectar tu repositorio

2. **Configurar Variables**:
   - En el proyecto, ir a "Variables"
   - Agregar todas las variables de entorno listadas arriba

3. **Configurar Base de Datos**:
   - Agregar servicio PostgreSQL
   - Railway configurará automáticamente `DATABASE_URL`

4. **Desplegar**:
   - Railway detectará automáticamente que es una aplicación Python
   - Usará el `requirements.txt` para instalar dependencias
   - Ejecutará `python app.py` para iniciar la aplicación

### Opción 2: Despliegue con Railway CLI

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Inicializar proyecto
railway init

# Configurar variables
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set JWT_SECRET_KEY=<tu-clave-secreta>
# ... configurar todas las variables

# Desplegar
railway up
```

## Configuración Post-Despliegue

### 1. Inicializar Base de Datos

```bash
# Conectar a la instancia de Railway
railway shell

# Ejecutar script de inicialización
python Test/Inits/init_database.py
```

### 2. Verificar Despliegue

```bash
# Verificar que la aplicación esté funcionando
curl https://tu-app.railway.app/health

# Verificar endpoints públicos
curl https://tu-app.railway.app/api/videojuegos

# Verificar documentación (si está habilitada)
curl https://tu-app.railway.app/docs
```

### 3. Crear Usuario Superadmin

```bash
# Registrar primer usuario (automáticamente será superadmin)
curl -X POST https://tu-app.railway.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@tu-dominio.com",
    "password": "SuperAdminPassword123!",
    "role": "desarrolladora"
  }'
```

## Configuración de Dominio Personalizado

### 1. Configurar Dominio en Railway

1. Ir a la configuración del proyecto
2. Seleccionar "Domains"
3. Agregar tu dominio personalizado
4. Configurar DNS según las instrucciones de Railway

### 2. Actualizar Variables de Entorno

```bash
# Actualizar CORS origins
CORS_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com

# Actualizar API Flask URL si es necesario
FLASK_API_URL=https://api.tu-dominio.com
```

## Monitoreo y Logs

### 1. Ver Logs en Railway

```bash
# Ver logs en tiempo real
railway logs

# Ver logs específicos
railway logs --service <nombre-del-servicio>
```

### 2. Configurar Alertas

- Configurar alertas en Railway para errores críticos
- Integrar con Sentry para monitoreo de errores
- Configurar health checks automáticos

### 3. Métricas

```bash
# Ver métricas de la aplicación
railway metrics
```

## Rollback y Recuperación

### 1. Rollback a Versión Anterior

```bash
# Ver historial de deployments
railway deployments

# Rollback a versión específica
railway rollback <deployment-id>
```

### 2. Backup de Base de Datos

```bash
# Crear backup
railway run pg_dump $DATABASE_URL > backup.sql

# Restaurar backup
railway run psql $DATABASE_URL < backup.sql
```

### 3. Recuperación de Emergencia

```bash
# Si la aplicación no responde
railway restart

# Si hay problemas con la base de datos
railway run python Test/Inits/clean_database.py
railway run python Test/Inits/init_database.py
```

## Optimizaciones de Producción

### 1. Configuración de Gunicorn

```python
# En app.py, para producción
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        workers=4,
        access_log=True,
        log_level="info"
    )
```

### 2. Configuración de Caché

```bash
# Agregar Redis para caché (opcional)
railway add redis
```

### 3. Configuración de CDN

- Configurar CDN para archivos estáticos
- Optimizar imágenes y assets
- Configurar compresión gzip

## Troubleshooting

### Problemas Comunes

**Error: "Database connection failed"**
```bash
# Verificar variables de entorno
railway variables

# Verificar conectividad
railway run python -c "import os; print(os.getenv('DATABASE_URL'))"
```

**Error: "JWT secret key not set"**
```bash
# Configurar clave JWT
railway variables set JWT_SECRET_KEY=<nueva-clave>
```

**Error: "CORS origin not allowed"**
```bash
# Actualizar CORS origins
railway variables set CORS_ORIGINS=https://tu-dominio.com
```

**Error: "Flask API not reachable"**
```bash
# Verificar URL de API Flask
railway variables set FLASK_API_URL=https://api-flask-correcta.railway.app
```

### Logs Útiles

```bash
# Ver logs de autenticación
railway logs | grep "AUTH"

# Ver logs de errores
railway logs | grep "ERROR"

# Ver logs de base de datos
railway logs | grep "DATABASE"
```

## Checklist de Despliegue

### Pre-Despliegue

- [ ] Código en rama `main`
- [ ] Tests pasando localmente
- [ ] Variables de entorno configuradas
- [ ] Base de datos PostgreSQL configurada
- [ ] Clave JWT segura generada

### Despliegue

- [ ] Aplicación desplegada en Railway
- [ ] Variables de entorno aplicadas
- [ ] Base de datos inicializada
- [ ] Health check funcionando
- [ ] Endpoints públicos accesibles

### Post-Despliegue

- [ ] Usuario superadmin creado
- [ ] Documentación accesible (si está habilitada)
- [ ] Logs funcionando correctamente
- [ ] Métricas configuradas
- [ ] Dominio personalizado configurado (si aplica)

### Verificación Final

- [ ] Registro de usuarios funcionando
- [ ] Login funcionando
- [ ] Endpoints protegidos funcionando
- [ ] Validación de roles funcionando
- [ ] Endpoints públicos funcionando
- [ ] Validación de propiedad funcionando

## Comandos Útiles

```bash
# Ver estado del proyecto
railway status

# Ver variables de entorno
railway variables

# Conectar a la base de datos
railway connect

# Ejecutar comando en el entorno de Railway
railway run python script.py

# Ver logs en tiempo real
railway logs --follow

# Reiniciar aplicación
railway restart

# Ver métricas
railway metrics

# Ver deployments
railway deployments
```

## Contacto y Soporte

Para problemas con el despliegue:

1. **Revisar logs**: `railway logs`
2. **Verificar variables**: `railway variables`
3. **Consultar documentación**: Railway Docs
4. **Contactar soporte**: Railway Support
5. **Crear issue**: En el repositorio del proyecto

## Notas Importantes

- **Sistema de Roles**: Asegurarse de que el primer usuario registrado sea superadmin
- **Endpoints Públicos**: Verificar que GET /videojuegos/* funcionen sin autenticación
- **Validación de Propiedad**: Confirmar que desarrolladoras solo puedan modificar sus recursos
- **CORS**: Configurar correctamente los orígenes permitidos
- **Logs**: Monitorear logs regularmente para detectar problemas
- **Backup**: Realizar backups regulares de la base de datos
- **Actualizaciones**: Mantener dependencias actualizadas
- **Seguridad**: Rotar claves JWT periódicamente