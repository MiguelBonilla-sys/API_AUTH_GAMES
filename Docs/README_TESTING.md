# 🧪 Testing del API Auth Gateway

Este documento explica cómo probar todos los endpoints implementados en el gateway de autenticación.

## 📋 Prerrequisitos

1. **Python 3.8+** instalado
2. **PostgreSQL** ejecutándose (local o remoto)
3. **Variables de entorno** configuradas

## 🚀 Pasos para Testing

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Base de datos
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/api_auth_games

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production-2024
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API Flask
FLASK_API_URL=https://flaskapi-production-a966.up.railway.app

# Aplicación
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
LOG_LEVEL=INFO
```

### 3. Inicializar Base de Datos

```bash
python init_database.py
```

Esto creará:
- ✅ Tablas de la base de datos
- ✅ Roles por defecto (admin, user)
- ✅ Usuarios de prueba

### 4. Ejecutar Servidor

```bash
python app.py
```

El servidor se ejecutará en `http://localhost:8000`

### 5. Ejecutar Tests

En otra terminal:

```bash
python test_endpoints.py
```

## 📊 Endpoints Disponibles

### 🔐 Autenticación (`/auth/`)

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Registrar usuario | No |
| POST | `/auth/login` | Iniciar sesión | No |
| POST | `/auth/refresh` | Renovar token | No (refresh token) |
| POST | `/auth/logout` | Cerrar sesión | Sí |
| GET | `/auth/me` | Perfil de usuario | Sí |
| POST | `/auth/change-password` | Cambiar contraseña | Sí |
| POST | `/auth/check-password-strength` | Analizar contraseña | No |

### 👑 Administración (`/admin/`)

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/admin/users` | Listar usuarios | Admin |
| GET | `/admin/users/{id}` | Obtener usuario | Admin |
| GET | `/admin/roles` | Listar roles | Admin |
| GET | `/admin/stats` | Estadísticas | Admin |
| GET | `/admin/my-permissions` | Mis permisos | Admin |

### 🎮 Videojuegos (`/api/videojuegos/`)

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/videojuegos/` | Listar videojuegos | Admin, User |
| GET | `/api/videojuegos/{id}` | Obtener videojuego | Admin, User |
| GET | `/api/videojuegos/categorias/` | Listar categorías | Admin, User |
| GET | `/api/videojuegos/estadisticas/` | Estadísticas | Admin, User |
| GET | `/api/videojuegos/buscar/` | Búsqueda avanzada | Admin, User |
| POST | `/api/videojuegos/` | Crear videojuego | Admin |
| PUT | `/api/videojuegos/{id}` | Actualizar videojuego | Admin |
| DELETE | `/api/videojuegos/{id}` | Eliminar videojuego | Admin |

### 🏢 Desarrolladoras (`/api/desarrolladoras/`)

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/desarrolladoras/` | Listar desarrolladoras | Admin, User |
| GET | `/api/desarrolladoras/{id}` | Obtener desarrolladora | Admin, User |
| GET | `/api/desarrolladoras/paises/` | Listar países | Admin, User |
| GET | `/api/desarrolladoras/estadisticas/` | Estadísticas | Admin, User |
| GET | `/api/desarrolladoras/buscar/` | Búsqueda avanzada | Admin, User |
| GET | `/api/desarrolladoras/{id}/videojuegos/` | Videojuegos de desarrolladora | Admin, User |
| POST | `/api/desarrolladoras/` | Crear desarrolladora | Admin |
| PUT | `/api/desarrolladoras/{id}` | Actualizar desarrolladora | Admin |
| DELETE | `/api/desarrolladoras/{id}` | Eliminar desarrolladora | Admin |

## 👥 Usuarios de Prueba

### Administrador
- **Email:** `admin@example.com`
- **Contraseña:** `AdminPassword123!`
- **Permisos:** Acceso completo a todos los endpoints

### Usuario Regular
- **Email:** `user@example.com`
- **Contraseña:** `UserPassword123!`
- **Permisos:** Solo lectura en videojuegos y desarrolladoras

## 🧪 Casos de Prueba

### 1. Autenticación Básica
```bash
# Registro
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "confirm_password": "TestPassword123!",
    "role": "user"
  }'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

### 2. Endpoints Protegidos
```bash
# Obtener perfil (requiere token)
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Listar videojuegos (requiere token)
curl -X GET "http://localhost:8000/api/videojuegos/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Verificación de Permisos
```bash
# Como usuario regular - debería fallar
curl -X GET "http://localhost:8000/admin/users" \
  -H "Authorization: Bearer USER_TOKEN"

# Como administrador - debería funcionar
curl -X GET "http://localhost:8000/admin/users" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

## 🔍 Verificaciones

### ✅ Funcionalidades Implementadas

1. **Autenticación JWT**
   - ✅ Registro de usuarios
   - ✅ Login con tokens
   - ✅ Renovación de tokens
   - ✅ Logout con revocación

2. **Autorización por Roles**
   - ✅ Verificación de permisos
   - ✅ Restricciones por rol
   - ✅ Middleware de autenticación

3. **Proxy a API Flask**
   - ✅ Reenvío de requests
   - ✅ Preservación de formato
   - ✅ Manejo de errores

4. **Validaciones**
   - ✅ Schemas Pydantic
   - ✅ Validación de contraseñas
   - ✅ Validación de email

### 🎯 Resultados Esperados

Al ejecutar `test_endpoints.py`, deberías ver:

```
🚀 Iniciando pruebas de la API Auth Gateway...
============================================================
🔍 Probando health check...
✅ Health check OK: API Auth Gateway funcionando correctamente

🔍 Probando análisis de fortaleza de contraseña...
✅ Análisis de contraseña: Score 6

🔍 Probando registro de usuario: test@example.com
✅ Usuario registrado: Usuario registrado exitosamente

🔍 Probando login: test@example.com
✅ Login exitoso: Login exitoso

🔍 Probando obtener perfil...
✅ Perfil obtenido: test@example.com

🔍 Probando renovación de token...
✅ Token renovado: Token renovado exitosamente

🔍 Probando listar videojuegos...
✅ Videojuegos listados: X elementos

🔍 Probando listar desarrolladoras...
✅ Desarrolladoras listadas: X elementos

🔍 Probando endpoints de administración...
✅ Acceso denegado correctamente (usuario no es admin)

🔍 Probando logout...
✅ Logout exitoso: Logout exitoso

============================================================
📊 Resumen de pruebas: 10/10 pasaron
🎉 ¡Todas las pruebas pasaron exitosamente!
```

## 🐛 Solución de Problemas

### Error de Conexión a Base de Datos
```
❌ Error: connection to server at "localhost" (127.0.0.1), port 5432 failed
```
**Solución:** Verificar que PostgreSQL esté ejecutándose y la URL de conexión sea correcta.

### Error de Token Inválido
```
❌ Token inválido: Token has expired
```
**Solución:** Hacer login nuevamente para obtener un token fresco.

### Error de Permisos
```
❌ Acceso denegado: Se requieren permisos de administrador
```
**Solución:** Usar el usuario admin (`admin@example.com`) en lugar del usuario regular.

### Error de API Flask
```
❌ No se puede conectar con la API Flask
```
**Solución:** Verificar que la URL de la API Flask sea correcta y esté accesible.

## 📝 Notas

- Los tests asumen que la API Flask está disponible en `https://flaskapi-production-a966.up.railway.app`
- Si la API Flask no está disponible, los tests de proxy fallarán pero la autenticación funcionará
- Los tokens JWT expiran en 30 minutos por defecto
- Los refresh tokens expiran en 7 días por defecto
