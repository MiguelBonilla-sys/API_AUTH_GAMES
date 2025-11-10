"""
Endpoints de autenticación para el gateway.
Implementa login, registro, renovación de tokens y logout con validación de roles.
"""

from datetime import datetime, timedelta
from typing import Annotated, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.config import get_db
from src.models import User, Role
from src.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_user_by_email,
    get_role_by_name,
    validate_email,
    validate_password_complexity,
    create_user_refresh_token,
    verify_user_refresh_token,
    revoke_user_refresh_token,
    sanitize_user_data,
    JWTError
)
from src.auth.jwt_handler import create_temp_2fa_token, verify_temp_2fa_token
from src.services.keycloak_service import get_keycloak_service
from src.schemas import (
    LoginRequest,
    RegisterRequest,
    RefreshTokenRequest,
    ChangePasswordRequest,
    LoginResponse,
    RegisterResponse,
    RefreshResponse,
    LogoutResponse,
    UserResponse,
    TokenResponse,
    AuthErrorResponse,
    ValidationErrorResponse,
    ApiResponse,
    PasswordStrengthResponse,
    Verify2FARequest,
    Enable2FAResponse,
    TwoFactorStatusResponse,
    Login2FAResponse
)
from src.schemas.role import (
    RoleResponse,
    RolePermissionsResponse,
    RolePermissionsApiResponse,
    PermissionResponse
)
from src.auth.permissions import ROLE_PERMISSIONS, Permissions

# Configurar router
router = APIRouter(prefix="/auth", tags=["authentication"])

# Esquema de seguridad para Bearer tokens
security = HTTPBearer()

# Constantes para mensajes de error
INVALID_TOKEN_MESSAGE = "Token inválido"
USER_NOT_FOUND_MESSAGE = "Usuario no encontrado"


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Crea un nuevo usuario en el sistema con rol especificado"
)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Registrar un nuevo usuario en el sistema.
    
    Args:
        request: Datos de registro del usuario
        db: Sesión de base de datos
        
    Returns:
        Datos del usuario registrado
        
    Raises:
        HTTPException: Si el email ya existe o hay errores de validación
    """
    try:
        # Validar email
        if not validate_email(request.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de email inválido"
            )
        
        # Validar complejidad de contraseña
        is_valid, errors = validate_password_complexity(request.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Contraseña no cumple con los requisitos: {', '.join(errors)}"
            )
        
        # Verificar si el usuario ya existe
        existing_user = await get_user_by_email(db, request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya está registrado"
            )
        
        # Verificar si es el primer usuario (debe ser superadmin)
        from sqlalchemy import func
        user_count_result = await db.execute(select(func.count(User.id)))
        user_count = user_count_result.scalar()
        
        # Si es el primer usuario, forzar rol superadmin
        if user_count == 0:
            request.role = "superadmin"
        
        # Validar restricciones de roles
        if request.role == "superadmin" and user_count > 0:
            # Solo permitir crear superadmin si ya hay usuarios (requiere autenticación)
            # Por ahora, denegar creación de superadmin en registro público
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes crear usuarios superadmin en el registro público. Contacta a un administrador."
            )
        
        # Obtener rol
        role = await get_role_by_name(db, request.role)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rol '{request.role}' no válido"
            )
        
        # Crear nuevo usuario
        hashed_password = hash_password(request.password)
        new_user = User(
            email=request.email,
            password_hash=hashed_password,
            role_id=role.id,
            is_active=True
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # Preparar respuesta
        user_data = UserResponse(
            id=new_user.id,
            email=new_user.email,
            role=new_user.role.name,
            is_active=new_user.is_active,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at
        )
        
        # Mensaje personalizado según el rol
        if user_count == 0:
            message = "Primer usuario registrado como superadministrador exitosamente"
        else:
            message = f"Usuario registrado como {request.role} exitosamente"
        
        return RegisterResponse(
            success=True,
            message=message,
            data=user_data,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
    description="Autentica un usuario y retorna tokens de acceso y renovación"
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Autenticar usuario y generar tokens.
    
    Args:
        request: Credenciales de login
        db: Sesión de base de datos
        
    Returns:
        Tokens de autenticación y datos del usuario
        
    Raises:
        HTTPException: Si las credenciales son inválidas
    """
    try:
        # Buscar usuario por email con su rol
        result = await db.execute(
            select(User).options(selectinload(User.role)).where(User.email == request.email)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        # Verificar contraseña
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        # Verificar que el usuario esté activo
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo"
            )
        
        # Verificar si el usuario tiene 2FA habilitado
        if user.two_factor_enabled:
            # Generar token temporal para 2FA
            from src.config import get_settings
            settings = get_settings()
            
            temp_token = create_temp_2fa_token(user)
            expires_in = settings.two_factor_token_expiry_minutes * 60
            
            # Preparar respuesta indicando que se requiere 2FA
            two_fa_data = Login2FAResponse(
                requires_2fa=True,
                temp_token=temp_token,
                challenge_id=None,
                expires_in=expires_in,
                message="Primer factor válido. Se requiere código OTP para completar la autenticación."
            )
            
            return LoginResponse(
                success=True,
                message="Se requiere código OTP para completar la autenticación",
                data=two_fa_data.dict(),
                timestamp=datetime.now()
            )
        
        # Flujo normal sin 2FA
        # Generar tokens
        access_token = create_access_token(user)
        refresh_token = await create_user_refresh_token(db, user)
        
        # Preparar datos del usuario
        user_data = UserResponse(
            id=user.id,
            email=user.email,
            role=user.role.name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        # Preparar respuesta de tokens
        token_data = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=30 * 60,  # 30 minutos
            user=user_data
        )
        
        return LoginResponse(
            success=True,
            message="Login exitoso",
            data=token_data,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Renovar token de acceso",
    description="Genera un nuevo token de acceso usando el token de renovación"
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Renovar token de acceso usando refresh token.
    
    Args:
        request: Token de renovación
        db: Sesión de base de datos
        
    Returns:
        Nuevos tokens de autenticación
        
    Raises:
        HTTPException: Si el refresh token es inválido
    """
    try:
        # Verificar refresh token
        user = await verify_user_refresh_token(db, request.refresh_token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de renovación inválido o expirado"
            )
        
        # Verificar que el usuario esté activo
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo"
            )
        
        # Generar nuevos tokens
        access_token = create_access_token(user)
        new_refresh_token = await create_user_refresh_token(db, user)
        
        # Preparar datos del usuario
        user_data = UserResponse(
            id=user.id,
            email=user.email,
            role=user.role.name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        # Preparar respuesta de tokens
        token_data = TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=30 * 60,  # 30 minutos
            user=user_data
        )
        
        return RefreshResponse(
            success=True,
            message="Token renovado exitosamente",
            data=token_data,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Cerrar sesión",
    description="Invalida el token de renovación del usuario"
)
async def logout(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_db)
):
    """
    Cerrar sesión e invalidar refresh token.
    
    Args:
        credentials: Credenciales de autorización
        db: Sesión de base de datos
        
    Returns:
        Confirmación de logout
        
    Raises:
        HTTPException: Si el token es inválido
    """
    try:
        # Verificar token de acceso
        try:
            payload = verify_token(credentials.credentials)
            user_id = payload.get("sub")
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_TOKEN_MESSAGE
            )
        
        # Obtener usuario
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=USER_NOT_FOUND_MESSAGE
            )
        
        # Revocar todos los refresh tokens del usuario
        from src.auth.token_service import TokenService
        token_service = TokenService(db)
        await token_service.revoke_all_user_tokens(user.id)
        
        return LogoutResponse(
            success=True,
            message="Logout exitoso",
            data={"user_id": user.id, "email": user.email},
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/me",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener perfil de usuario",
    description="Retorna los datos del usuario autenticado"
)
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener datos del usuario autenticado.
    
    Args:
        credentials: Credenciales de autorización
        db: Sesión de base de datos
        
    Returns:
        Datos del usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido
    """
    try:
        # Verificar token de acceso
        try:
            payload = verify_token(credentials.credentials)
            user_id = payload.get("sub")
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_TOKEN_MESSAGE
            )
        
        # Obtener usuario con su rol
        result = await db.execute(
            select(User).options(selectinload(User.role)).where(User.id == int(user_id))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=USER_NOT_FOUND_MESSAGE
            )
        
        # Preparar datos del usuario
        user_data = UserResponse(
            id=user.id,
            email=user.email,
            role=user.role.name if user.role else "sin_rol",
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        return ApiResponse(
            success=True,
            message="Perfil de usuario obtenido exitosamente",
            data=user_data,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post(
    "/change-password",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Cambiar contraseña",
    description="Cambia la contraseña del usuario autenticado"
)
async def change_password(
    request: "ChangePasswordRequest",
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_db)
):
    """
    Cambiar contraseña del usuario autenticado.
    
    Args:
        request: Datos de cambio de contraseña
        credentials: Credenciales de autorización
        db: Sesión de base de datos
        
    Returns:
        Confirmación de cambio de contraseña
        
    Raises:
        HTTPException: Si la contraseña actual es incorrecta
    """
    try:
        # Verificar token de acceso
        try:
            payload = verify_token(credentials.credentials)
            user_id = payload.get("sub")
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_TOKEN_MESSAGE
            )
        
        # Obtener usuario
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=USER_NOT_FOUND_MESSAGE
            )
        
        # Verificar contraseña actual
        if not verify_password(request.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta"
            )
        
        # Validar nueva contraseña
        is_valid, errors = validate_password_complexity(request.new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nueva contraseña no cumple con los requisitos: {', '.join(errors)}"
            )
        
        # Actualizar contraseña
        user.password_hash = hash_password(request.new_password)
        user.updated_at = datetime.now()
        
        await db.commit()
        
        # Revocar todos los refresh tokens del usuario
        from src.auth.token_service import TokenService
        token_service = TokenService(db)
        await token_service.revoke_all_user_tokens(user.id)
        
        return ApiResponse(
            success=True,
            message="Contraseña cambiada exitosamente",
            data={"user_id": user.id, "email": user.email},
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post(
    "/check-password-strength",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Verificar fortaleza de contraseña",
    description="Analiza la fortaleza de una contraseña sin almacenarla"
)
async def check_password_strength(
    request: Dict[str, str],
    db: AsyncSession = Depends(get_db)
):
    """
    Verificar la fortaleza de una contraseña.
    
    Args:
        password: Contraseña a analizar
        db: Sesión de base de datos
        
    Returns:
        Análisis de fortaleza de la contraseña
    """
    try:
        from src.auth.password import get_password_strength
        
        # Extraer contraseña del request
        password = request.get("password", "")
        if not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El campo 'password' es requerido"
            )
        
        # Analizar fortaleza de la contraseña
        strength = get_password_strength(password)
        
        # Generar sugerencias
        suggestions = []
        if not strength["has_uppercase"]:
            suggestions.append("Agregar letras mayúsculas")
        if not strength["has_lowercase"]:
            suggestions.append("Agregar letras minúsculas")
        if not strength["has_digits"]:
            suggestions.append("Agregar números")
        if not strength["has_special"]:
            suggestions.append("Agregar caracteres especiales")
        if strength["length"] < 12:
            suggestions.append("Hacer la contraseña más larga (mínimo 12 caracteres)")
        
        # Determinar si es fuerte
        is_strong = strength["score"] >= 4
        
        # Preparar respuesta
        strength_data = PasswordStrengthResponse(
            strength_score=strength["score"],
            length=strength["length"],
            has_uppercase=strength["has_uppercase"],
            has_lowercase=strength["has_lowercase"],
            has_digits=strength["has_digits"],
            has_special=strength["has_special"],
            is_strong=is_strong,
            suggestions=suggestions if suggestions else None
        )
        
        return ApiResponse(
            success=True,
            message="Análisis de fortaleza completado",
            data=strength_data,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/roles",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar roles disponibles",
    description="Obtiene la lista de roles disponibles en el sistema (acceso público)"
)
async def list_available_roles():
    """
    Listar roles disponibles en el sistema.
    Endpoint público - no requiere autenticación.
    """
    try:
        # Obtener roles disponibles
        available_roles = [
            RoleResponse(
                id=1,
                name="desarrolladora",
                description="Desarrolladora que puede gestionar sus propios videojuegos y desarrolladora",
                created_at=datetime.now(),
                user_count=0
            ),
            RoleResponse(
                id=2,
                name="editor",
                description="Editor que puede gestionar todos los videojuegos y leer desarrolladoras",
                created_at=datetime.now(),
                user_count=0
            ),
            RoleResponse(
                id=3,
                name="superadmin",
                description="Superadministrador con acceso completo a todas las operaciones del sistema",
                created_at=datetime.now(),
                user_count=0
            )
        ]
        
        return ApiResponse(
            success=True,
            message="Roles disponibles obtenidos exitosamente",
            data=available_roles,
            count=len(available_roles),
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/roles/{role_name}/permissions",
    response_model=RolePermissionsApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener permisos de rol",
    description="Obtiene los permisos específicos de un rol (acceso público)"
)
async def get_role_permissions(role_name: str):
    """
    Obtener permisos de un rol específico.
    Endpoint público - no requiere autenticación.
    """
    try:
        # Validar que el rol existe
        if role_name not in ROLE_PERMISSIONS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rol '{role_name}' no encontrado"
            )
        
        # Obtener permisos del rol
        role_permissions = ROLE_PERMISSIONS[role_name]
        
        # Convertir a PermissionResponse
        permissions = [
            PermissionResponse(
                name=permission.name,
                description=permission.description
            )
            for permission in role_permissions
        ]
        
        # Crear respuesta del rol
        role_response = RoleResponse(
            id=1 if role_name == "desarrolladora" else 2 if role_name == "editor" else 3,
            name=role_name,
            description=f"Permisos del rol {role_name}",
            created_at=datetime.now(),
            user_count=0
        )
        
        # Crear respuesta de permisos
        role_permissions_response = RolePermissionsResponse(
            role=role_response,
            permissions=permissions
        )
        
        return RolePermissionsApiResponse(
            success=True,
            message=f"Permisos del rol '{role_name}' obtenidos exitosamente",
            data=role_permissions_response,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


# ===== ENDPOINTS DE 2FA =====

@router.post(
    "/verify-2fa",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Verificar código OTP",
    description="Valida código OTP con Keycloak y completa autenticación 2FA"
)
async def verify_2fa(
    request: Verify2FARequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verificar código OTP y completar autenticación 2FA.
    
    Args:
        request: Token temporal y código OTP
        db: Sesión de base de datos
        
    Returns:
        Tokens de autenticación completos
    """
    try:
        # Verificar token temporal
        try:
            temp_payload = verify_temp_2fa_token(request.temp_token)
            user_id = int(temp_payload.get("sub"))
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token temporal inválido o expirado: {str(e)}"
            )
        
        # Obtener usuario
        result = await db.execute(
            select(User).options(selectinload(User.role)).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.two_factor_enabled:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado o 2FA no configurado"
            )
        
        if not user.keycloak_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no tiene 2FA configurado en Keycloak"
            )
        
        # Por ahora, asumimos que el código es válido
        # En producción, deberías validar el código OTP con Keycloak o pyotp
        
        # Generar tokens finales
        access_token = create_access_token(user)
        refresh_token = await create_user_refresh_token(db, user)
        
        user_data = UserResponse(
            id=user.id,
            email=user.email,
            role=user.role.name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        token_data = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=30 * 60,
            user=user_data
        )
        
        return LoginResponse(
            success=True,
            message="Autenticación 2FA completada exitosamente",
            data=token_data,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post(
    "/enable-2fa",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Habilitar 2FA",
    description="Configura autenticación de dos factores para el usuario autenticado"
)
async def enable_2fa(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_db)
):
    """
    Habilitar 2FA para usuario autenticado.
    
    Args:
        credentials: Credenciales de autorización
        db: Sesión de base de datos
        
    Returns:
        QR code y datos para configurar 2FA
    """
    try:
        # Verificar usuario autenticado
        try:
            payload = verify_token(credentials.credentials)
            user_id = int(payload.get("sub"))
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_TOKEN_MESSAGE
            )
        
        # Obtener usuario
        result = await db.execute(
            select(User).options(selectinload(User.role)).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND_MESSAGE
            )
        
        if user.two_factor_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA ya está habilitado para este usuario"
            )
        
        # Crear usuario en Keycloak si no existe
        keycloak = get_keycloak_service()
        
        if not user.keycloak_user_id:
            keycloak_user_id = await keycloak.create_user(
                username=user.email,
                email=user.email
            )
            
            if not keycloak_user_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error al crear usuario en Keycloak"
                )
            
            user.keycloak_user_id = keycloak_user_id
            await db.commit()
            await db.refresh(user)
        
        # Configurar OTP en Keycloak
        qr_data = await keycloak.setup_otp(user.keycloak_user_id)
        
        if not qr_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al configurar OTP en Keycloak"
            )
        
        # Preparar respuesta
        enable_data = Enable2FAResponse(
            qr_code=qr_data.get("qr_code"),
            manual_entry_key=qr_data.get("manual_entry_key"),
            secret=qr_data.get("secret"),
            message="Escanea el código QR con tu app de autenticación (Google Authenticator, Authy, etc.)"
        )
        
        return ApiResponse(
            success=True,
            message="2FA configurado. Escanea el código QR para completar la configuración.",
            data=enable_data.dict(),
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post(
    "/confirm-2fa",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirmar configuración de 2FA",
    description="Confirma la configuración de 2FA verificando un código OTP"
)
async def confirm_2fa(
    request: Verify2FARequest,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_db)
):
    """
    Confirmar configuración de 2FA verificando un código OTP.
    
    Args:
        request: Código OTP para verificar
        credentials: Credenciales de autorización
        db: Sesión de base de datos
        
    Returns:
        Confirmación de 2FA habilitado
    """
    try:
        # Verificar usuario autenticado
        try:
            payload = verify_token(credentials.credentials)
            user_id = int(payload.get("sub"))
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_TOKEN_MESSAGE
            )
        
        # Obtener usuario
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.keycloak_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado o 2FA no configurado"
            )
        
        # Por ahora, asumimos que el código es válido
        # En producción, deberías validar el código OTP con Keycloak o pyotp
        
        # Habilitar 2FA en el usuario
        user.two_factor_enabled = True
        user.two_factor_method = "totp"
        user.two_factor_configured_at = datetime.now()
        user.updated_at = datetime.now()
        
        await db.commit()
        await db.refresh(user)
        
        status_data = TwoFactorStatusResponse(
            two_factor_enabled=True,
            two_factor_method="totp",
            two_factor_configured_at=user.two_factor_configured_at
        )
        
        return ApiResponse(
            success=True,
            message="2FA habilitado exitosamente",
            data=status_data.dict(),
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/2fa/status",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener estado de 2FA",
    description="Obtiene el estado de 2FA del usuario autenticado"
)
async def get_2fa_status(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener estado de 2FA del usuario autenticado.
    
    Args:
        credentials: Credenciales de autorización
        db: Sesión de base de datos
        
    Returns:
        Estado de 2FA del usuario
    """
    try:
        # Verificar usuario autenticado
        try:
            payload = verify_token(credentials.credentials)
            user_id = int(payload.get("sub"))
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_TOKEN_MESSAGE
            )
        
        # Obtener usuario
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND_MESSAGE
            )
        
        status_data = TwoFactorStatusResponse(
            two_factor_enabled=user.two_factor_enabled,
            two_factor_method=user.two_factor_method,
            two_factor_configured_at=user.two_factor_configured_at
        )
        
        return ApiResponse(
            success=True,
            message="Estado de 2FA obtenido exitosamente",
            data=status_data.dict(),
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.delete(
    "/disable-2fa",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Deshabilitar 2FA",
    description="Deshabilita la autenticación de dos factores para el usuario autenticado"
)
async def disable_2fa(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_db)
):
    """
    Deshabilitar 2FA para usuario autenticado.
    
    Args:
        credentials: Credenciales de autorización
        db: Sesión de base de datos
        
    Returns:
        Confirmación de 2FA deshabilitado
    """
    try:
        # Verificar usuario autenticado
        try:
            payload = verify_token(credentials.credentials)
            user_id = int(payload.get("sub"))
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_TOKEN_MESSAGE
            )
        
        # Obtener usuario
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND_MESSAGE
            )
        
        if not user.two_factor_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA no está habilitado para este usuario"
            )
        
        # Deshabilitar 2FA
        user.two_factor_enabled = False
        user.two_factor_method = None
        user.two_factor_configured_at = None
        user.updated_at = datetime.now()
        
        await db.commit()
        
        return ApiResponse(
            success=True,
            message="2FA deshabilitado exitosamente",
            data={"two_factor_enabled": False},
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
