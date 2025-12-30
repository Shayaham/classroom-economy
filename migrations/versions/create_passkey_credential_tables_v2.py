"""Create passkey credential tables (v2 - simplified schema)

Revision ID: create_passkey_v2
Revises: z2a3b4c5d6e7
Create Date: 2025-12-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_passkey_v2'
down_revision = 'z2a3b4c5d6e7'
branch_labels = None
depends_on = None


def upgrade():
    # Create system_admin_credentials table
    op.create_table('system_admin_credentials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sysadmin_id', sa.Integer(), nullable=False),
        sa.Column('credential_id', sa.String(length=255), nullable=False),
        sa.Column('authenticator_name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['sysadmin_id'], ['system_admins.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('system_admin_credentials', schema=None) as batch_op:
        batch_op.create_index('ix_system_admin_credentials_credential_id', ['credential_id'], unique=True)

    # Create admin_credentials table
    op.create_table('admin_credentials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('credential_id', sa.String(length=255), nullable=False),
        sa.Column('authenticator_name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['admin_id'], ['admins.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('admin_credentials', schema=None) as batch_op:
        batch_op.create_index('ix_admin_credentials_credential_id', ['credential_id'], unique=True)


def downgrade():
    # Drop admin_credentials table
    with op.batch_alter_table('admin_credentials', schema=None) as batch_op:
        batch_op.drop_index('ix_admin_credentials_credential_id')
    op.drop_table('admin_credentials')

    # Drop system_admin_credentials table
    with op.batch_alter_table('system_admin_credentials', schema=None) as batch_op:
        batch_op.drop_index('ix_system_admin_credentials_credential_id')
    op.drop_table('system_admin_credentials')
