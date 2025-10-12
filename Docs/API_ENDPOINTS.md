# API Endpoints - Sistema de Roles Personalizado v2.0.0

## Resumen

Esta documentación describe todos los endpoints disponibles en el API Auth Gateway, incluyendo los nuevos endpoints públicos y el sistema de roles personalizado.

## Autenticación

### Headers Requeridos

Para endpoints protegidos, incluir el header de autorización:

```
Authorization: Bearer <jwt_token>
```

### Endpoints Públicos

Los siguientes endpoints **NO requieren autenticación**:

- `GET /api/videojuegos/*` - Todos los endpoints de lectura de videojuegos
- `GET /auth/roles` - Listar roles disponibles
- `GET /auth/roles/{role_name}/permissions` - Obtener permisos de un rol

## Endpoints de Autenticación

### POST /auth/register
**Descripción**: Registrar un nuevo usuario en el sistema.

**Acceso**: Público

**Body**:
```json
{
    "email": "usuario@ejemplo.com",
    "password": "MiPassword123!",
    "role": "desarrolladora"  // "desarrolladora", "editor", o "superadmin"
}
```

**Respuesta**:
```json
{
    "success": true,
    "message": "Usuario registrado como desarrolladora exitosamente",
    "data": {
        "id": 1,
        "email": "usuario@ejemplo.com",
        "role": "desarrolladora",
        "is_active": true,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

**Notas**:
- El primer usuario registrado automáticamente recibe rol `superadmin`
- Solo se pueden crear roles `desarrolladora` y `editor` en registro público
- Para crear `superadmin`, debe ser creado por un superadmin existente

### POST /auth/login
**Descripción**: Iniciar sesión y obtener tokens de autenticación.

**Acceso**: Público

**Body**:
```json
{
    "email": "usuario@ejemplo.com",
    "password": "MiPassword123!"
}
```

**Respuesta**:
```json
{
    "success": true,
    "message": "Login exitoso",
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer",
        "expires_in": 1800,
        "user": {
            "id": 1,
            "email": "usuario@ejemplo.com",
            "role": "desarrolladora",
            "is_active": true,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### POST /auth/refresh
**Descripción**: Renovar token de acceso usando refresh token.

**Acceso**: Público

**Body**:
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### POST /auth/logout
**Descripción**: Cerrar sesión e invalidar tokens.

**Acceso**: Requiere autenticación

### POST /auth/change-password
**Descripción**: Cambiar contraseña del usuario actual.

**Acceso**: Requiere autenticación

**Body**:
```json
{
    "current_password": "PasswordActual123!",
    "new_password": "NuevoPassword123!"
}
```

### GET /auth/roles
**Descripción**: Listar roles disponibles en el sistema.

**Acceso**: Público

**Respuesta**:
```json
{
    "success": true,
    "message": "Roles disponibles obtenidos exitosamente",
    "data": [
        {
            "id": 1,
            "name": "desarrolladora",
            "description": "Desarrolladora que puede gestionar sus propios videojuegos y desarrolladora",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        },
        {
            "id": 2,
            "name": "editor",
            "description": "Editor que puede gestionar todos los videojuegos y leer desarrolladoras",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        },
        {
            "id": 3,
            "name": "superadmin",
            "description": "Superadministrador con acceso completo a todas las operaciones del sistema",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    ],
    "count": 3,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### GET /auth/roles/{role_name}/permissions
**Descripción**: Obtener permisos específicos de un rol.

**Acceso**: Público

**Parámetros**:
- `role_name`: Nombre del rol (`desarrolladora`, `editor`, `superadmin`)

**Respuesta**:
```json
{
    "success": true,
    "message": "Permisos del rol obtenidos exitosamente",
    "data": {
        "role": {
            "id": 1,
            "name": "desarrolladora",
            "description": "Desarrolladora que puede gestionar sus propios videojuegos y desarrolladora",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        },
        "permissions": [
            {
                "name": "AUTH_LOGIN",
                "description": "Permiso para iniciar sesión"
            },
            {
                "name": "VIDEOJUEGO_READ",
                "description": "Permiso para leer videojuegos"
            },
            {
                "name": "VIDEOJUEGO_CREATE",
                "description": "Permiso para crear videojuegos"
            }
        ]
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## Endpoints de Videojuegos

### GET /api/videojuegos
**Descripción**: Listar videojuegos con filtros opcionales.

**Acceso**: Público

**Parámetros de Query**:
- `page`: Número de página (default: 1)
- `per_page`: Elementos por página (default: 10)
- `categoria`: Filtrar por categoría
- `desarrolladora`: Filtrar por desarrolladora
- `precio_min`: Precio mínimo
- `precio_max`: Precio máximo
- `ordenar`: Campo para ordenar (`titulo`, `precio`, `fecha_lanzamiento`)
- `direccion`: Dirección de ordenamiento (`asc`, `desc`)

**Ejemplo**:
```
GET /api/videojuegos?categoria=Action&precio_max=50&ordenar=precio&direccion=asc
```

**Respuesta**:
```json
{
    "success": true,
    "message": "Videojuegos obtenidos exitosamente",
    "data": [
        {
            "id": 1,
            "titulo": "Cyberpunk 2077",
            "desarrolladora": "CD Projekt Red",
            "categoria": "RPG",
            "precio": 59.99,
            "fecha_lanzamiento": "2020-12-10",
            "descripcion": "Un RPG de mundo abierto ambientado en Night City",
            "imagen_url": "https://example.com/cyberpunk.jpg"
        }
    ],
    "count": 1,
    "pagination": {
        "page": 1,
        "per_page": 10,
        "total": 1,
        "pages": 1,
        "has_next": false,
        "has_prev": false
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### GET /api/videojuegos/{videojuego_id}
**Descripción**: Obtener videojuego por ID.

**Acceso**: Público

**Parámetros**:
- `videojuego_id`: ID del videojuego

**Respuesta**:
```json
{
    "success": true,
    "message": "Videojuego obtenido exitosamente",
    "data": {
        "id": 1,
        "titulo": "Cyberpunk 2077",
        "desarrolladora": "CD Projekt Red",
        "categoria": "RPG",
        "precio": 59.99,
        "fecha_lanzamiento": "2020-12-10",
        "descripcion": "Un RPG de mundo abierto ambientado en Night City",
        "imagen_url": "https://example.com/cyberpunk.jpg",
        "owner_email": "desarrolladora@ejemplo.com",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### GET /api/videojuegos/categorias/
**Descripción**: Listar todas las categorías disponibles.

**Acceso**: Público

**Respuesta**:
```json
{
    "success": true,
    "message": "Categorías obtenidas exitosamente",
    "data": ["Action", "RPG", "Strategy", "Simulation", "Sports"],
    "count": 5,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### GET /api/videojuegos/estadisticas/
**Descripción**: Obtener estadísticas generales de videojuegos.

**Acceso**: Público

**Respuesta**:
```json
{
    "success": true,
    "message": "Estadísticas obtenidas exitosamente",
    "data": {
        "total_videojuegos": 150,
        "categorias": 8,
        "desarrolladoras": 25,
        "precio_promedio": 35.50,
        "precio_minimo": 9.99,
        "precio_maximo": 89.99,
        "videojuegos_por_categoria": {
            "Action": 45,
            "RPG": 30,
            "Strategy": 25,
            "Simulation": 20,
            "Sports": 15,
            "Adventure": 10,
            "Puzzle": 3,
            "Racing": 2
        }
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### GET /api/videojuegos/buscar/
**Descripción**: Buscar videojuegos por término de búsqueda.

**Acceso**: Público

**Parámetros de Query**:
- `q`: Término de búsqueda (requerido)
- `page`: Número de página (default: 1)
- `per_page`: Elementos por página (default: 10)

**Ejemplo**:
```
GET /api/videojuegos/buscar/?q=cyberpunk&page=1&per_page=5
```

### POST /api/videojuegos
**Descripción**: Crear nuevo videojuego.

**Acceso**: Editor, Superadmin

**Body**:
```json
{
    "titulo": "Nuevo Videojuego",
    "desarrolladora": "Mi Desarrolladora",
    "categoria": "Action",
    "precio": 29.99,
    "fecha_lanzamiento": "2024-06-01",
    "descripcion": "Descripción del videojuego",
    "imagen_url": "https://example.com/imagen.jpg"
}
```

**Respuesta**:
```json
{
    "success": true,
    "message": "Videojuego creado exitosamente",
    "data": {
        "id": 151,
        "titulo": "Nuevo Videojuego",
        "desarrolladora": "Mi Desarrolladora",
        "categoria": "Action",
        "precio": 29.99,
        "fecha_lanzamiento": "2024-06-01",
        "descripcion": "Descripción del videojuego",
        "imagen_url": "https://example.com/imagen.jpg",
        "owner_email": "editor@ejemplo.com",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### PUT /api/videojuegos/{videojuego_id}
**Descripción**: Actualizar videojuego existente.

**Acceso**: 
- Editor: Todos los videojuegos
- Superadmin: Todos los videojuegos
- Desarrolladora: Solo sus propios videojuegos

**Parámetros**:
- `videojuego_id`: ID del videojuego

**Body** (campos opcionales):
```json
{
    "titulo": "Título Actualizado",
    "precio": 39.99,
    "descripcion": "Nueva descripción"
}
```

### DELETE /api/videojuegos/{videojuego_id}
**Descripción**: Eliminar videojuego.

**Acceso**: 
- Editor: Todos los videojuegos
- Superadmin: Todos los videojuegos
- Desarrolladora: Solo sus propios videojuegos

**Parámetros**:
- `videojuego_id`: ID del videojuego

## Endpoints de Desarrolladoras

### GET /api/desarrolladoras
**Descripción**: Listar desarrolladoras.

**Acceso**: Desarrolladora, Editor, Superadmin

**Parámetros de Query**:
- `page`: Número de página (default: 1)
- `per_page`: Elementos por página (default: 10)
- `nombre`: Filtrar por nombre
- `pais`: Filtrar por país

### GET /api/desarrolladoras/{desarrolladora_id}
**Descripción**: Obtener desarrolladora por ID.

**Acceso**: Desarrolladora, Editor, Superadmin

### POST /api/desarrolladoras
**Descripción**: Crear nueva desarrolladora.

**Acceso**: Desarrolladora, Superadmin

**Body**:
```json
{
    "nombre": "Mi Desarrolladora",
    "pais": "España",
    "fecha_fundacion": "2020-01-01",
    "descripcion": "Desarrolladora independiente",
    "sitio_web": "https://midesarrolladora.com",
    "logo_url": "https://example.com/logo.jpg"
}
```

### PUT /api/desarrolladoras/{desarrolladora_id}
**Descripción**: Actualizar desarrolladora.

**Acceso**: 
- Superadmin: Todas las desarrolladoras
- Desarrolladora: Solo su propia desarrolladora

### DELETE /api/desarrolladoras/{desarrolladora_id}
**Descripción**: Eliminar desarrolladora.

**Acceso**: 
- Superadmin: Todas las desarrolladoras
- Desarrolladora: Solo su propia desarrolladora

## Endpoints de Administración

### GET /admin/users
**Descripción**: Listar todos los usuarios.

**Acceso**: Solo Superadmin

**Parámetros de Query**:
- `page`: Número de página (default: 1)
- `per_page`: Elementos por página (default: 10)
- `role`: Filtrar por rol
- `is_active`: Filtrar por estado activo

### GET /admin/users/{user_id}
**Descripción**: Obtener usuario por ID.

**Acceso**: Solo Superadmin

### POST /admin/users
**Descripción**: Crear nuevo usuario.

**Acceso**: Solo Superadmin

**Body**:
```json
{
    "email": "nuevo@usuario.com",
    "password": "Password123!",
    "role": "editor",
    "is_active": true
}
```

### PUT /admin/users/{user_id}
**Descripción**: Actualizar usuario.

**Acceso**: Solo Superadmin

**Body** (campos opcionales):
```json
{
    "email": "nuevo@email.com",
    "role": "superadmin",
    "is_active": false
}
```

### DELETE /admin/users/{user_id}
**Descripción**: Eliminar usuario.

**Acceso**: Solo Superadmin

### GET /admin/roles
**Descripción**: Listar todos los roles.

**Acceso**: Solo Superadmin

### POST /admin/roles
**Descripción**: Crear nuevo rol.

**Acceso**: Solo Superadmin

**Body**:
```json
{
    "name": "nuevo_rol",
    "description": "Descripción del nuevo rol"
}
```

### PUT /admin/roles/{role_id}
**Descripción**: Actualizar rol.

**Acceso**: Solo Superadmin

### DELETE /admin/roles/{role_id}
**Descripción**: Eliminar rol.

**Acceso**: Solo Superadmin

## Códigos de Estado HTTP

| Código | Descripción | Cuándo Ocurre |
|--------|-------------|---------------|
| 200 | OK | Operación exitosa |
| 201 | Created | Recurso creado exitosamente |
| 400 | Bad Request | Datos de entrada inválidos |
| 401 | Unauthorized | Token inválido o faltante |
| 403 | Forbidden | Permisos insuficientes |
| 404 | Not Found | Recurso no encontrado |
| 409 | Conflict | Conflicto (ej: email ya existe) |
| 422 | Unprocessable Entity | Error de validación |
| 500 | Internal Server Error | Error interno del servidor |

## Ejemplos de Uso

### Flujo Completo de Usuario Desarrolladora

1. **Registro**:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dev@ejemplo.com",
    "password": "DevPassword123!",
    "role": "desarrolladora"
  }'
```

2. **Login**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dev@ejemplo.com",
    "password": "DevPassword123!"
  }'
```

3. **Crear desarrolladora**:
```bash
curl -X POST http://localhost:8000/api/desarrolladoras \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "nombre": "Mi Desarrolladora",
    "pais": "España",
    "descripcion": "Desarrolladora independiente"
  }'
```

4. **Crear videojuego**:
```bash
curl -X POST http://localhost:8000/api/videojuegos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "titulo": "Mi Videojuego",
    "desarrolladora": "Mi Desarrolladora",
    "categoria": "Action",
    "precio": 29.99
  }'
```

### Acceso Público a Videojuegos

```bash
# Listar videojuegos (sin autenticación)
curl http://localhost:8000/api/videojuegos

# Buscar videojuegos (sin autenticación)
curl "http://localhost:8000/api/videojuegos/buscar/?q=action"

# Obtener estadísticas (sin autenticación)
curl http://localhost:8000/api/videojuegos/estadisticas/
```

## Notas Importantes

1. **Endpoints Públicos**: Los endpoints GET de videojuegos son completamente públicos y no requieren autenticación.

2. **Validación de Propiedad**: Las desarrolladoras solo pueden modificar/eliminar recursos que les pertenecen.

3. **Primer Usuario**: El primer usuario registrado automáticamente recibe el rol `superadmin`.

4. **Tokens JWT**: Los tokens de acceso expiran en 30 minutos. Use el refresh token para renovarlos.

5. **Rate Limiting**: Los endpoints pueden tener límites de velocidad configurados.

6. **CORS**: La API está configurada para aceptar requests desde dominios específicos.

7. **Logs**: Todas las operaciones se registran para auditoría y debugging.

8. **Validación**: Todos los inputs se validan antes del procesamiento.

9. **Seguridad**: Las contraseñas se hashean usando bcrypt con rounds configurables.

10. **Documentación**: La documentación interactiva está disponible en `/docs` (Swagger UI) y `/redoc`.
