"""
Schemas Pydantic para gestión de roles.
Define modelos para operaciones CRUD de roles (solo para administradores).
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from src.schemas.base import ApiResponse, ErrorResponse

# Constantes para strings reutilizados
ROLE_NAME_DESCRIPTION = "Nombre del rol"
ROLE_DESCRIPTION_DESCRIPTION = "Descripción del rol"


# ===== SCHEMAS DE ENTRADA (REQUEST) =====

class RoleCreateRequest(BaseModel):
    """
    Schema para creación de rol (solo administradores).
    """
    name: str = Field(min_length=2, max_length=50, description=ROLE_NAME_DESCRIPTION)
    description: Optional[str] = Field(default=None, max_length=500, description=ROLE_DESCRIPTION_DESCRIPTION)
    
    @validator('name')
    def validate_name(cls, v):
        """Validar nombre del rol."""
        if not v or len(v.strip()) == 0:
            raise ValueError('El nombre del rol no puede estar vacío')
        
        # Convertir a minúsculas y reemplazar espacios con guiones bajos
        name = v.lower().strip().replace(' ', '_')
        
        # Validar que solo contenga letras, números y guiones bajos
        if not name.replace('_', '').isalnum():
            raise ValueError('El nombre del rol solo puede contener letras, números y guiones bajos')
        
        return name
    
    @validator('description')
    def validate_description(cls, v):
        """Validar descripción del rol."""
        if v is not None and len(v.strip()) == 0:
            return None
        return v.strip() if v else v


class RoleUpdateRequest(BaseModel):
    """
    Schema para actualización de rol (solo administradores).
    """
    name: Optional[str] = Field(default=None, min_length=2, max_length=50, description=ROLE_NAME_DESCRIPTION)
    description: Optional[str] = Field(default=None, max_length=500, description=ROLE_DESCRIPTION_DESCRIPTION)
    
    @validator('name')
    def validate_name(cls, v):
        """Validar nombre del rol si se proporciona."""
        if v is not None:
            if not v or len(v.strip()) == 0:
                raise ValueError('El nombre del rol no puede estar vacío')
            
            # Convertir a minúsculas y reemplazar espacios con guiones bajos
            name = v.lower().strip().replace(' ', '_')
            
            # Validar que solo contenga letras, números y guiones bajos
            if not name.replace('_', '').isalnum():
                raise ValueError('El nombre del rol solo puede contener letras, números y guiones bajos')
            
            return name
        return v
    
    @validator('description')
    def validate_description(cls, v):
        """Validar descripción del rol si se proporciona."""
        if v is not None and len(v.strip()) == 0:
            return None
        return v.strip() if v else v


# ===== SCHEMAS DE SALIDA (RESPONSE) =====

class RoleResponse(BaseModel):
    """
    Schema para respuesta de rol.
    """
    id: int = Field(description="ID del rol")
    name: str = Field(description=ROLE_NAME_DESCRIPTION)
    description: Optional[str] = Field(default=None, description=ROLE_DESCRIPTION_DESCRIPTION)
    created_at: datetime = Field(description="Fecha de creación")
    user_count: Optional[int] = Field(default=None, description="Número de usuarios con este rol")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RoleCreateResponse(ApiResponse):
    """
    Schema para respuesta de creación de rol exitosa.
    """
    data: RoleResponse = Field(description="Datos del rol creado")


class RoleUpdateResponse(ApiResponse):
    """
    Schema para respuesta de actualización de rol exitosa.
    """
    data: RoleResponse = Field(description="Datos del rol actualizado")


class RoleListApiResponse(ApiResponse):
    """
    Schema para respuesta de lista de roles exitosa.
    """
    data: List[RoleResponse] = Field(description="Lista de roles")
    count: int = Field(description="Número total de roles")


class RoleDetailApiResponse(ApiResponse):
    """
    Schema para respuesta de detalle de rol exitosa.
    """
    data: RoleResponse = Field(description="Datos del rol")


class RoleDeleteResponse(ApiResponse):
    """
    Schema para respuesta de eliminación de rol exitosa.
    """
    data: Optional[dict] = Field(default=None, description="Datos de confirmación de eliminación")


# ===== SCHEMAS DE PERMISOS =====

class PermissionResponse(BaseModel):
    """
    Schema para respuesta de permiso.
    """
    name: str = Field(description="Nombre del permiso")
    description: str = Field(description="Descripción del permiso")
    resource: str = Field(description="Recurso al que aplica el permiso")
    action: str = Field(description="Acción permitida")


class RolePermissionsResponse(BaseModel):
    """
    Schema para respuesta de permisos de rol.
    """
    role: RoleResponse = Field(description="Datos del rol")
    permissions: List[PermissionResponse] = Field(description="Lista de permisos del rol")


class RolePermissionsApiResponse(ApiResponse):
    """
    Schema para respuesta de permisos de rol exitosa.
    """
    data: RolePermissionsResponse = Field(description="Permisos del rol")


# ===== SCHEMAS DE ESTADÍSTICAS =====

class RoleStatsResponse(BaseModel):
    """
    Schema para estadísticas de roles.
    """
    total_roles: int = Field(description="Total de roles")
    roles_with_users: int = Field(description="Roles que tienen usuarios asignados")
    roles_without_users: int = Field(description="Roles sin usuarios asignados")
    most_used_role: Optional[str] = Field(default=None, description="Rol más utilizado")
    least_used_role: Optional[str] = Field(default=None, description="Rol menos utilizado")


class RoleStatsApiResponse(ApiResponse):
    """
    Schema para respuesta de estadísticas de roles exitosa.
    """
    data: RoleStatsResponse = Field(description="Estadísticas de roles")


# ===== SCHEMAS DE ASIGNACIÓN =====

class UserRoleAssignmentRequest(BaseModel):
    """
    Schema para asignación de rol a usuario.
    """
    user_id: int = Field(description="ID del usuario")
    role_id: int = Field(description="ID del rol")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Validar ID del usuario."""
        if v <= 0:
            raise ValueError('El ID del usuario debe ser mayor que 0')
        return v
    
    @validator('role_id')
    def validate_role_id(cls, v):
        """Validar ID del rol."""
        if v <= 0:
            raise ValueError('El ID del rol debe ser mayor que 0')
        return v


class UserRoleAssignmentResponse(ApiResponse):
    """
    Schema para respuesta de asignación de rol exitosa.
    """
    data: dict = Field(description="Datos de confirmación de asignación")


class UserRoleRemovalRequest(BaseModel):
    """
    Schema para remoción de rol de usuario.
    """
    user_id: int = Field(description="ID del usuario")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Validar ID del usuario."""
        if v <= 0:
            raise ValueError('El ID del usuario debe ser mayor que 0')
        return v


class UserRoleRemovalResponse(ApiResponse):
    """
    Schema para respuesta de remoción de rol exitosa.
    """
    data: dict = Field(description="Datos de confirmación de remoción")
