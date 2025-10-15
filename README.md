# API Auth Gateway - Sistema de Roles Personalizado v2.0.0

## Resumen

API Gateway de autenticación y autorización con sistema de roles personalizado para gestión de videojuegos y desarrolladoras. Implementa control de acceso granular con 3 roles principales y endpoints públicos para consulta de videojuegos.

## Características Principales

### 🔐 Sistema de Autenticación
- **JWT Tokens**: Autenticación basada en tokens JWT
- **Refresh Tokens**: Renovación automática de tokens
- **Bcrypt**: Hash seguro de contraseñas
- **Validación**: Contraseñas complejas y emails válidos

### 👥 Sistema de Roles Personalizado
- **🎮 Desarrolladora**: Gestiona sus propios videojuegos y desarrolladora
- **✏️ Editor**: Gestiona todos los videojuegos y lee desarrolladoras
- **👑 Superadmin**: Acceso completo a todas las operaciones

### 🌐 Endpoints Públicos
- **GET /videojuegos/\***: Acceso público sin autenticación
- **GET /auth/roles**: Información de roles disponibles
- **GET /auth/roles/{role}/permissions**: Permisos específicos por rol

### 🛡️ Seguridad
- **Validación de Propiedad**: Desarrolladoras solo pueden modificar sus recursos
- **CORS**: Configuración de orígenes permitidos
- **Rate Limiting**: Protección contra abuso
- **Logs de Auditoría**: Registro de todas las operaciones

## Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- PostgreSQL 12+
- pip

### Instalación

1. **Clonar el repositorio**:
```bash
git clone <repository-url>
cd API_AUTH
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configurar entorno**:
```bash
python Test/Inits/setup_environment.py development
```

4. **Inicializar base de datos**:
```bash
python Test/Inits/init_database.py
```

5. **Ejecutar la aplicación**:
```bash
python app.py
```

La API estará disponible en `http://localhost:8000`

## Uso Rápido

### 1. Acceso Público a Videojuegos
```bash
# Listar videojuegos (sin autenticación)
curl http://localhost:8000/api/videojuegos

# Buscar videojuegos
curl "http://localhost:8000/api/videojuegos/buscar/?q=action"

# Obtener estadísticas
curl http://localhost:8000/api/videojuegos/estadisticas/
```

### 2. Registro y Autenticación
```bash
# Registrar desarrolladora
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dev@ejemplo.com",
    "password": "DevPassword123!",
    "role": "desarrolladora"
  }'

# Iniciar sesión
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dev@ejemplo.com",
    "password": "DevPassword123!"
  }'
```

### 3. Gestión de Recursos (con autenticación)
```bash
# Crear videojuego (requiere token)
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

## Estructura del Proyecto

```
API_AUTH/
├── src/                    # Código fuente
│   ├── auth/              # Autenticación y autorización
│   ├── config/            # Configuración y base de datos
│   ├── models/            # Modelos de datos
│   ├── routers/           # Endpoints de la API
│   ├── schemas/           # Esquemas de validación
│   └── services/          # Servicios auxiliares
├── Test/                  # Tests y scripts
│   ├── Auth/             # Tests de autenticación
│   ├── Endpoints/        # Tests de endpoints
│   └── Inits/            # Scripts de inicialización
├── Docs/                 # Documentación
├── app.py               # Aplicación principal
└── requirements.txt     # Dependencias
```

## Documentación

- **[Sistema de Roles y Permisos](Docs/ROLES_AND_PERMISSIONS.md)**: Documentación completa del sistema de roles
- **[API Endpoints](Docs/API_ENDPOINTS.md)**: Documentación detallada de todos los endpoints
- **[Configuración](Docs/CONFIGURATION.md)**: Guía de configuración
- **[Deployment](Docs/RAILWAY_DEPLOYMENT.md)**: Guía de despliegue en Railway

## Scripts Útiles

```bash
# Configurar entorno de desarrollo
python Test/Inits/setup_environment.py development

# Configurar entorno de producción
python Test/Inits/setup_environment.py production

# Crear usuarios de prueba
python Test/Inits/init_database.py

# Limpiar base de datos
python Test/Inits/clean_database.py

# Ejecutar tests
pytest Test/ -v
```

## Desarrollo

### Ejecutar Tests
```bash
# Todos los tests
pytest Test/ -v

# Tests específicos
pytest Test/Auth/ -v
pytest Test/Endpoints/Public/ -v
```

### Estructura de Commits
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bugs
- `docs:` Cambios en documentación
- `test:` Agregar o modificar tests
- `chore:` Cambios en configuración o herramientas

### Branches
- `main`: Código de producción
- `release`: Preparación para release
- `feature`: Nuevas funcionalidades
- `development`: Desarrollo activo

## Despliegue

### Railway (Recomendado)
```bash
# Configurar para producción
python Test/Inits/setup_environment.py production

# Desplegar
railway deploy
```

### Docker
```bash
# Construir imagen
docker build -t api-auth-gateway .

# Ejecutar contenedor
docker run -p 8000:8000 api-auth-gateway
```

## Contribución

1. Fork el proyecto
2. Crear branch para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'feat: agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Soporte

Para soporte o preguntas:
1. Revisar la documentación en `Docs/`
2. Verificar logs de la aplicación
3. Crear un issue en el repositorio
4. Contactar al equipo de desarrollo

## Changelog

### v2.0.0 (2024-01-15)
- ✅ Sistema de roles personalizado (desarrolladora, editor, superadmin)
- ✅ Endpoints públicos para GET /videojuegos/*
- ✅ Validación de propiedad de recursos
- ✅ Manejo de errores mejorado
- ✅ Documentación completa
- ✅ Tests comprehensivos
- ✅ Scripts de inicialización actualizados

### v1.0.0 (2024-01-01)
- ✅ Sistema básico de autenticación JWT
- ✅ Roles admin/user
- ✅ Endpoints básicos de videojuegos
- ✅ Integración con API Flask
