"""
Schemas base para respuestas de la API.
Implementa el formato estándar ApiResponse y ErrorResponse del API Flask existente.
"""

from datetime import datetime
from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """
    Schema base para todas las respuestas de la API.
    Mantiene el formato estándar del API Flask existente.
    """
    success: bool = Field(description="Indica si la operación fue exitosa")
    message: str = Field(description="Mensaje descriptivo de la respuesta")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp de la respuesta")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ApiResponse(BaseResponse):
    """
    Schema para respuestas exitosas de la API.
    Formato estándar: {success: true, message: string, data: object, count: integer, timestamp: datetime}
    """
    data: Optional[Any] = Field(default=None, description="Datos de la respuesta")
    count: Optional[int] = Field(default=None, description="Número de elementos en la respuesta")


class ErrorResponse(BaseResponse):
    """
    Schema para respuestas de error de la API.
    Formato estándar: {success: false, message: string, errors: array, timestamp: datetime}
    """
    success: bool = Field(default=False, description="Siempre false para errores")
    errors: Optional[List[Dict[str, Any]]] = Field(default=None, description="Lista de errores detallados")
    error_code: Optional[str] = Field(default=None, description="Código de error específico")
    error_type: Optional[str] = Field(default="general_error", description="Tipo de error")


class ValidationError(BaseModel):
    """
    Schema para errores de validación individuales.
    """
    field: str = Field(description="Campo que causó el error")
    message: str = Field(description="Mensaje de error específico")
    value: Optional[Any] = Field(default=None, description="Valor que causó el error")


class PaginationResponse(BaseModel):
    """
    Schema para respuestas paginadas.
    """
    page: int = Field(description="Página actual")
    per_page: int = Field(description="Elementos por página")
    total: int = Field(description="Total de elementos")
    pages: int = Field(description="Total de páginas")
    has_next: bool = Field(description="Indica si hay página siguiente")
    has_prev: bool = Field(description="Indica si hay página anterior")


class HealthCheckResponse(BaseModel):
    """
    Schema para respuesta de health check.
    """
    status: str = Field(description="Estado del servicio")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del check")
    version: Optional[str] = Field(default=None, description="Versión de la aplicación")
    database: Optional[str] = Field(default=None, description="Estado de la base de datos")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ===== SCHEMAS DE ERROR ESPECÍFICOS =====

class AuthorizationErrorResponse(ErrorResponse):
    """
    Schema para errores de autorización.
    """
    error_type: str = Field(default="authorization_error", description="Tipo de error de autorización")
    error_code: Optional[str] = Field(default=None, description="Código específico de autorización")


class PermissionErrorResponse(ErrorResponse):
    """
    Schema para errores de permisos.
    """
    error_type: str = Field(default="permission_error", description="Tipo de error de permisos")
    error_code: Optional[str] = Field(default=None, description="Código específico de permisos")
    required_permission: Optional[str] = Field(default=None, description="Permiso requerido")
    user_role: Optional[str] = Field(default=None, description="Rol del usuario actual")


class ResourceOwnershipErrorResponse(ErrorResponse):
    """
    Schema para errores de propiedad de recursos.
    """
    error_type: str = Field(default="resource_ownership_error", description="Tipo de error de propiedad")
    error_code: str = Field(default="NOT_RESOURCE_OWNER", description="Código de error de propiedad")
    resource_type: Optional[str] = Field(default=None, description="Tipo de recurso")
    resource_id: Optional[int] = Field(default=None, description="ID del recurso")


class RoleValidationErrorResponse(ErrorResponse):
    """
    Schema para errores de validación de roles.
    """
    error_type: str = Field(default="role_validation_error", description="Tipo de error de validación de rol")
    error_code: Optional[str] = Field(default=None, description="Código específico de validación")
    requested_role: Optional[str] = Field(default=None, description="Rol solicitado")
    allowed_roles: Optional[List[str]] = Field(default=None, description="Roles permitidos")
