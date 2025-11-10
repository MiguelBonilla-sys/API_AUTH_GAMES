"""
Módulo de schemas Pydantic para el gateway de autenticación.
Contiene todos los modelos de validación de entrada y salida.
"""

# Schemas base
from .base import (
    BaseResponse,
    ApiResponse,
    ErrorResponse,
    ValidationError,
    PaginationResponse,
    HealthCheckResponse
)

# Schemas de autenticación
from .auth import (
    # Request schemas
    LoginRequest,
    RegisterRequest,
    RefreshTokenRequest,
    ChangePasswordRequest,
    
    # Response schemas
    UserResponse,
    TokenResponse,
    LoginResponse,
    RegisterResponse,
    RefreshResponse,
    LogoutResponse,
    ChangePasswordResponse,
    UserProfileResponse,
    
    # Error schemas
    AuthErrorResponse,
    ValidationErrorResponse,
    
    # Utility schemas
    PasswordStrengthResponse,
    TokenInfoResponse,
    
    # 2FA schemas
    Verify2FARequest,
    Enable2FAResponse,
    TwoFactorStatusResponse,
    Login2FAResponse
)

# Schemas de usuarios
from .user import (
    # Request schemas
    UserCreateRequest,
    UserUpdateRequest,
    UserPasswordUpdateRequest,
    UserFilterRequest,
    
    # Response schemas
    UserDetailResponse,
    UserListResponse,
    UserCreateResponse,
    UserUpdateResponse,
    UserListApiResponse,
    UserDetailApiResponse,
    UserDeleteResponse,
    UserStatsResponse,
    UserStatsApiResponse
)

# Schemas de roles
from .role import (
    # Request schemas
    RoleCreateRequest,
    RoleUpdateRequest,
    UserRoleAssignmentRequest,
    UserRoleRemovalRequest,
    
    # Response schemas
    RoleResponse,
    RoleCreateResponse,
    RoleUpdateResponse,
    RoleListApiResponse,
    RoleDetailApiResponse,
    RoleDeleteResponse,
    RolePermissionsResponse,
    RolePermissionsApiResponse,
    RoleStatsResponse,
    RoleStatsApiResponse,
    UserRoleAssignmentResponse,
    UserRoleRemovalResponse,
    
    # Permission schemas
    PermissionResponse
)

# Schemas de videojuegos
from .videojuegos import (
    # Request schemas
    VideojuegoCreateRequest,
    VideojuegoUpdateRequest,
    VideojuegoFilterRequest,
    
    # Response schemas
    DesarrolladoraResponse,
    VideojuegoResponse,
    VideojuegoListResponse,
    VideojuegoDetailResponse,
    VideojuegoCreateResponse,
    VideojuegoUpdateResponse,
    VideojuegoDeleteResponse,
    CategoriasResponse,
    EstadisticasResponse,
    
    # Error schemas
    VideojuegoErrorResponse,
    VideojuegoNotFoundResponse
)

__all__ = [
    # Base schemas
    "BaseResponse",
    "ApiResponse", 
    "ErrorResponse",
    "ValidationError",
    "PaginationResponse",
    "HealthCheckResponse",
    
    # Auth request schemas
    "LoginRequest",
    "RegisterRequest", 
    "RefreshTokenRequest",
    "ChangePasswordRequest",
    
    # Auth response schemas
    "UserResponse",
    "TokenResponse",
    "LoginResponse",
    "RegisterResponse",
    "RefreshResponse", 
    "LogoutResponse",
    "ChangePasswordResponse",
    "UserProfileResponse",
    
    # Auth error schemas
    "AuthErrorResponse",
    "ValidationErrorResponse",
    
    # Auth utility schemas
    "PasswordStrengthResponse",
    "TokenInfoResponse",
    
    # 2FA schemas
    "Verify2FARequest",
    "Enable2FAResponse",
    "TwoFactorStatusResponse",
    "Login2FAResponse",
    
    # User request schemas
    "UserCreateRequest",
    "UserUpdateRequest",
    "UserPasswordUpdateRequest", 
    "UserFilterRequest",
    
    # User response schemas
    "UserDetailResponse",
    "UserListResponse",
    "UserCreateResponse",
    "UserUpdateResponse",
    "UserListApiResponse",
    "UserDetailApiResponse",
    "UserDeleteResponse",
    "UserStatsResponse",
    "UserStatsApiResponse",
    
    # Role request schemas
    "RoleCreateRequest",
    "RoleUpdateRequest",
    "UserRoleAssignmentRequest",
    "UserRoleRemovalRequest",
    
    # Role response schemas
    "RoleResponse",
    "RoleCreateResponse",
    "RoleUpdateResponse",
    "RoleListApiResponse",
    "RoleDetailApiResponse",
    "RoleDeleteResponse",
    "RolePermissionsResponse",
    "RolePermissionsApiResponse",
    "RoleStatsResponse",
    "RoleStatsApiResponse",
    "UserRoleAssignmentResponse",
    "UserRoleRemovalResponse",
    
    # Permission schemas
    "PermissionResponse",
    
    # Videojuego request schemas
    "VideojuegoCreateRequest",
    "VideojuegoUpdateRequest",
    "VideojuegoFilterRequest",
    
    # Videojuego response schemas
    "DesarrolladoraResponse",
    "VideojuegoResponse",
    "VideojuegoListResponse",
    "VideojuegoDetailResponse",
    "VideojuegoCreateResponse",
    "VideojuegoUpdateResponse",
    "VideojuegoDeleteResponse",
    "CategoriasResponse",
    "EstadisticasResponse",
    
    # Videojuego error schemas
    "VideojuegoErrorResponse",
    "VideojuegoNotFoundResponse"
]
