"""
Middleware de autenticación y autorización.
Implementa middleware para validación automática de tokens y manejo de errores.
"""

import time
from typing import Callable, Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.auth import JWTError, verify_token, extract_token_from_header
from src.schemas import ErrorResponse


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware de autenticación para validar tokens JWT automáticamente.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        protected_paths: Optional[list] = None,
        excluded_paths: Optional[list] = None
    ):
        super().__init__(app)
        self.protected_paths = protected_paths or ["/api/"]
        self.excluded_paths = excluded_paths or ["/auth/", "/docs", "/redoc", "/openapi.json", "/health"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Procesar request y validar autenticación si es necesario.
        
        Args:
            request: Request HTTP
            call_next: Siguiente middleware/handler
            
        Returns:
            Response HTTP
        """
        # Verificar si la ruta requiere autenticación
        if not self._requires_auth(request.url.path):
            return await call_next(request)
        
        # Extraer token del header Authorization
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return self._unauthorized_response("Token de autorización requerido")
        
        token = extract_token_from_header(auth_header)
        if not token:
            return self._unauthorized_response("Formato de token inválido")
        
        # Validar token JWT
        try:
            payload = verify_token(token)
            # Agregar información del usuario al request state
            request.state.user_id = payload.get("sub")
            request.state.user_email = payload.get("email")
            request.state.user_role = payload.get("role")
            request.state.user_is_active = payload.get("is_active")
            
        except JWTError as e:
            return self._unauthorized_response(f"Token inválido: {str(e)}")
        
        # Continuar con el request
        response = await call_next(request)
        return response
    
    def _requires_auth(self, path: str) -> bool:
        """
        Verificar si una ruta requiere autenticación.
        
        Args:
            path: Ruta a verificar
            
        Returns:
            True si requiere autenticación, False en caso contrario
        """
        # Verificar rutas excluidas primero
        for excluded_path in self.excluded_paths:
            if path.startswith(excluded_path):
                return False
        
        # Verificar rutas protegidas
        for protected_path in self.protected_paths:
            if path.startswith(protected_path):
                return True
        
        return False
    
    def _unauthorized_response(self, message: str) -> JSONResponse:
        """
        Crear respuesta de error de autorización.
        
        Args:
            message: Mensaje de error
            
        Returns:
            Respuesta JSON con error de autorización
        """
        error_response = ErrorResponse(
            success=False,
            message=message,
            timestamp=time.time()
        )
        
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response.dict()
        )


class RoleMiddleware(BaseHTTPMiddleware):
    """
    Middleware de autorización basado en roles.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        admin_paths: Optional[list] = None,
        user_paths: Optional[list] = None
    ):
        super().__init__(app)
        self.admin_paths = admin_paths or ["/api/admin/", "/api/users/", "/api/roles/"]
        self.user_paths = user_paths or ["/api/videojuegos/", "/api/desarrolladoras/"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Procesar request y validar autorización por roles.
        
        Args:
            request: Request HTTP
            call_next: Siguiente middleware/handler
            
        Returns:
            Response HTTP
        """
        # Verificar si la ruta requiere autorización por roles
        if not self._requires_role_auth(request.url.path):
            return await call_next(request)
        
        # Obtener información del usuario del request state
        user_role = getattr(request.state, 'user_role', None)
        if not user_role:
            return self._forbidden_response("Información de usuario no disponible")
        
        # Verificar permisos según la ruta
        if self._is_admin_path(request.url.path) and user_role != "admin":
            return self._forbidden_response("Se requieren permisos de administrador")
        
        if self._is_user_path(request.url.path) and user_role not in ["admin", "user"]:
            return self._forbidden_response("Se requieren permisos de usuario")
        
        # Continuar con el request
        response = await call_next(request)
        return response
    
    def _requires_role_auth(self, path: str) -> bool:
        """
        Verificar si una ruta requiere autorización por roles.
        
        Args:
            path: Ruta a verificar
            
        Returns:
            True si requiere autorización por roles, False en caso contrario
        """
        return (self._is_admin_path(path) or 
                self._is_user_path(path))
    
    def _is_admin_path(self, path: str) -> bool:
        """
        Verificar si una ruta es solo para administradores.
        
        Args:
            path: Ruta a verificar
            
        Returns:
            True si es ruta de administrador, False en caso contrario
        """
        return any(path.startswith(admin_path) for admin_path in self.admin_paths)
    
    def _is_user_path(self, path: str) -> bool:
        """
        Verificar si una ruta es para usuarios (admin o user).
        
        Args:
            path: Ruta a verificar
            
        Returns:
            True si es ruta de usuario, False en caso contrario
        """
        return any(path.startswith(user_path) for user_path in self.user_paths)
    
    def _forbidden_response(self, message: str) -> JSONResponse:
        """
        Crear respuesta de error de autorización.
        
        Args:
            message: Mensaje de error
            
        Returns:
            Respuesta JSON con error de autorización
        """
        error_response = ErrorResponse(
            success=False,
            message=message,
            timestamp=time.time()
        )
        
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_response.dict()
        )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware de rate limiting básico.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 100,
        excluded_paths: Optional[list] = None
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.excluded_paths = excluded_paths or ["/health", "/docs", "/redoc"]
        self.requests = {}  # En producción usar Redis o similar
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Procesar request y aplicar rate limiting.
        
        Args:
            request: Request HTTP
            call_next: Siguiente middleware/handler
            
        Returns:
            Response HTTP
        """
        # Verificar si la ruta está excluida del rate limiting
        if self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        # Obtener IP del cliente
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Limpiar requests antiguos
        self._cleanup_old_requests(current_time)
        
        # Verificar rate limit
        if self._is_rate_limited(client_ip, current_time):
            return self._rate_limit_response()
        
        # Registrar request
        self._record_request(client_ip, current_time)
        
        # Continuar con el request
        response = await call_next(request)
        return response
    
    def _is_excluded_path(self, path: str) -> bool:
        """
        Verificar si una ruta está excluida del rate limiting.
        
        Args:
            path: Ruta a verificar
            
        Returns:
            True si está excluida, False en caso contrario
        """
        return any(path.startswith(excluded_path) for excluded_path in self.excluded_paths)
    
    def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """
        Verificar si un cliente está siendo rate limited.
        
        Args:
            client_ip: IP del cliente
            current_time: Tiempo actual
            
        Returns:
            True si está siendo rate limited, False en caso contrario
        """
        if client_ip not in self.requests:
            return False
        
        # Contar requests en el último minuto
        minute_ago = current_time - 60
        recent_requests = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]
        
        return len(recent_requests) >= self.requests_per_minute
    
    def _record_request(self, client_ip: str, current_time: float):
        """
        Registrar un request para rate limiting.
        
        Args:
            client_ip: IP del cliente
            current_time: Tiempo actual
        """
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        self.requests[client_ip].append(current_time)
    
    def _cleanup_old_requests(self, current_time: float):
        """
        Limpiar requests antiguos para ahorrar memoria.
        
        Args:
            current_time: Tiempo actual
        """
        minute_ago = current_time - 60
        
        for client_ip in self.requests.keys():
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if req_time > minute_ago
            ]
            
            # Eliminar clientes sin requests recientes
            if not self.requests[client_ip]:
                del self.requests[client_ip]
    
    def _rate_limit_response(self) -> JSONResponse:
        """
        Crear respuesta de rate limit excedido.
        
        Returns:
            Respuesta JSON con error de rate limit
        """
        error_response = ErrorResponse(
            success=False,
            message="Rate limit excedido. Intenta de nuevo más tarde.",
            timestamp=time.time()
        )
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=error_response.dict()
        )
