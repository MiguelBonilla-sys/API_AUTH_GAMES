"""
Servicio de proxy para reenviar requests a la API Flask existente.
Implementa cliente httpx para forwarding con manejo de errores y formato de respuesta.
"""

import httpx
import json
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from src.config import get_flask_api_url
from src.schemas import ApiResponse, ErrorResponse


class ProxyService:
    """
    Servicio para reenviar requests a la API Flask existente.
    """
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or get_flask_api_url()
        self.timeout = 30.0  # Timeout de 30 segundos
    
    async def forward_request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        user_email: Optional[str] = None
    ) -> JSONResponse:
        """
        Reenviar request a la API Flask existente.
        
        Args:
            method: Método HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint de la API Flask
            headers: Headers HTTP
            params: Parámetros de query
            json_data: Datos JSON para el body
            user_email: Email del usuario autenticado (para logging)
            
        Returns:
            Respuesta JSON de la API Flask
            
        Raises:
            HTTPException: Si hay error en la comunicación
        """
        try:
            # Preparar URL completa
            url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            
            # Preparar headers
            request_headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "API-Auth-Gateway/1.0"
            }
            
            if headers:
                request_headers.update(headers)
            
            # Agregar header de usuario autenticado si está disponible
            if user_email:
                request_headers["X-Authenticated-User"] = user_email
            
            # Realizar request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    headers=request_headers,
                    params=params,
                    json=json_data
                )
                
                # Procesar respuesta
                return self._process_response(response)
                
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Timeout al comunicarse con la API Flask"
            )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No se puede conectar con la API Flask"
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Error de la API Flask: {e.response.text}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno del proxy: {str(e)}"
            )
    
    def _process_response(self, response: httpx.Response) -> JSONResponse:
        """
        Procesar respuesta de la API Flask.
        
        Args:
            response: Respuesta HTTP de httpx
            
        Returns:
            Respuesta JSON procesada
        """
        try:
            # Intentar parsear JSON
            response_data = response.json()
            
            # Verificar si la respuesta tiene el formato esperado
            if isinstance(response_data, dict):
                # Mantener el formato original de la API Flask
                return JSONResponse(
                    status_code=response.status_code,
                    content=response_data
                )
            else:
                # Si no es un dict, envolver en formato estándar
                return JSONResponse(
                    status_code=response.status_code,
                    content={
                        "success": response.status_code < 400,
                        "message": "Respuesta de la API Flask",
                        "data": response_data,
                        "timestamp": None  # La API Flask no incluye timestamp
                    }
                )
                
        except json.JSONDecodeError:
            # Si no es JSON válido, devolver como texto
            return JSONResponse(
                status_code=response.status_code,
                content={
                    "success": response.status_code < 400,
                    "message": "Respuesta de la API Flask",
                    "data": response.text,
                    "timestamp": None
                }
            )
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        user_email: Optional[str] = None
    ) -> JSONResponse:
        """
        Realizar GET request a la API Flask.
        
        Args:
            endpoint: Endpoint de la API Flask
            params: Parámetros de query
            user_email: Email del usuario autenticado
            
        Returns:
            Respuesta JSON
        """
        return await self.forward_request(
            method="GET",
            endpoint=endpoint,
            params=params,
            user_email=user_email
        )
    
    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        user_email: Optional[str] = None
    ) -> JSONResponse:
        """
        Realizar POST request a la API Flask.
        
        Args:
            endpoint: Endpoint de la API Flask
            json_data: Datos JSON para el body
            user_email: Email del usuario autenticado
            
        Returns:
            Respuesta JSON
        """
        return await self.forward_request(
            method="POST",
            endpoint=endpoint,
            json_data=json_data,
            user_email=user_email
        )
    
    async def put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        user_email: Optional[str] = None
    ) -> JSONResponse:
        """
        Realizar PUT request a la API Flask.
        
        Args:
            endpoint: Endpoint de la API Flask
            json_data: Datos JSON para el body
            user_email: Email del usuario autenticado
            
        Returns:
            Respuesta JSON
        """
        return await self.forward_request(
            method="PUT",
            endpoint=endpoint,
            json_data=json_data,
            user_email=user_email
        )
    
    async def delete(
        self,
        endpoint: str,
        user_email: Optional[str] = None
    ) -> JSONResponse:
        """
        Realizar DELETE request a la API Flask.
        
        Args:
            endpoint: Endpoint de la API Flask
            user_email: Email del usuario autenticado
            
        Returns:
            Respuesta JSON
        """
        return await self.forward_request(
            method="DELETE",
            endpoint=endpoint,
            user_email=user_email
        )


# Instancia global del servicio de proxy
proxy_service = ProxyService()


def get_proxy_service() -> ProxyService:
    """
    Obtener instancia del servicio de proxy.
    
    Returns:
        Instancia del ProxyService
    """
    return proxy_service
