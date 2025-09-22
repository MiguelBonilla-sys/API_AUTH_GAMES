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
    PasswordStrengthResponse
)

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
        
        return RegisterResponse(
            success=True,
            message="Usuario registrado exitosamente",
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
        
        # Obtener usuario
        result = await db.execute(select(User).where(User.id == int(user_id)))
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
            role=user.role.name,
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
