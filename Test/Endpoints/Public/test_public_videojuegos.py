"""
Tests para endpoints públicos de videojuegos.
Verifica que los endpoints GET /videojuegos/* son accesibles sin autenticación.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

from app import app
from src.models import User, Role


class TestPublicVideojuegosEndpoints:
    """Tests para endpoints públicos de videojuegos."""
    
    @pytest.fixture
    def client(self):
        """Cliente de prueba para FastAPI."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_proxy_service(self):
        """Mock del servicio proxy."""
        mock_service = AsyncMock()
        mock_service.get.return_value = {
            "success": True,
            "data": [
                {
                    "id": 1,
                    "titulo": "Test Game",
                    "desarrolladora": "Test Dev",
                    "categoria": "Action",
                    "precio": 29.99
                }
            ],
            "count": 1
        }
        return mock_service
    
    def test_list_videojuegos_public_access(self, client, mock_proxy_service):
        """Verificar que GET /api/videojuegos es accesible sin token."""
        with patch('src.services.get_proxy_service', return_value=mock_proxy_service):
            response = client.get("/api/videojuegos")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "data" in data
    
    def test_get_videojuego_by_id_public_access(self, client, mock_proxy_service):
        """Verificar que GET /api/videojuegos/{id} es accesible sin token."""
        mock_proxy_service.get.return_value = {
            "success": True,
            "data": {
                "id": 1,
                "titulo": "Test Game",
                "desarrolladora": "Test Dev",
                "categoria": "Action",
                "precio": 29.99
            }
        }
        
        with patch('src.services.get_proxy_service', return_value=mock_proxy_service):
            response = client.get("/api/videojuegos/1")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["id"] == 1
    
    def test_get_videojuegos_categorias_public_access(self, client, mock_proxy_service):
        """Verificar que GET /api/videojuegos/categorias/ es accesible sin token."""
        mock_proxy_service.get.return_value = {
            "success": True,
            "data": ["Action", "RPG", "Strategy"],
            "count": 3
        }
        
        with patch('src.services.get_proxy_service', return_value=mock_proxy_service):
            response = client.get("/api/videojuegos/categorias/")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "Action" in data["data"]
    
    def test_get_videojuegos_estadisticas_public_access(self, client, mock_proxy_service):
        """Verificar que GET /api/videojuegos/estadisticas/ es accesible sin token."""
        mock_proxy_service.get.return_value = {
            "success": True,
            "data": {
                "total_videojuegos": 100,
                "categorias": 5,
                "precio_promedio": 25.50
            }
        }
        
        with patch('src.services.get_proxy_service', return_value=mock_proxy_service):
            response = client.get("/api/videojuegos/estadisticas/")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "total_videojuegos" in data["data"]
    
    def test_search_videojuegos_public_access(self, client, mock_proxy_service):
        """Verificar que GET /api/videojuegos/buscar/ es accesible sin token."""
        mock_proxy_service.get.return_value = {
            "success": True,
            "data": [
                {
                    "id": 1,
                    "titulo": "Test Game",
                    "desarrolladora": "Test Dev",
                    "categoria": "Action",
                    "precio": 29.99
                }
            ],
            "count": 1
        }
        
        with patch('src.services.get_proxy_service', return_value=mock_proxy_service):
            response = client.get("/api/videojuegos/buscar/?q=test")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) == 1


class TestProtectedVideojuegosEndpoints:
    """Tests para endpoints protegidos de videojuegos."""
    
    @pytest.fixture
    def client(self):
        """Cliente de prueba para FastAPI."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_proxy_service(self):
        """Mock del servicio proxy."""
        mock_service = AsyncMock()
        mock_service.post.return_value = {
            "success": True,
            "data": {
                "id": 1,
                "titulo": "New Game",
                "desarrolladora": "New Dev",
                "categoria": "Action",
                "precio": 29.99
            }
        }
        return mock_service
    
    def test_create_videojuego_requires_authentication(self, client, mock_proxy_service):
        """Verificar que POST /api/videojuegos requiere autenticación."""
        videojuego_data = {
            "titulo": "New Game",
            "desarrolladora": "New Dev",
            "categoria": "Action",
            "precio": 29.99
        }
        
        with patch('src.services.get_proxy_service', return_value=mock_proxy_service):
            response = client.post("/api/videojuegos", json=videojuego_data)
            
            assert response.status_code == 401  # Unauthorized
    
    def test_update_videojuego_requires_authentication(self, client, mock_proxy_service):
        """Verificar que PUT /api/videojuegos/{id} requiere autenticación."""
        videojuego_data = {
            "titulo": "Updated Game",
            "precio": 39.99
        }
        
        with patch('src.services.get_proxy_service', return_value=mock_proxy_service):
            response = client.put("/api/videojuegos/1", json=videojuego_data)
            
            assert response.status_code == 401  # Unauthorized
    
    def test_delete_videojuego_requires_authentication(self, client, mock_proxy_service):
        """Verificar que DELETE /api/videojuegos/{id} requiere autenticación."""
        with patch('src.services.get_proxy_service', return_value=mock_proxy_service):
            response = client.delete("/api/videojuegos/1")
            
            assert response.status_code == 401  # Unauthorized


class TestRoleBasedAccess:
    """Tests para acceso basado en roles."""
    
    @pytest.fixture
    def client(self):
        """Cliente de prueba para FastAPI."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_proxy_service(self):
        """Mock del servicio proxy."""
        mock_service = AsyncMock()
        mock_service.post.return_value = {
            "success": True,
            "data": {"id": 1, "titulo": "New Game"}
        }
        mock_service.put.return_value = {
            "success": True,
            "data": {"id": 1, "titulo": "Updated Game"}
        }
        mock_service.delete.return_value = {
            "success": True,
            "message": "Videojuego eliminado"
        }
        return mock_service
    
    def create_auth_headers(self, role_name):
        """Crear headers de autenticación para un rol específico."""
        # Mock token con información del rol
        mock_token = f"mock_token_for_{role_name}"
        return {"Authorization": f"Bearer {mock_token}"}
    
    @patch('src.auth.dependencies.get_current_user')
    def test_editor_can_create_videojuego(self, mock_get_current_user, client, mock_proxy_service):
        """Verificar que editor puede crear videojuegos."""
        # Mock user con rol editor
        role = Mock(spec=Role)
        role.name = "editor"
        
        user = Mock(spec=User)
        user.email = "editor@test.com"
        user.role = role
        user.is_active = True
        
        mock_get_current_user.return_value = user
        
        videojuego_data = {
            "titulo": "New Game",
            "desarrolladora": "New Dev",
            "categoria": "Action",
            "precio": 29.99
        }
        
        with patch('src.services.get_proxy_service', return_value=mock_proxy_service):
            response = client.post("/api/videojuegos", json=videojuego_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    @patch('src.auth.dependencies.get_current_user')
    def test_superadmin_can_create_videojuego(self, mock_get_current_user, client, mock_proxy_service):
        """Verificar que superadmin puede crear videojuegos."""
        # Mock user con rol superadmin
        role = Mock(spec=Role)
        role.name = "superadmin"
        
        user = Mock(spec=User)
        user.email = "superadmin@test.com"
        user.role = role
        user.is_active = True
        
        mock_get_current_user.return_value = user
        
        videojuego_data = {
            "titulo": "New Game",
            "desarrolladora": "New Dev",
            "categoria": "Action",
            "precio": 29.99
        }
        
        with patch('src.services.get_proxy_service', return_value=mock_proxy_service):
            response = client.post("/api/videojuegos", json=videojuego_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    @patch('src.auth.dependencies.get_current_user')
    def test_desarrolladora_cannot_create_videojuego(self, mock_get_current_user, client, mock_proxy_service):
        """Verificar que desarrolladora NO puede crear videojuegos."""
        # Mock user con rol desarrolladora
        role = Mock(spec=Role)
        role.name = "desarrolladora"
        
        user = Mock(spec=User)
        user.email = "desarrolladora@test.com"
        user.role = role
        user.is_active = True
        
        mock_get_current_user.return_value = user
        
        videojuego_data = {
            "titulo": "New Game",
            "desarrolladora": "New Dev",
            "categoria": "Action",
            "precio": 29.99
        }
        
        with patch('src.services.get_proxy_service', return_value=mock_proxy_service):
            response = client.post("/api/videojuegos", json=videojuego_data)
            
            assert response.status_code == 403  # Forbidden
    
    @patch('src.auth.dependencies.get_current_user')
    @patch('src.auth.utils.verify_resource_ownership')
    def test_desarrolladora_can_update_own_videojuego(self, mock_verify_ownership, mock_get_current_user, client, mock_proxy_service):
        """Verificar que desarrolladora puede actualizar sus propios videojuegos."""
        # Mock user con rol desarrolladora
        role = Mock(spec=Role)
        role.name = "desarrolladora"
        
        user = Mock(spec=User)
        user.email = "desarrolladora@test.com"
        user.role = role
        user.is_active = True
        
        mock_get_current_user.return_value = user
        mock_verify_ownership.return_value = True  # Es propietario
        
        videojuego_data = {
            "titulo": "Updated Game",
            "precio": 39.99
        }
        
        with patch('src.services.get_proxy_service', return_value=mock_proxy_service):
            response = client.put("/api/videojuegos/1", json=videojuego_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    @patch('src.auth.dependencies.get_current_user')
    @patch('src.auth.utils.verify_resource_ownership')
    def test_desarrolladora_cannot_update_others_videojuego(self, mock_verify_ownership, mock_get_current_user, client, mock_proxy_service):
        """Verificar que desarrolladora NO puede actualizar videojuegos de otros."""
        # Mock user con rol desarrolladora
        role = Mock(spec=Role)
        role.name = "desarrolladora"
        
        user = Mock(spec=User)
        user.email = "desarrolladora@test.com"
        user.role = role
        user.is_active = True
        
        mock_get_current_user.return_value = user
        mock_verify_ownership.return_value = False  # NO es propietario
        
        videojuego_data = {
            "titulo": "Updated Game",
            "precio": 39.99
        }
        
        with patch('src.services.get_proxy_service', return_value=mock_proxy_service):
            response = client.put("/api/videojuegos/1", json=videojuego_data)
            
            assert response.status_code == 403  # Forbidden


class TestPublicEndpointsIntegration:
    """Tests de integración para endpoints públicos."""
    
    @pytest.fixture
    def client(self):
        """Cliente de prueba para FastAPI."""
        return TestClient(app)
    
    def test_public_endpoints_work_without_any_headers(self, client):
        """Verificar que endpoints públicos funcionan sin headers de autenticación."""
        # Mock del proxy service para evitar llamadas reales
        with patch('src.services.get_proxy_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get.return_value = {
                "success": True,
                "data": [],
                "count": 0
            }
            mock_get_service.return_value = mock_service
            
            # Probar varios endpoints públicos
            endpoints = [
                "/api/videojuegos",
                "/api/videojuegos/1",
                "/api/videojuegos/categorias/",
                "/api/videojuegos/estadisticas/",
                "/api/videojuegos/buscar/?q=test"
            ]
            
            for endpoint in endpoints:
                response = client.get(endpoint)
                assert response.status_code == 200, f"Endpoint {endpoint} falló"
                data = response.json()
                assert data["success"] is True, f"Endpoint {endpoint} no retornó success=True"
    
    def test_public_endpoints_ignore_invalid_tokens(self, client):
        """Verificar que endpoints públicos ignoran tokens inválidos."""
        with patch('src.services.get_proxy_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get.return_value = {
                "success": True,
                "data": [],
                "count": 0
            }
            mock_get_service.return_value = mock_service
            
            # Headers con token inválido
            invalid_headers = {
                "Authorization": "Bearer invalid_token"
            }
            
            response = client.get("/api/videojuegos", headers=invalid_headers)
            assert response.status_code == 200  # Debe funcionar igual


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v"])
