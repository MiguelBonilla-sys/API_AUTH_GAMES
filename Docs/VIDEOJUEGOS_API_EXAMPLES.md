# 🎮 Ejemplos de Body para la API de Videojuegos

Este documento contiene ejemplos detallados de cómo usar los endpoints de videojuegos en el API_AUTH, basados en los ejemplos del proyecto FlaskAPI.

## 📋 Tabla de Contenidos

- [Autenticación](#-autenticación)
- [Endpoints de Videojuegos](#-endpoints-de-videojuegos)
- [Ejemplos de Request Body](#-ejemplos-de-request-body)
- [Ejemplos de Response](#-ejemplos-de-response)
- [Códigos de Error](#-códigos-de-error)

## 🔐 Autenticación

Todos los endpoints requieren autenticación. Incluye el token JWT en el header:

```bash
Authorization: Bearer <tu_token_jwt>
```

## 🎯 Endpoints de Videojuegos

### 1. Listar Videojuegos

**GET** `/api/videojuegos/`

**Parámetros de consulta:**
```bash
GET /api/videojuegos/?categoria=RPG&precio_min=20&precio_max=60&page=1&per_page=5
```

**Ejemplo de respuesta:**
```json
{
    "success": true,
    "message": "Videojuegos obtenidos exitosamente",
    "data": [
        {
            "id": 1,
            "nombre": "The Legend of Zelda: Breath of the Wild",
            "categoria": "Aventura",
            "precio": 59.99,
            "valoracion": 9.7,
            "desarrolladora_id": 1,
            "desarrolladora": {
                "id": 1,
                "nombre": "Nintendo",
                "pais": "Japón",
                "fundacion": 18890923,
                "sitio_web": "https://www.nintendo.com",
                "descripcion": "Compañía japonesa de videojuegos conocida por Mario, Zelda y Pokémon"
            },
            "fecha_creacion": "2024-01-15T10:30:00Z",
            "fecha_actualizacion": "2024-01-15T10:30:00Z"
        }
    ],
    "count": 5,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. Obtener Videojuego por ID

**GET** `/api/videojuegos/{id}`

**Ejemplo:**
```bash
GET /api/videojuegos/1
```

### 3. Crear Videojuego (Solo Admin)

**POST** `/api/videojuegos/`

**Ejemplo de body:**
```json
{
    "nombre": "The Witcher 3: Wild Hunt",
    "categoria": "RPG",
    "precio": 39.99,
    "valoracion": 9.3,
    "desarrolladora_id": 1
}
```

**Ejemplo de respuesta:**
```json
{
    "success": true,
    "message": "Videojuego creado exitosamente",
    "data": {
        "id": 2,
        "nombre": "The Witcher 3: Wild Hunt",
        "categoria": "RPG",
        "precio": 39.99,
        "valoracion": 9.3,
        "desarrolladora_id": 1,
        "desarrolladora": {
            "id": 1,
            "nombre": "CD Projekt Red",
            "pais": "Polonia",
            "fundacion": 19940201,
            "sitio_web": "https://www.cdprojektred.com",
            "descripcion": "Desarrolladora polaca conocida por la serie The Witcher"
        },
        "fecha_creacion": "2024-01-15T10:30:00Z",
        "fecha_actualizacion": "2024-01-15T10:30:00Z"
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### 4. Actualizar Videojuego (Solo Admin)

**PUT** `/api/videojuegos/{id}`

**Ejemplo de body:**
```json
{
    "nombre": "The Witcher 3: Wild Hunt - Complete Edition",
    "categoria": "RPG",
    "precio": 29.99,
    "valoracion": 9.5,
    "desarrolladora_id": 1
}
```

### 5. Eliminar Videojuego (Solo Admin)

**DELETE** `/api/videojuegos/{id}`

**Ejemplo:**
```bash
DELETE /api/videojuegos/1
```

**Ejemplo de respuesta:**
```json
{
    "success": true,
    "message": "Videojuego eliminado exitosamente",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### 6. Listar Categorías

**GET** `/api/videojuegos/categorias/`

**Ejemplo de respuesta:**
```json
{
    "success": true,
    "message": "Categorías obtenidas exitosamente",
    "data": ["RPG", "Acción", "Aventura", "Deportes", "Estrategia"],
    "count": 5,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### 7. Estadísticas de Videojuegos

**GET** `/api/videojuegos/estadisticas/`

**Ejemplo de respuesta:**
```json
{
    "success": true,
    "message": "Estadísticas obtenidas exitosamente",
    "data": {
        "total_videojuegos": 15,
        "categorias_unicas": 5,
        "precio_promedio": 45.99,
        "valoracion_promedio": 8.2
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### 8. Búsqueda Avanzada

**GET** `/api/videojuegos/buscar/`

**Parámetros de consulta:**
```bash
GET /api/videojuegos/buscar/?categoria=RPG&precio_min=20&precio_max=60&valoracion_min=8.0
```

## 📝 Ejemplos de Request Body

### Crear Videojuego - Ejemplo Mínimo
```json
{
    "nombre": "Nuevo Videojuego",
    "categoria": "Aventura",
    "precio": 49.99,
    "valoracion": 8.5
}
```

### Crear Videojuego - Ejemplo Completo
```json
{
    "nombre": "Cyberpunk 2077",
    "categoria": "RPG",
    "precio": 59.99,
    "valoracion": 7.5,
    "desarrolladora_id": 2
}
```

### Actualizar Videojuego - Ejemplo Parcial
```json
{
    "precio": 29.99,
    "valoracion": 9.0
}
```

### Actualizar Videojuego - Ejemplo Completo
```json
{
    "nombre": "Cyberpunk 2077 - Phantom Liberty",
    "categoria": "RPG",
    "precio": 39.99,
    "valoracion": 8.5,
    "desarrolladora_id": 2
}
```

## 📊 Ejemplos de Response

### Respuesta Exitosa - Lista
```json
{
    "success": true,
    "message": "Videojuegos obtenidos exitosamente",
    "data": [...],
    "count": 10,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Respuesta Exitosa - Elemento Único
```json
{
    "success": true,
    "message": "Videojuego obtenido exitosamente",
    "data": {
        "id": 1,
        "nombre": "The Legend of Zelda: Breath of the Wild",
        "categoria": "Aventura",
        "precio": 59.99,
        "valoracion": 9.7,
        "desarrolladora_id": 1,
        "desarrolladora": {...},
        "fecha_creacion": "2024-01-15T10:30:00Z",
        "fecha_actualizacion": "2024-01-15T10:30:00Z"
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## ❌ Códigos de Error

### 400 - Bad Request
```json
{
    "success": false,
    "message": "Error en la validación de datos del videojuego",
    "errors": [
        "El nombre es requerido",
        "El precio debe ser mayor a 0",
        "La valoración debe estar entre 0 y 10"
    ],
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### 403 - Forbidden
```json
{
    "success": false,
    "message": "No tienes permisos para crear videojuegos",
    "errors": ["Acceso denegado"],
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### 404 - Not Found
```json
{
    "success": false,
    "message": "Videojuego no encontrado",
    "errors": ["No se encontró un videojuego con el ID especificado"],
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### 500 - Internal Server Error
```json
{
    "success": false,
    "message": "Error interno del servidor",
    "errors": ["Ha ocurrido un error inesperado en el servidor"],
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔧 Validaciones

### Campos Requeridos para Crear
- `nombre`: 1-255 caracteres
- `categoria`: 1-100 caracteres
- `precio`: >= 0
- `valoracion`: 0-10

### Campos Opcionales
- `desarrolladora_id`: ID de desarrolladora existente

### Filtros Disponibles
- `categoria`: Filtrar por categoría
- `desarrolladora`: Filtrar por desarrolladora
- `buscar`: Búsqueda de texto
- `precio_min` y `precio_max`: Rango de precios
- `valoracion_min` y `valoracion_max`: Rango de valoraciones
- `page` y `per_page`: Paginación
- `ordenar` y `direccion`: Ordenamiento

## 📚 Documentación Interactiva

La documentación interactiva está disponible en:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🚀 Ejemplos de Uso con cURL

### Crear Videojuego
```bash
curl -X POST "http://localhost:8000/api/videojuegos/" \
  -H "Authorization: Bearer <tu_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Nuevo Videojuego",
    "categoria": "RPG",
    "precio": 49.99,
    "valoracion": 8.5,
    "desarrolladora_id": 1
  }'
```

### Listar Videojuegos con Filtros
```bash
curl -X GET "http://localhost:8000/api/videojuegos/?categoria=RPG&precio_min=20&precio_max=60" \
  -H "Authorization: Bearer <tu_token>"
```

### Búsqueda Avanzada
```bash
curl -X GET "http://localhost:8000/api/videojuegos/buscar/?categoria=RPG&valoracion_min=8.0" \
  -H "Authorization: Bearer <tu_token>"
```

---

## 📝 Notas Importantes

1. **Autenticación**: Todos los endpoints requieren un token JWT válido
2. **Permisos**: Los endpoints de escritura (POST, PUT, DELETE) requieren rol de administrador
3. **Validación**: Los datos se validan automáticamente usando Pydantic
4. **Desarrolladoras**: Para asociar una desarrolladora, primero consulta `/api/desarrolladoras/`
5. **Paginación**: Usa `page` y `per_page` para controlar la paginación
6. **Filtros**: Puedes combinar múltiples filtros para búsquedas específicas

---

*Documentación generada automáticamente basada en los esquemas Pydantic y ejemplos del proyecto FlaskAPI.*
