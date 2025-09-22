"""
Módulo de autenticación para el gateway de autenticación.
Contiene lógica JWT, manejo de contraseñas y utilidades de seguridad.
"""

from .password import (
    hash_password,
    verify_password,
    get_password_strength,
    validate_password_strength
)

from .jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_token_payload,
    is_token_expired,
    get_user_id_from_token,
    get_user_role_from_token,
    JWTError
)

from .token_service import (
    TokenService,
    create_user_refresh_token,
    verify_user_refresh_token,
    revoke_user_refresh_token
)

from .utils import (
    validate_email,
    validate_password_complexity,
    get_user_by_email,
    get_user_by_id,
    get_role_by_name,
    check_user_permissions,
    is_admin_user,
    is_regular_user,
    extract_token_from_header,
    validate_token_format,
    get_user_info_from_token,
    sanitize_user_data
)

from .dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    get_current_regular_user,
    get_optional_current_user,
    CurrentUser,
    CurrentActiveUser,
    CurrentAdminUser,
    CurrentRegularUser,
    OptionalCurrentUser
)

from .permissions import (
    Permission,
    Permissions,
    has_permission,
    has_any_permission,
    has_all_permissions,
    require_permission,
    require_any_permission,
    require_all_permissions,
    require_role,
    require_admin,
    require_user,
    get_user_permissions,
    get_user_permission_names
)

from .middleware import (
    AuthMiddleware,
    RoleMiddleware,
    RateLimitMiddleware
)

__all__ = [
    # Password utilities
    "hash_password",
    "verify_password", 
    "get_password_strength",
    "validate_password_strength",
    
    # JWT utilities
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "get_token_payload",
    "is_token_expired",
    "get_user_id_from_token",
    "get_user_role_from_token",
    "JWTError",
    
    # Token service
    "TokenService",
    "create_user_refresh_token",
    "verify_user_refresh_token", 
    "revoke_user_refresh_token",
    
    # General utilities
    "validate_email",
    "validate_password_complexity",
    "get_user_by_email",
    "get_user_by_id",
    "get_role_by_name",
    "check_user_permissions",
    "is_admin_user",
    "is_regular_user",
    "extract_token_from_header",
    "validate_token_format",
    "get_user_info_from_token",
    "sanitize_user_data",
    
    # Dependencies
    "get_current_user",
    "get_current_active_user",
    "get_current_admin_user",
    "get_current_regular_user",
    "get_optional_current_user",
    "CurrentUser",
    "CurrentActiveUser",
    "CurrentAdminUser",
    "CurrentRegularUser",
    "OptionalCurrentUser",
    
    # Permissions
    "Permission",
    "Permissions",
    "has_permission",
    "has_any_permission",
    "has_all_permissions",
    "require_permission",
    "require_any_permission",
    "require_all_permissions",
    "require_role",
    "require_admin",
    "require_user",
    "get_user_permissions",
    "get_user_permission_names",
    
    # Middleware
    "AuthMiddleware",
    "RoleMiddleware",
    "RateLimitMiddleware"
]
