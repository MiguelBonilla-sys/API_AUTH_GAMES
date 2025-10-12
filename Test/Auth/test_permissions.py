"""
Tests unitarios para el sistema de permisos.
Verifica la asignación y validación de permisos por rol.
"""

import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock

# Agregar el directorio raíz del proyecto al path para importar módulos
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.auth.permissions import (
    Permissions,
    ROLE_PERMISSIONS,
    has_permission,
    require_role,
    require_desarrolladora,
    require_editor,
    require_superadmin
)
from src.models import User, Role


class TestPermissions:
    """Tests para la definición de permisos."""
    
    def test_permissions_enum_has_all_required_permissions(self):
        """Verificar que el enum Permissions tiene todos los permisos necesarios."""
        required_permissions = [
            "AUTH_LOGIN", "AUTH_LOGOUT", "AUTH_REFRESH", "AUTH_CHANGE_PASSWORD",
            "USER_READ", "USER_CREATE", "USER_UPDATE", "USER_DELETE",
            "ROLE_READ", "ROLE_CREATE", "ROLE_UPDATE", "ROLE_DELETE",
            "VIDEOJUEGO_READ", "VIDEOJUEGO_CREATE", "VIDEOJUEGO_UPDATE", "VIDEOJUEGO_DELETE",
            "DESARROLLADORA_READ", "DESARROLLADORA_CREATE", "DESARROLLADORA_UPDATE", "DESARROLLADORA_DELETE"
        ]
        
        for permission in required_permissions:
            assert hasattr(Permissions, permission)
    
    def test_role_permissions_mapping_has_all_roles(self):
        """Verificar que ROLE_PERMISSIONS tiene todos los roles."""
        expected_roles = ["desarrolladora", "editor", "superadmin"]
        
        for role in expected_roles:
            assert role in ROLE_PERMISSIONS
    
    def test_desarrolladora_permissions(self):
        """Verificar permisos específicos del rol desarrolladora."""
        desarrolladora_permissions = ROLE_PERMISSIONS["desarrolladora"]
        
        # Debe tener permisos de autenticación
        assert Permissions.AUTH_LOGIN in desarrolladora_permissions
        assert Permissions.AUTH_LOGOUT in desarrolladora_permissions
        assert Permissions.AUTH_REFRESH in desarrolladora_permissions
        assert Permissions.AUTH_CHANGE_PASSWORD in desarrolladora_permissions
        
        # Debe tener permisos de videojuegos
        assert Permissions.VIDEOJUEGO_READ in desarrolladora_permissions
        assert Permissions.VIDEOJUEGO_CREATE in desarrolladora_permissions
        assert Permissions.VIDEOJUEGO_UPDATE in desarrolladora_permissions
        assert Permissions.VIDEOJUEGO_DELETE in desarrolladora_permissions
        
        # Debe tener permisos de desarrolladora
        assert Permissions.DESARROLLADORA_READ in desarrolladora_permissions
        assert Permissions.DESARROLLADORA_CREATE in desarrolladora_permissions
        assert Permissions.DESARROLLADORA_UPDATE in desarrolladora_permissions
        assert Permissions.DESARROLLADORA_DELETE in desarrolladora_permissions
        
        # NO debe tener permisos de admin
        assert Permissions.USER_READ not in desarrolladora_permissions
        assert Permissions.USER_CREATE not in desarrolladora_permissions
        assert Permissions.ROLE_READ not in desarrolladora_permissions
        assert Permissions.ROLE_CREATE not in desarrolladora_permissions
    
    def test_editor_permissions(self):
        """Verificar permisos específicos del rol editor."""
        editor_permissions = ROLE_PERMISSIONS["editor"]
        
        # Debe tener permisos de autenticación
        assert Permissions.AUTH_LOGIN in editor_permissions
        assert Permissions.AUTH_LOGOUT in editor_permissions
        assert Permissions.AUTH_REFRESH in editor_permissions
        assert Permissions.AUTH_CHANGE_PASSWORD in editor_permissions
        
        # Debe tener permisos de videojuegos
        assert Permissions.VIDEOJUEGO_READ in editor_permissions
        assert Permissions.VIDEOJUEGO_CREATE in editor_permissions
        assert Permissions.VIDEOJUEGO_UPDATE in editor_permissions
        assert Permissions.VIDEOJUEGO_DELETE in editor_permissions
        
        # Debe tener solo READ de desarrolladoras
        assert Permissions.DESARROLLADORA_READ in editor_permissions
        assert Permissions.DESARROLLADORA_CREATE not in editor_permissions
        assert Permissions.DESARROLLADORA_UPDATE not in editor_permissions
        assert Permissions.DESARROLLADORA_DELETE not in editor_permissions
        
        # NO debe tener permisos de admin
        assert Permissions.USER_READ not in editor_permissions
        assert Permissions.USER_CREATE not in editor_permissions
        assert Permissions.ROLE_READ not in editor_permissions
        assert Permissions.ROLE_CREATE not in editor_permissions
    
    def test_superadmin_permissions(self):
        """Verificar permisos específicos del rol superadmin."""
        superadmin_permissions = ROLE_PERMISSIONS["superadmin"]
        
        # Debe tener TODOS los permisos
        all_permissions = [
            Permissions.AUTH_LOGIN, Permissions.AUTH_LOGOUT, Permissions.AUTH_REFRESH, Permissions.AUTH_CHANGE_PASSWORD,
            Permissions.USER_READ, Permissions.USER_CREATE, Permissions.USER_UPDATE, Permissions.USER_DELETE,
            Permissions.ROLE_READ, Permissions.ROLE_CREATE, Permissions.ROLE_UPDATE, Permissions.ROLE_DELETE,
            Permissions.VIDEOJUEGO_READ, Permissions.VIDEOJUEGO_CREATE, Permissions.VIDEOJUEGO_UPDATE, Permissions.VIDEOJUEGO_DELETE,
            Permissions.DESARROLLADORA_READ, Permissions.DESARROLLADORA_CREATE, Permissions.DESARROLLADORA_UPDATE, Permissions.DESARROLLADORA_DELETE
        ]
        
        for permission in all_permissions:
            assert permission in superadmin_permissions


class TestPermissionValidation:
    """Tests para la validación de permisos."""
    
    def test_has_permission_with_valid_user_and_permission(self):
        """Verificar que has_permission retorna True para permisos válidos."""
        # Mock user con rol desarrolladora
        role = Mock(spec=Role)
        role.name = "desarrolladora"
        
        user = Mock(spec=User)
        user.role = role
        user.is_active = True
        
        # Verificar permiso que tiene
        assert has_permission(user, Permissions.VIDEOJUEGO_READ)
        assert has_permission(user, Permissions.VIDEOJUEGO_CREATE)
        assert has_permission(user, Permissions.DESARROLLADORA_READ)
    
    def test_has_permission_with_invalid_permission(self):
        """Verificar que has_permission retorna False para permisos inválidos."""
        # Mock user con rol desarrolladora
        role = Mock(spec=Role)
        role.name = "desarrolladora"
        
        user = Mock(spec=User)
        user.role = role
        user.is_active = True
        
        # Verificar permiso que NO tiene
        assert not has_permission(user, Permissions.USER_READ)
        assert not has_permission(user, Permissions.ROLE_CREATE)
    
    def test_has_permission_with_inactive_user(self):
        """Verificar que usuarios inactivos no tienen permisos."""
        role = Mock(spec=Role)
        role.name = "superadmin"
        
        user = Mock(spec=User)
        user.role = role
        user.is_active = False
        
        # Usuario inactivo no debe tener permisos
        assert not has_permission(user, Permissions.VIDEOJUEGO_READ)
    
    def test_has_permission_without_role(self):
        """Verificar que usuarios sin rol no tienen permisos."""
        user = Mock(spec=User)
        user.role = None
        user.is_active = True
        
        # Usuario sin rol no debe tener permisos
        assert not has_permission(user, Permissions.VIDEOJUEGO_READ)
    
    def test_has_permission_with_none_user(self):
        """Verificar que usuario None no tiene permisos."""
        assert not has_permission(None, Permissions.VIDEOJUEGO_READ)


class TestRoleDecorators:
    """Tests para los decoradores de roles."""
    
    def test_require_role_decorator_with_valid_role(self):
        """Verificar que require_role permite acceso con rol válido."""
        # Mock function
        mock_func = Mock(return_value="success")
        
        # Mock user con rol válido
        role = Mock(spec=Role)
        role.name = "desarrolladora"
        
        user = Mock(spec=User)
        user.role = role
        user.is_active = True
        
        # Aplicar decorador
        decorated_func = require_role("desarrolladora")(mock_func)
        
        # Simular llamada
        result = decorated_func(user=user)
        
        # Verificar que se ejecutó la función
        mock_func.assert_called_once_with(user=user)
        assert result == "success"
    
    def test_require_role_decorator_with_invalid_role(self):
        """Verificar que require_role deniega acceso con rol inválido."""
        from fastapi import HTTPException
        
        # Mock function
        mock_func = Mock(return_value="success")
        
        # Mock user con rol inválido
        role = Mock(spec=Role)
        role.name = "desarrolladora"
        
        user = Mock(spec=User)
        user.role = role
        user.is_active = True
        
        # Aplicar decorador
        decorated_func = require_role("editor")(mock_func)
        
        # Simular llamada - debe lanzar excepción
        with pytest.raises(HTTPException) as exc_info:
            decorated_func(user=user)
        
        assert exc_info.value.status_code == 403
        assert "No tienes permisos" in str(exc_info.value.detail)
    
    def test_require_desarrolladora_decorator(self):
        """Verificar decorador require_desarrolladora."""
        # Mock function
        mock_func = Mock(return_value="success")
        
        # Mock user con rol desarrolladora
        role = Mock(spec=Role)
        role.name = "desarrolladora"
        
        user = Mock(spec=User)
        user.role = role
        user.is_active = True
        
        # Aplicar decorador
        decorated_func = require_desarrolladora(mock_func)
        
        # Simular llamada
        result = decorated_func(user=user)
        
        # Verificar que se ejecutó la función
        mock_func.assert_called_once_with(user=user)
        assert result == "success"
    
    def test_require_editor_decorator(self):
        """Verificar decorador require_editor."""
        # Mock function
        mock_func = Mock(return_value="success")
        
        # Mock user con rol editor
        role = Mock(spec=Role)
        role.name = "editor"
        
        user = Mock(spec=User)
        user.role = role
        user.is_active = True
        
        # Aplicar decorador
        decorated_func = require_editor(mock_func)
        
        # Simular llamada
        result = decorated_func(user=user)
        
        # Verificar que se ejecutó la función
        mock_func.assert_called_once_with(user=user)
        assert result == "success"
    
    def test_require_superadmin_decorator(self):
        """Verificar decorador require_superadmin."""
        # Mock function
        mock_func = Mock(return_value="success")
        
        # Mock user con rol superadmin
        role = Mock(spec=Role)
        role.name = "superadmin"
        
        user = Mock(spec=User)
        user.role = role
        user.is_active = True
        
        # Aplicar decorador
        decorated_func = require_superadmin(mock_func)
        
        # Simular llamada
        result = decorated_func(user=user)
        
        # Verificar que se ejecutó la función
        mock_func.assert_called_once_with(user=user)
        assert result == "success"


class TestPermissionEdgeCases:
    """Tests para casos edge de permisos."""
    
    def test_permission_with_unknown_role(self):
        """Verificar comportamiento con rol desconocido."""
        role = Mock(spec=Role)
        role.name = "unknown_role"
        
        user = Mock(spec=User)
        user.role = role
        user.is_active = True
        
        # Rol desconocido no debe tener permisos
        assert not has_permission(user, Permissions.VIDEOJUEGO_READ)
    
    def test_permission_with_empty_role_permissions(self):
        """Verificar comportamiento si un rol no tiene permisos definidos."""
        # Simular rol sin permisos (caso edge)
        original_permissions = ROLE_PERMISSIONS.copy()
        ROLE_PERMISSIONS["test_role"] = []
        
        try:
            role = Mock(spec=Role)
            role.name = "test_role"
            
            user = Mock(spec=User)
            user.role = role
            user.is_active = True
            
            # Rol sin permisos no debe tener ningún permiso
            assert not has_permission(user, Permissions.VIDEOJUEGO_READ)
        finally:
            # Restaurar permisos originales
            ROLE_PERMISSIONS.clear()
            ROLE_PERMISSIONS.update(original_permissions)


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v"])
