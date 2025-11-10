"""
Tests unitarios para el sistema de roles personalizado.
Verifica la creación, asignación y validación de roles.
"""

import pytest
import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

# Agregar el directorio raíz del proyecto al path para importar módulos
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.models import User, Role
from src.config import AsyncSessionLocal
from sqlalchemy import delete
from src.auth.utils import (
    check_user_permissions,
    is_superadmin_user,
    is_editor_user,
    is_desarrolladora_user,
    verify_resource_ownership
)
from src.config.init_roles import init_default_roles


class TestRoleCreation:
    """Tests para la creación de roles por defecto."""
    
    @pytest.mark.asyncio
    async def test_init_default_roles_creates_correct_roles(self):
        """Verificar que se crean los 3 roles correctos."""
        # Inicializar roles (no necesitamos limpiar, init_default_roles no duplica)
        await init_default_roles()
        
        # Verificar que se crearon los roles
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Role))
            roles = result.scalars().all()
            
            assert len(roles) >= 3  # Puede haber más si ya existían
            
            role_names = [role.name for role in roles]
            assert "desarrolladora" in role_names
            assert "editor" in role_names
            assert "superadmin" in role_names
    
    @pytest.mark.asyncio
    async def test_init_default_roles_does_not_duplicate(self):
        """Verificar que no se duplican roles si ya existen."""
        # Asegurar que los roles existen primero
        await init_default_roles()
        
        # Contar roles antes de la segunda llamada
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Role))
            roles_before = result.scalars().all()
            count_before = len(roles_before)
        
        # Inicializar roles nuevamente (no debería crear duplicados)
        await init_default_roles()
        
        # Verificar que el número de roles no cambió
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Role))
            roles_after = result.scalars().all()
            count_after = len(roles_after)
            
            assert count_after == count_before, f"Se crearon roles duplicados: {count_before} -> {count_after}"
            assert count_after >= 3  # Debe haber al menos los 3 roles por defecto
    
    @pytest.mark.asyncio
    async def test_role_descriptions_are_correct(self):
        """Verificar que las descripciones de roles son correctas."""
        await init_default_roles()
        
        async with AsyncSessionLocal() as session:
            # Verificar desarrolladora
            result = await session.execute(
                select(Role).where(Role.name == "desarrolladora")
            )
            desarrolladora = result.scalar_one_or_none()
            assert desarrolladora is not None
            assert "propios videojuegos" in desarrolladora.description
            
            # Verificar editor
            result = await session.execute(
                select(Role).where(Role.name == "editor")
            )
            editor = result.scalar_one_or_none()
            assert editor is not None
            assert "todos los videojuegos" in editor.description
            
            # Verificar superadmin
            result = await session.execute(
                select(Role).where(Role.name == "superadmin")
            )
            superadmin = result.scalar_one_or_none()
            assert superadmin is not None
            assert "acceso completo" in superadmin.description


class TestRolePermissions:
    """Tests para la validación de permisos por rol."""
    
    @pytest.mark.asyncio
    async def test_check_user_permissions_with_valid_roles(self):
        """Verificar permisos con roles válidos."""
        await init_default_roles()
        
        async with AsyncSessionLocal() as session:
            # Crear usuarios de prueba
            desarrolladora_role = await session.execute(
                select(Role).where(Role.name == "desarrolladora")
            )
            desarrolladora_role = desarrolladora_role.scalar_one()
            
            editor_role = await session.execute(
                select(Role).where(Role.name == "editor")
            )
            editor_role = editor_role.scalar_one()
            
            superadmin_role = await session.execute(
                select(Role).where(Role.name == "superadmin")
            )
            superadmin_role = superadmin_role.scalar_one()
            
            # Crear usuarios
            user_desarrolladora = User(
                email="desarrolladora@test.com",
                password_hash="hash",
                role_id=desarrolladora_role.id,
                is_active=True
            )
            
            user_editor = User(
                email="editor@test.com",
                password_hash="hash",
                role_id=editor_role.id,
                is_active=True
            )
            
            user_superadmin = User(
                email="superadmin@test.com",
                password_hash="hash",
                role_id=superadmin_role.id,
                is_active=True
            )
            
            session.add_all([user_desarrolladora, user_editor, user_superadmin])
            await session.commit()
            await session.refresh(user_desarrolladora)
            await session.refresh(user_editor)
            await session.refresh(user_superadmin)
            
            # Verificar permisos
            assert check_user_permissions(user_desarrolladora, "desarrolladora")
            assert check_user_permissions(user_editor, "editor")
            assert check_user_permissions(user_superadmin, "superadmin")
            
            # Verificar que no tienen permisos de otros roles
            assert not check_user_permissions(user_desarrolladora, "editor")
            assert not check_user_permissions(user_desarrolladora, "superadmin")
            assert not check_user_permissions(user_editor, "desarrolladora")
            assert not check_user_permissions(user_editor, "superadmin")
    
    @pytest.mark.asyncio
    async def test_check_user_permissions_with_inactive_user(self):
        """Verificar que usuarios inactivos no tienen permisos."""
        await init_default_roles()
        
        async with AsyncSessionLocal() as session:
            desarrolladora_role = await session.execute(
                select(Role).where(Role.name == "desarrolladora")
            )
            desarrolladora_role = desarrolladora_role.scalar_one()
            
            inactive_user = User(
                email="inactive@test.com",
                password_hash="hash",
                role_id=desarrolladora_role.id,
                is_active=False
            )
            
            session.add(inactive_user)
            await session.commit()
            await session.refresh(inactive_user)
            
            assert not check_user_permissions(inactive_user, "desarrolladora")
    
    @pytest.mark.asyncio
    async def test_check_user_permissions_without_role(self):
        """Verificar que usuarios sin rol no tienen permisos."""
        user_without_role = User(
            email="norole@test.com",
            password_hash="hash",
            role_id=None,
            is_active=True
        )
        
        assert not check_user_permissions(user_without_role, "desarrolladora")


class TestRoleHelperFunctions:
    """Tests para las funciones helper de roles."""
    
    @pytest.mark.asyncio
    async def test_is_superadmin_user(self):
        """Verificar función is_superadmin_user."""
        await init_default_roles()

        async with AsyncSessionLocal() as session:
            superadmin_role = await session.execute(
                select(Role).where(Role.name == "superadmin")
            )
            superadmin_role = superadmin_role.scalar_one()
            
            desarrolladora_role = await session.execute(
                select(Role).where(Role.name == "desarrolladora")
            )
            desarrolladora_role = desarrolladora_role.scalar_one()
            
            superadmin_user = User(
                email="superadmin@test.com",
                password_hash="hash",
                role_id=superadmin_role.id,
                is_active=True
            )
            
            desarrolladora_user = User(
                email="desarrolladora@test.com",
                password_hash="hash",
                role_id=desarrolladora_role.id,
                is_active=True
            )
            
            session.add_all([superadmin_user, desarrolladora_user])
            await session.commit()
            await session.refresh(superadmin_user)
            await session.refresh(desarrolladora_user)
            
            assert is_superadmin_user(superadmin_user)
            assert not is_superadmin_user(desarrolladora_user)
    
    @pytest.mark.asyncio
    async def test_is_editor_user(self):
        """Verificar función is_editor_user."""
        await init_default_roles()

        async with AsyncSessionLocal() as session:
            editor_role = await session.execute(
                select(Role).where(Role.name == "editor")
            )
            editor_role = editor_role.scalar_one()
            
            desarrolladora_role = await session.execute(
                select(Role).where(Role.name == "desarrolladora")
            )
            desarrolladora_role = desarrolladora_role.scalar_one()
            
            editor_user = User(
                email="editor@test.com",
                password_hash="hash",
                role_id=editor_role.id,
                is_active=True
            )
            
            desarrolladora_user = User(
                email="desarrolladora@test.com",
                password_hash="hash",
                role_id=desarrolladora_role.id,
                is_active=True
            )
            
            session.add_all([editor_user, desarrolladora_user])
            await session.commit()
            await session.refresh(editor_user)
            await session.refresh(desarrolladora_user)
            
            assert is_editor_user(editor_user)
            assert not is_editor_user(desarrolladora_user)
    
    @pytest.mark.asyncio
    async def test_is_desarrolladora_user(self):
        """Verificar función is_desarrolladora_user."""
        await init_default_roles()
        
        async with AsyncSessionLocal() as session:
            desarrolladora_role = await session.execute(
                select(Role).where(Role.name == "desarrolladora")
            )
            desarrolladora_role = desarrolladora_role.scalar_one()
            
            editor_role = await session.execute(
                select(Role).where(Role.name == "editor")
            )
            editor_role = editor_role.scalar_one()
            
            desarrolladora_user = User(
                email="desarrolladora@test.com",
                password_hash="hash",
                role_id=desarrolladora_role.id,
                is_active=True
            )
            
            editor_user = User(
                email="editor@test.com",
                password_hash="hash",
                role_id=editor_role.id,
                is_active=True
            )
            
            session.add_all([desarrolladora_user, editor_user])
            await session.commit()
            await session.refresh(desarrolladora_user)
            await session.refresh(editor_user)
            
            assert is_desarrolladora_user(desarrolladora_user)
            assert not is_desarrolladora_user(editor_user)


class TestResourceOwnership:
    """Tests para la validación de propiedad de recursos."""
    
    @pytest.mark.asyncio
    async def test_verify_resource_ownership_without_proxy_service(self):
        """Verificar que sin proxy service se permite acceso (fallback)."""
        await init_default_roles()
        
        async with AsyncSessionLocal() as session:
            desarrolladora_role = await session.execute(
                select(Role).where(Role.name == "desarrolladora")
            )
            desarrolladora_role = desarrolladora_role.scalar_one()
            
            user = User(
                email="owner@test.com",
                password_hash="hash",
                role_id=desarrolladora_role.id,
                is_active=True
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            # Sin proxy service, debe permitir acceso
            result = await verify_resource_ownership(
                resource_type="videojuego",
                resource_id=1,
                user=user,
                proxy_service=None
            )
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_verify_resource_ownership_invalid_resource_type(self):
        """Verificar que tipos de recurso inválidos retornan False."""
        await init_default_roles()
        
        async with AsyncSessionLocal() as session:
            desarrolladora_role = await session.execute(
                select(Role).where(Role.name == "desarrolladora")
            )
            desarrolladora_role = desarrolladora_role.scalar_one()
            
            user = User(
                email="owner@test.com",
                password_hash="hash",
                role_id=desarrolladora_role.id,
                is_active=True
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            # Tipo de recurso inválido
            result = await verify_resource_ownership(
                resource_type="invalid_type",
                resource_id=1,
                user=user,
                proxy_service=None
            )
            
            assert result is False


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v"])
