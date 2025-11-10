"""
Servicio para interactuar con Keycloak usando OpenID Connect.
Maneja autenticación, creación de usuarios, y configuración de OTP.
"""

import httpx
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from src.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class KeycloakOpenIDConfig:
    """Configuración de OpenID Connect obtenida del documento de descubrimiento"""
    
    def __init__(self, config: Dict[str, Any]):
        self.issuer = config.get("issuer")
        self.token_endpoint = config.get("token_endpoint")
        self.userinfo_endpoint = config.get("userinfo_endpoint")
        self.introspection_endpoint = config.get("introspection_endpoint")
        self.authorization_endpoint = config.get("authorization_endpoint")
        self.end_session_endpoint = config.get("end_session_endpoint")
        self.jwks_uri = config.get("jwks_uri")
        self.grant_types_supported = config.get("grant_types_supported", [])


class KeycloakService:
    """Servicio para interactuar con Keycloak usando OpenID Connect"""
    
    def __init__(self):
        self.base_url = settings.keycloak_server_url
        self.realm = settings.keycloak_realm
        self.client_id = settings.keycloak_client_id
        self.client_secret = settings.keycloak_client_secret
        self._openid_config: Optional[KeycloakOpenIDConfig] = None
        self._service_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._config_fetched_at: Optional[datetime] = None
        self._client = httpx.AsyncClient(timeout=10.0)
    
    async def get_openid_config(self, force_refresh: bool = False) -> KeycloakOpenIDConfig:
        """Obtener configuración OpenID Connect del documento de descubrimiento"""
        if (self._openid_config and not force_refresh and 
            self._config_fetched_at and 
            datetime.utcnow() < self._config_fetched_at + timedelta(hours=1)):
            return self._openid_config
        
        discovery_url = f"{self.base_url}/auth/realms/{self.realm}/.well-known/openid-configuration"
        
        try:
            response = await self._client.get(discovery_url)
            response.raise_for_status()
            config_data = response.json()
            
            self._openid_config = KeycloakOpenIDConfig(config_data)
            self._config_fetched_at = datetime.utcnow()
            
            logger.info(f"Configuración OpenID Connect obtenida")
            return self._openid_config
            
        except Exception as e:
            logger.error(f"Error obteniendo configuración OpenID: {e}")
            raise
    
    async def get_service_token(self) -> str:
        """Obtener token de servicio usando client_credentials grant"""
        if self._service_token and datetime.utcnow() < self._token_expires_at:
            return self._service_token
        
        config = await self.get_openid_config()
        
        if "client_credentials" not in config.grant_types_supported:
            raise ValueError("Keycloak no soporta grant_type 'client_credentials'")
        
        response = await self._client.post(
            config.token_endpoint,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        data = response.json()
        
        self._service_token = data["access_token"]
        expires_in = data.get("expires_in", 3600)
        self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)
        
        return self._service_token
    
    async def create_user(self, username: str, email: str, 
                         first_name: str = "", last_name: str = "") -> Optional[str]:
        """Crear usuario en Keycloak y retornar su ID"""
        token = await self.get_service_token()
        admin_url = f"{self.base_url}/auth/admin/realms/{self.realm}/users"
        
        try:
            response = await self._client.post(
                admin_url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json={
                    "username": username,
                    "email": email,
                    "firstName": first_name,
                    "lastName": last_name,
                    "enabled": True,
                    "emailVerified": False
                }
            )
            
            if response.status_code == 201:
                location = response.headers.get("Location", "")
                user_id = location.split("/")[-1]
                return user_id
            elif response.status_code == 409:
                # Usuario ya existe, buscarlo
                return await self.get_user_id_by_username(username)
            else:
                logger.error(f"Error creando usuario en Keycloak: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Excepción al crear usuario en Keycloak: {e}")
            return None
    
    async def get_user_id_by_username(self, username: str) -> Optional[str]:
        """Obtener ID de usuario por username"""
        try:
            token = await self.get_service_token()
            admin_url = f"{self.base_url}/auth/admin/realms/{self.realm}/users"
            
            response = await self._client.get(
                admin_url,
                headers={"Authorization": f"Bearer {token}"},
                params={"username": username, "exact": "true"}
            )
            response.raise_for_status()
            users = response.json()
            if users:
                return users[0]["id"]
            return None
        except Exception as e:
            logger.error(f"Error obteniendo usuario de Keycloak: {e}")
            return None
    
    async def setup_otp(self, keycloak_user_id: str) -> Dict[str, Any]:
        """Configurar OTP para un usuario y retornar QR code"""
        try:
            token = await self.get_service_token()
            admin_url = f"{self.base_url}/auth/admin/realms/{self.realm}/users/{keycloak_user_id}/otp/generate"
            
            response = await self._client.post(
                admin_url,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "qr_code": data.get("qrCode"),
                    "secret": data.get("secret"),
                    "manual_entry_key": data.get("key")
                }
            
            logger.error(f"Error configurando OTP: {response.status_code} - {response.text}")
            return {}
        except Exception as e:
            logger.error(f"Excepción al configurar OTP: {e}")
            return {}
    
    async def delete_user(self, keycloak_user_id: str) -> bool:
        """Eliminar usuario de Keycloak"""
        try:
            token = await self.get_service_token()
            admin_url = f"{self.base_url}/auth/admin/realms/{self.realm}/users/{keycloak_user_id}"
            
            response = await self._client.delete(
                admin_url,
                headers={"Authorization": f"Bearer {token}"}
            )
            return response.status_code in [204, 200]
        except Exception as e:
            logger.error(f"Error eliminando usuario de Keycloak: {e}")
            return False
    
    async def close(self):
        """Cerrar cliente HTTP"""
        await self._client.aclose()


# Instancia global
_keycloak_service: Optional[KeycloakService] = None


def get_keycloak_service() -> KeycloakService:
    """Obtener instancia del servicio Keycloak"""
    global _keycloak_service
    if _keycloak_service is None:
        _keycloak_service = KeycloakService()
    return _keycloak_service

