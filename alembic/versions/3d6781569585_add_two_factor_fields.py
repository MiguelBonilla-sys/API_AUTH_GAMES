"""add_two_factor_fields

Revision ID: 3d6781569585
Revises: 
Create Date: 2025-11-09 22:43:04.123989

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d6781569585'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Agregar campos de 2FA a la tabla users
    op.add_column('users', sa.Column('two_factor_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('two_factor_method', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('keycloak_user_id', sa.String(36), nullable=True))
    op.add_column('users', sa.Column('two_factor_configured_at', sa.DateTime(timezone=True), nullable=True))
    
    # Crear índice para keycloak_user_id
    op.create_index('ix_users_keycloak_user_id', 'users', ['keycloak_user_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar índice
    op.drop_index('ix_users_keycloak_user_id', table_name='users')
    
    # Eliminar columnas de 2FA
    op.drop_column('users', 'two_factor_configured_at')
    op.drop_column('users', 'keycloak_user_id')
    op.drop_column('users', 'two_factor_method')
    op.drop_column('users', 'two_factor_enabled')
