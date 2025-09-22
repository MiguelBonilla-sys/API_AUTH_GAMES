"""
Aplicación principal FastAPI para el gateway de autenticación.
Configuración básica para testing de los endpoints implementados.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import time
import logging
from contextlib import asynccontextmanager

from src.config import init_db, close_db
from src.routers import auth_router, admin_router, videojuegos_router, desarrolladoras_router
from src.schemas import ErrorResponse

# Constantes
APP_NAME = "API Auth Gateway"
APP_VERSION = "1.0.0"

# Configurar logger para endpoints
endpoint_logger = logging.getLogger("endpoints")
endpoint_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - 🌐 %(message)s', datefmt='%H:%M:%S')
handler.setFormatter(formatter)
endpoint_logger.addHandler(handler)
endpoint_logger.propagate = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación.
    Inicializa y cierra la base de datos.
    """
    try:
        # Inicializar base de datos
        await init_db()
        print("✅ Base de datos inicializada")
        
        yield
        
    except Exception as e:
        print(f"⚠️ Error durante el ciclo de vida: {e}")
    finally:
        try:
            # Cerrar base de datos
            await close_db()
            print("✅ Base de datos cerrada")
        except Exception as e:
            print(f"⚠️ Error al cerrar base de datos: {e}")


# Crear aplicación FastAPI
app = FastAPI(
    title=APP_NAME,
    description="Gateway de autenticación para la API de videojuegos",
    version=APP_VERSION,
    lifespan=lifespan
)

# Middleware para logging de endpoints
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log del request
    endpoint_logger.info(f"{request.method} {request.url.path} - Usuario: {request.client.host}")
    
    # Procesar request
    response = await call_next(request)
    
    # Log del response
    process_time = time.time() - start_time
    
    # Determinar emoji según status code
    if 200 <= response.status_code < 300:
        status_emoji = "✅"
    elif response.status_code >= 400:
        status_emoji = "❌"
    else:
        status_emoji = "⚠️"
    
    endpoint_logger.info(f"{status_emoji} {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
    
    return response

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(videojuegos_router)
app.include_router(desarrolladoras_router)


@app.get("/", summary="Health Check", description="Verificar estado de la aplicación")
async def root():
    """
    Endpoint de health check.
    """
    return {
        "success": True,
        "message": "API Auth Gateway funcionando correctamente",
        "data": {
            "service": APP_NAME,
            "version": APP_VERSION,
            "status": "healthy"
        },
        "timestamp": None
    }


@app.get("/health", summary="Health Check Detallado", description="Verificar estado detallado de la aplicación")
async def health_check():
    """
    Health check detallado.
    """
    return {
        "success": True,
        "message": "Servicio funcionando correctamente",
        "data": {
            "service": APP_NAME,
            "version": APP_VERSION,
            "status": "healthy",
            "database": "connected",
            "endpoints": {
                "auth": "/auth/",
                "admin": "/admin/",
                "videojuegos": "/api/videojuegos/",
                "desarrolladoras": "/api/desarrolladoras/"
            }
        },
        "timestamp": None
    }


# Manejo global de errores
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Manejar errores HTTP de forma consistente.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "data": None,
            "timestamp": None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Manejar errores generales.
    """
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Error interno del servidor",
            "data": None,
            "timestamp": None
        }
    )


if __name__ == "__main__":
    # Configuración para desarrollo
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=False,  # Usamos middleware personalizado para logs más limpios
        reload_includes=["*.py"],  # Solo recargar archivos Python
        reload_excludes=["tests/*", "Test/*", "*.pyc", "__pycache__"]  # Excluir archivos innecesarios
    )
