"""
Schemas Pydantic para videojuegos.
Basados en los ejemplos de la API Flask de videojuegos.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from .base import BaseResponse, ApiResponse, ErrorResponse


# ===== SCHEMAS DE ENTRADA (REQUEST) =====

class VideojuegoCreateRequest(BaseModel):
    """Schema para crear un nuevo videojuego."""
    
    nombre: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nombre del videojuego",
        example="The Witcher 3: Wild Hunt"
    )
    
    categoria: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Categoría del videojuego",
        example="RPG"
    )
    
    precio: float = Field(
        ...,
        ge=0,
        description="Precio del videojuego en USD",
        example=39.99
    )
    
    valoracion: float = Field(
        ...,
        ge=0,
        le=10,
        description="Valoración del videojuego (0-10)",
        example=9.3
    )
    
    desarrolladora_id: Optional[int] = Field(
        None,
        description="ID de la desarrolladora (opcional). Usar GET /api/desarrolladoras para ver las opciones disponibles.",
        example=1
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Nuevo Videojuego",
                "categoria": "Aventura",
                "precio": 49.99,
                "valoracion": 8.5,
                "desarrolladora_id": 1
            }
        }


class VideojuegoUpdateRequest(BaseModel):
    """Schema para actualizar un videojuego existente."""
    
    nombre: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Nombre del videojuego",
        example="The Witcher 3: Wild Hunt - Complete Edition"
    )
    
    categoria: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Categoría del videojuego",
        example="RPG"
    )
    
    precio: Optional[float] = Field(
        None,
        ge=0,
        description="Precio del videojuego en USD",
        example=29.99
    )
    
    valoracion: Optional[float] = Field(
        None,
        ge=0,
        le=10,
        description="Valoración del videojuego (0-10)",
        example=9.5
    )
    
    desarrolladora_id: Optional[int] = Field(
        None,
        description="ID de la desarrolladora (opcional). Usar GET /api/desarrolladoras para ver las opciones disponibles.",
        example=1
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "The Witcher 3: Wild Hunt - Complete Edition",
                "categoria": "RPG",
                "precio": 29.99,
                "valoracion": 9.5,
                "desarrolladora_id": 1
            }
        }


class VideojuegoFilterRequest(BaseModel):
    """Schema para filtros de búsqueda de videojuegos."""
    
    categoria: Optional[str] = Field(
        None,
        description="Filtrar por categoría",
        example="RPG"
    )
    
    desarrolladora: Optional[str] = Field(
        None,
        description="Filtrar por desarrolladora",
        example="Nintendo"
    )
    
    buscar: Optional[str] = Field(
        None,
        description="Búsqueda de texto en nombre, categoría y desarrolladora",
        example="zelda"
    )
    
    precio_min: Optional[float] = Field(
        None,
        ge=0,
        description="Precio mínimo",
        example=10.0
    )
    
    precio_max: Optional[float] = Field(
        None,
        ge=0,
        description="Precio máximo",
        example=60.0
    )
    
    valoracion_min: Optional[float] = Field(
        None,
        ge=0,
        le=10,
        description="Valoración mínima (0-10)",
        example=8.0
    )
    
    valoracion_max: Optional[float] = Field(
        None,
        ge=0,
        le=10,
        description="Valoración máxima (0-10)",
        example=10.0
    )
    
    desarrolladora_id: Optional[int] = Field(
        None,
        description="ID de la desarrolladora",
        example=1
    )
    
    page: Optional[int] = Field(
        1,
        ge=1,
        description="Número de página",
        example=1
    )
    
    per_page: Optional[int] = Field(
        10,
        ge=1,
        le=100,
        description="Elementos por página",
        example=10
    )
    
    ordenar: Optional[str] = Field(
        "nombre",
        description="Campo para ordenar",
        example="nombre"
    )
    
    direccion: Optional[str] = Field(
        "asc",
        description="Dirección de ordenamiento (asc/desc)",
        example="asc"
    )


# ===== SCHEMAS DE SALIDA (RESPONSE) =====

class DesarrolladoraResponse(BaseModel):
    """Schema para información de desarrolladora."""
    
    id: int = Field(..., description="ID de la desarrolladora", example=1)
    nombre: str = Field(..., description="Nombre de la desarrolladora", example="Nintendo")
    pais: Optional[str] = Field(None, description="País de origen", example="Japón")
    fundacion: Optional[int] = Field(None, description="Fecha de fundación en formato YYYYMMDD", example=18890923)
    sitio_web: Optional[str] = Field(None, description="Sitio web", example="https://www.nintendo.com")
    descripcion: Optional[str] = Field(None, description="Descripción", example="Compañía japonesa de videojuegos conocida por Mario, Zelda y Pokémon")
    fecha_creacion: Optional[datetime] = Field(None, description="Fecha de creación")
    fecha_actualizacion: Optional[datetime] = Field(None, description="Fecha de actualización")


class VideojuegoResponse(BaseModel):
    """Schema para respuesta de videojuego."""
    
    id: int = Field(..., description="ID del videojuego", example=1)
    nombre: str = Field(..., description="Nombre del videojuego", example="The Legend of Zelda: Breath of the Wild")
    categoria: str = Field(..., description="Categoría del videojuego", example="Aventura")
    precio: float = Field(..., description="Precio del videojuego", example=59.99)
    valoracion: float = Field(..., description="Valoración del videojuego", example=9.7)
    desarrolladora_id: Optional[int] = Field(None, description="ID de la desarrolladora", example=1)
    desarrolladora: Optional[DesarrolladoraResponse] = Field(None, description="Información de la desarrolladora")
    fecha_creacion: Optional[datetime] = Field(None, description="Fecha de creación")
    fecha_actualizacion: Optional[datetime] = Field(None, description="Fecha de actualización")


class VideojuegoListResponse(BaseModel):
    """Schema para lista de videojuegos."""
    
    success: bool = Field(..., description="Indica si la operación fue exitosa", example=True)
    message: str = Field(..., description="Mensaje descriptivo", example="Videojuegos obtenidos exitosamente")
    data: List[VideojuegoResponse] = Field(..., description="Lista de videojuegos")
    count: Optional[int] = Field(None, description="Número total de videojuegos", example=5)
    timestamp: Optional[datetime] = Field(None, description="Timestamp de la respuesta")


class VideojuegoDetailResponse(BaseModel):
    """Schema para detalle de videojuego."""
    
    success: bool = Field(..., description="Indica si la operación fue exitosa", example=True)
    message: str = Field(..., description="Mensaje descriptivo", example="Videojuego obtenido exitosamente")
    data: VideojuegoResponse = Field(..., description="Datos del videojuego")
    timestamp: Optional[datetime] = Field(None, description="Timestamp de la respuesta")


class VideojuegoCreateResponse(BaseModel):
    """Schema para respuesta de creación de videojuego."""
    
    success: bool = Field(..., description="Indica si la operación fue exitosa", example=True)
    message: str = Field(..., description="Mensaje descriptivo", example="Videojuego creado exitosamente")
    data: VideojuegoResponse = Field(..., description="Datos del videojuego creado")
    timestamp: Optional[datetime] = Field(None, description="Timestamp de la respuesta")


class VideojuegoUpdateResponse(BaseModel):
    """Schema para respuesta de actualización de videojuego."""
    
    success: bool = Field(..., description="Indica si la operación fue exitosa", example=True)
    message: str = Field(..., description="Mensaje descriptivo", example="Videojuego actualizado exitosamente")
    data: VideojuegoResponse = Field(..., description="Datos del videojuego actualizado")
    timestamp: Optional[datetime] = Field(None, description="Timestamp de la respuesta")


class VideojuegoDeleteResponse(BaseModel):
    """Schema para respuesta de eliminación de videojuego."""
    
    success: bool = Field(..., description="Indica si la operación fue exitosa", example=True)
    message: str = Field(..., description="Mensaje descriptivo", example="Videojuego eliminado exitosamente")
    timestamp: Optional[datetime] = Field(None, description="Timestamp de la respuesta")


class CategoriasResponse(BaseModel):
    """Schema para respuesta de categorías."""
    
    success: bool = Field(..., description="Indica si la operación fue exitosa", example=True)
    message: str = Field(..., description="Mensaje descriptivo", example="Categorías obtenidas exitosamente")
    data: List[str] = Field(..., description="Lista de categorías", example=["RPG", "Acción", "Aventura", "Deportes"])
    count: Optional[int] = Field(None, description="Número total de categorías", example=4)
    timestamp: Optional[datetime] = Field(None, description="Timestamp de la respuesta")


class EstadisticasResponse(BaseModel):
    """Schema para respuesta de estadísticas."""
    
    success: bool = Field(..., description="Indica si la operación fue exitosa", example=True)
    message: str = Field(..., description="Mensaje descriptivo", example="Estadísticas obtenidas exitosamente")
    data: Dict[str, Any] = Field(
        ...,
        description="Estadísticas de videojuegos",
        example={
            "total_videojuegos": 15,
            "categorias_unicas": 5,
            "precio_promedio": 45.99,
            "valoracion_promedio": 8.2
        }
    )
    timestamp: Optional[datetime] = Field(None, description="Timestamp de la respuesta")


# ===== SCHEMAS DE ERROR =====

class VideojuegoErrorResponse(ErrorResponse):
    """Schema para errores específicos de videojuegos."""
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Error en la validación de datos del videojuego",
                "errors": [
                    "El nombre es requerido",
                    "El precio debe ser mayor a 0",
                    "La valoración debe estar entre 0 y 10"
                ],
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class VideojuegoNotFoundResponse(ErrorResponse):
    """Schema para videojuego no encontrado."""
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Videojuego no encontrado",
                "errors": ["No se encontró un videojuego con el ID especificado"],
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
