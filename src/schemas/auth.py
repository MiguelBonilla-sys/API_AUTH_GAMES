"""
Schemas Pydantic para autenticación.
Define los modelos de entrada y salida para endpoints de autenticación.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from src.schemas.base import ApiResponse, ErrorResponse

# Constantes para strings reutilizados
EMAIL_DESCRIPTION = "Email del usuario"
PASSWORD_DESCRIPTION = "Contraseña del usuario"
ROLE_DESCRIPTION = "Rol del usuario"


# ===== SCHEMAS DE ENTRADA (REQUEST) =====

class LoginRequest(BaseModel):
    """
    Schema para solicitud de login.
    """
    email: EmailStr = Field(description=EMAIL_DESCRIPTION)
    password: str = Field(min_length=1, description=PASSWORD_DESCRIPTION)
    
    @validator('email')
    def validate_email(cls, v):
        """Validar formato de email."""
        if not v or len(v.strip()) == 0:
            raise ValueError('El email no puede estar vacío')
        return v.lower().strip()
    
    @validator('password')
    def validate_password(cls, v):
        """Validar que la contraseña no esté vacía."""
        if not v or len(v.strip()) == 0:
            raise ValueError('La contraseña no puede estar vacía')
        return v


class RegisterRequest(BaseModel):
    """
    Schema para solicitud de registro de usuario.
    """
    email: EmailStr = Field(description=EMAIL_DESCRIPTION)
    password: str = Field(min_length=8, max_length=128, description=PASSWORD_DESCRIPTION)
    confirm_password: str = Field(description="Confirmación de contraseña")
    role: Optional[str] = Field(default="desarrolladora", description=f"{ROLE_DESCRIPTION} (desarrolladora/editor/superadmin)")
    
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
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        """Validar que las contraseñas coincidan."""
        if 'password' in values and v != values['password']:
            raise ValueError('Las contraseñas no coinciden')
        return v
    
    @validator('role')
    def validate_role(cls, v):
        """Validar rol del usuario."""
        if v not in ['desarrolladora', 'editor', 'superadmin']:
            raise ValueError('El rol debe ser "desarrolladora", "editor" o "superadmin"')
        return v


class RefreshTokenRequest(BaseModel):
    """
    Schema para solicitud de renovación de token.
    """
    refresh_token: str = Field(description="Token de renovación")
    
    @validator('refresh_token')
    def validate_refresh_token(cls, v):
        """Validar que el token no esté vacío."""
        if not v or len(v.strip()) == 0:
            raise ValueError('El token de renovación no puede estar vacío')
        return v.strip()


class ChangePasswordRequest(BaseModel):
    """
    Schema para solicitud de cambio de contraseña.
    """
    current_password: str = Field(description="Contraseña actual")
    new_password: str = Field(min_length=8, max_length=128, description="Nueva contraseña")
    confirm_password: str = Field(description="Confirmación de nueva contraseña")
    
    @validator('current_password')
    def validate_current_password(cls, v):
        """Validar contraseña actual."""
        if not v or len(v.strip()) == 0:
            raise ValueError('La contraseña actual no puede estar vacía')
        return v
    
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
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        """Validar que las contraseñas coincidan."""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Las contraseñas no coinciden')
        return v


# ===== SCHEMAS DE SALIDA (RESPONSE) =====

class UserResponse(BaseModel):
    """
    Schema para respuesta de datos de usuario.
    """
    id: int = Field(description="ID del usuario")
    email: str = Field(description=EMAIL_DESCRIPTION)
    role: str = Field(description=ROLE_DESCRIPTION)
    is_active: bool = Field(description="Estado activo del usuario")
    created_at: datetime = Field(description="Fecha de creación")
    updated_at: Optional[datetime] = Field(default=None, description="Fecha de última actualización")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TokenResponse(BaseModel):
    """
    Schema para respuesta de tokens de autenticación.
    """
    access_token: str = Field(description="Token de acceso JWT")
    refresh_token: str = Field(description="Token de renovación")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(description="Tiempo de expiración en segundos")
    user: UserResponse = Field(description="Datos del usuario autenticado")


class LoginResponse(ApiResponse):
    """
    Schema para respuesta de login exitoso.
    """
    data: TokenResponse = Field(description="Datos de autenticación")


class RegisterResponse(ApiResponse):
    """
    Schema para respuesta de registro exitoso.
    """
    data: UserResponse = Field(description="Datos del usuario registrado")


class RefreshResponse(ApiResponse):
    """
    Schema para respuesta de renovación de token exitosa.
    """
    data: TokenResponse = Field(description="Nuevos tokens de autenticación")


class LogoutResponse(ApiResponse):
    """
    Schema para respuesta de logout exitoso.
    """
    data: Optional[dict] = Field(default=None, description="Datos de confirmación de logout")


class ChangePasswordResponse(ApiResponse):
    """
    Schema para respuesta de cambio de contraseña exitoso.
    """
    data: Optional[dict] = Field(default=None, description="Datos de confirmación de cambio")


class UserProfileResponse(ApiResponse):
    """
    Schema para respuesta de perfil de usuario.
    """
    data: UserResponse = Field(description="Datos del perfil de usuario")


# ===== SCHEMAS DE ERROR =====

class AuthErrorResponse(ErrorResponse):
    """
    Schema para respuestas de error de autenticación.
    """
    error_code: Optional[str] = Field(default=None, description="Código de error específico")
    error_type: Optional[str] = Field(default="authentication_error", description="Tipo de error")


class ValidationErrorResponse(ErrorResponse):
    """
    Schema para respuestas de error de validación.
    """
    error_type: str = Field(default="validation_error", description="Tipo de error")
    field_errors: Optional[dict] = Field(default=None, description="Errores por campo")


# ===== SCHEMAS DE UTILIDAD =====

class PasswordStrengthResponse(BaseModel):
    """
    Schema para respuesta de análisis de fortaleza de contraseña.
    """
    strength_score: int = Field(description="Puntuación de fortaleza (0-6)")
    length: int = Field(description="Longitud de la contraseña")
    has_uppercase: bool = Field(description="Contiene mayúsculas")
    has_lowercase: bool = Field(description="Contiene minúsculas")
    has_digits: bool = Field(description="Contiene números")
    has_special: bool = Field(description="Contiene caracteres especiales")
    is_strong: bool = Field(description="Es considerada fuerte")
    suggestions: Optional[list] = Field(default=None, description="Sugerencias de mejora")


class TokenInfoResponse(BaseModel):
    """
    Schema para información de token (debugging).
    """
    user_id: Optional[str] = Field(description="ID del usuario")
    email: Optional[str] = Field(description=EMAIL_DESCRIPTION)
    role: Optional[str] = Field(description=ROLE_DESCRIPTION)
    is_active: Optional[bool] = Field(description="Estado activo")
    token_type: Optional[str] = Field(description="Tipo de token")
    expires_at: Optional[datetime] = Field(description="Fecha de expiración")
    issued_at: Optional[datetime] = Field(description="Fecha de emisión")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
