"""create passkey credential tables v2

Revision ID: ed9de5ef6f79
Revises: 55f079e43ae6
Create Date: 2025-12-31 01:02:21.198065

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ed9de5ef6f79'
down_revision = '55f079e43ae6'
branch_labels = None
depends_on = None


def upgrade():
    # Create admin_credentials table
    op.create_table(
        'admin_credentials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('credential_id', sa.String(length=255), nullable=False),
        sa.Column('authenticator_name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['admin_id'], ['admins.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_credentials_credential_id'), 'admin_credentials', ['credential_id'], unique=True)

    # Create system_admin_credentials table
    op.create_table(
        'system_admin_credentials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('system_admin_id', sa.Integer(), nullable=False),
        sa.Column('credential_id', sa.String(length=255), nullable=False),
        sa.Column('authenticator_name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['system_admin_id'], ['system_admins.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_admin_credentials_credential_id'), 'system_admin_credentials', ['credential_id'], unique=True)


def downgrade():
    # Drop indexes first
    op.drop_index(op.f('ix_system_admin_credentials_credential_id'), table_name='system_admin_credentials')
    op.drop_index(op.f('ix_admin_credentials_credential_id'), table_name='admin_credentials')

    # Drop tables
    op.drop_table('system_admin_credentials')
    op.drop_table('admin_credentials')
