"""
Schemas Pydantic para gestión de usuarios.
Define modelos para operaciones CRUD de usuarios (solo para administradores).
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from src.schemas.base import ApiResponse, ErrorResponse

# Constantes para strings reutilizados
EMAIL_DESCRIPTION = "Email del usuario"
PASSWORD_DESCRIPTION = "Contraseña del usuario"
ROLE_DESCRIPTION = "Rol del usuario"
IS_ACTIVE_DESCRIPTION = "Estado activo del usuario"
ROLE_VALIDATION_MESSAGE = 'El rol debe ser "admin" o "user"'


# ===== SCHEMAS DE ENTRADA (REQUEST) =====

class UserCreateRequest(BaseModel):
    """
    Schema para creación de usuario (solo administradores).
    """
    email: EmailStr = Field(description=EMAIL_DESCRIPTION)
    password: str = Field(min_length=8, max_length=128, description="Contraseña del usuario")
    role: str = Field(description=ROLE_DESCRIPTION)
    is_active: bool = Field(default=True, description=IS_ACTIVE_DESCRIPTION)
    
    @validator('email')
    def validate_email(cls, v):
        """Validar formato de email."""
        if not v or len(v.strip()) == 0:
            raise ValueError('El email no puede estar vacío')
        return v.lower().strip()
    
    @validator('password')
    def validate_password(cls, v):
        """Validar complejidad de contraseña."""
        if not v or len(v.strip()) == 0:
            raise ValueError('La contraseña no puede estar vacía')
        
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        
        if len(v) > 128:
            raise ValueError('La contraseña no puede tener más de 128 caracteres')
        
        # Verificar complejidad básica
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('La contraseña debe contener al menos una mayúscula, una minúscula y un número')
        
        return v
    
    @validator('role')
    def validate_role(cls, v):
        """Validar rol del usuario."""
        if v not in ['admin', 'user']:
            raise ValueError(ROLE_VALIDATION_MESSAGE)
        return v


class UserUpdateRequest(BaseModel):
    """
    Schema para actualización de usuario (solo administradores).
    """
    email: Optional[EmailStr] = Field(default=None, description=EMAIL_DESCRIPTION)
    role: Optional[str] = Field(default=None, description=ROLE_DESCRIPTION)
    is_active: Optional[bool] = Field(default=None, description=IS_ACTIVE_DESCRIPTION)
    
    @validator('email')
    def validate_email(cls, v):
        """Validar formato de email si se proporciona."""
        if v is not None:
            if not v or len(v.strip()) == 0:
                raise ValueError('El email no puede estar vacío')
            return v.lower().strip()
        return v
    
    @validator('role')
    def validate_role(cls, v):
        """Validar rol del usuario si se proporciona."""
        if v is not None and v not in ['admin', 'user']:
            raise ValueError(ROLE_VALIDATION_MESSAGE)
        return v


class UserPasswordUpdateRequest(BaseModel):
    """
    Schema para actualización de contraseña de usuario (solo administradores).
    """
    new_password: str = Field(min_length=8, max_length=128, description="Nueva contraseña")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validar nueva contraseña."""
        if not v or len(v.strip()) == 0:
            raise ValueError('La nueva contraseña no puede estar vacía')
        
        if len(v) < 8:
            raise ValueError('La nueva contraseña debe tener al menos 8 caracteres')
        
        if len(v) > 128:
            raise ValueError('La nueva contraseña no puede tener más de 128 caracteres')
        
        # Verificar complejidad básica
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('La nueva contraseña debe contener al menos una mayúscula, una minúscula y un número')
        
        return v


# ===== SCHEMAS DE SALIDA (RESPONSE) =====

class UserDetailResponse(BaseModel):
    """
    Schema para respuesta detallada de usuario.
    """
    id: int = Field(description="ID del usuario")
    email: str = Field(description=EMAIL_DESCRIPTION)
    role: str = Field(description=ROLE_DESCRIPTION)
    is_active: bool = Field(description=IS_ACTIVE_DESCRIPTION)
    created_at: datetime = Field(description="Fecha de creación")
    updated_at: Optional[datetime] = Field(default=None, description="Fecha de última actualización")
    last_login: Optional[datetime] = Field(default=None, description="Último login")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserListResponse(BaseModel):
    """
    Schema para respuesta de lista de usuarios.
    """
    id: int = Field(description="ID del usuario")
    email: str = Field(description=EMAIL_DESCRIPTION)
    role: str = Field(description=ROLE_DESCRIPTION)
    is_active: bool = Field(description=IS_ACTIVE_DESCRIPTION)
    created_at: datetime = Field(description="Fecha de creación")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserCreateResponse(ApiResponse):
    """
    Schema para respuesta de creación de usuario exitosa.
    """
    data: UserDetailResponse = Field(description="Datos del usuario creado")


class UserUpdateResponse(ApiResponse):
    """
    Schema para respuesta de actualización de usuario exitosa.
    """
    data: UserDetailResponse = Field(description="Datos del usuario actualizado")


class UserListApiResponse(ApiResponse):
    """
    Schema para respuesta de lista de usuarios exitosa.
    """
    data: List[UserListResponse] = Field(description="Lista de usuarios")
    count: int = Field(description="Número total de usuarios")


class UserDetailApiResponse(ApiResponse):
    """
    Schema para respuesta de detalle de usuario exitosa.
    """
    data: UserDetailResponse = Field(description="Datos del usuario")


class UserDeleteResponse(ApiResponse):
    """
    Schema para respuesta de eliminación de usuario exitosa.
    """
    data: Optional[dict] = Field(default=None, description="Datos de confirmación de eliminación")


# ===== SCHEMAS DE FILTROS Y BÚSQUEDA =====

class UserFilterRequest(BaseModel):
    """
    Schema para filtros de búsqueda de usuarios.
    """
    role: Optional[str] = Field(default=None, description="Filtrar por rol")
    is_active: Optional[bool] = Field(default=None, description="Filtrar por estado activo")
    email_contains: Optional[str] = Field(default=None, description="Buscar por email que contenga")
    created_after: Optional[datetime] = Field(default=None, description="Usuarios creados después de")
    created_before: Optional[datetime] = Field(default=None, description="Usuarios creados antes de")
    
    @validator('role')
    def validate_role(cls, v):
        """Validar rol si se proporciona."""
        if v is not None and v not in ['admin', 'user']:
            raise ValueError(ROLE_VALIDATION_MESSAGE)
        return v
    
    @validator('email_contains')
    def validate_email_contains(cls, v):
        """Validar búsqueda de email."""
        if v is not None and len(v.strip()) < 2:
            raise ValueError('La búsqueda de email debe tener al menos 2 caracteres')
        return v.strip() if v else v


class UserStatsResponse(BaseModel):
    """
    Schema para estadísticas de usuarios.
    """
    total_users: int = Field(description="Total de usuarios")
    active_users: int = Field(description="Usuarios activos")
    inactive_users: int = Field(description="Usuarios inactivos")
    admin_users: int = Field(description="Usuarios administradores")
    regular_users: int = Field(description="Usuarios regulares")
    users_created_today: int = Field(description="Usuarios creados hoy")
    users_created_this_month: int = Field(description="Usuarios creados este mes")


class UserStatsApiResponse(ApiResponse):
    """
    Schema para respuesta de estadísticas de usuarios exitosa.
    """
    data: UserStatsResponse = Field(description="Estadísticas de usuarios")
