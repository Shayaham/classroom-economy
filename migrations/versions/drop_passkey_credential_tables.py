"""Drop passkey credential tables

Revision ID: drop_passkey_creds
Revises: z2a3b4c5d6e7
Create Date: 2025-12-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'drop_passkey_creds'
down_revision = 'z2a3b4c5d6e7'
branch_labels = None
depends_on = None


def upgrade():
    # Drop admin_credentials table
    with op.batch_alter_table('admin_credentials', schema=None) as batch_op:
        batch_op.drop_index('ix_admin_credentials_credential_id')

    op.drop_table('admin_credentials')

    # Drop system_admin_credentials table
    with op.batch_alter_table('system_admin_credentials', schema=None) as batch_op:
        batch_op.drop_index('ix_system_admin_credentials_credential_id')

    op.drop_table('system_admin_credentials')


def downgrade():
    # Recreate system_admin_credentials table
    op.create_table('system_admin_credentials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sysadmin_id', sa.Integer(), nullable=False),
        sa.Column('credential_id', sa.LargeBinary(), nullable=False),
        sa.Column('public_key', sa.LargeBinary(), nullable=True),
        sa.Column('sign_count', sa.Integer(), nullable=False),
        sa.Column('transports', sa.String(length=255), nullable=True),
        sa.Column('authenticator_name', sa.String(length=100), nullable=True),
        sa.Column('aaguid', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['sysadmin_id'], ['system_admins.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('system_admin_credentials', schema=None) as batch_op:
        batch_op.create_index('ix_system_admin_credentials_credential_id', ['credential_id'], unique=True)

    # Recreate admin_credentials table
    op.create_table('admin_credentials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('credential_id', sa.LargeBinary(), nullable=False),
        sa.Column('public_key', sa.LargeBinary(), nullable=True),
        sa.Column('sign_count', sa.Integer(), nullable=False),
        sa.Column('transports', sa.String(length=255), nullable=True),
        sa.Column('authenticator_name', sa.String(length=100), nullable=True),
        sa.Column('aaguid', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['admin_id'], ['admins.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('admin_credentials', schema=None) as batch_op:
        batch_op.create_index('ix_admin_credentials_credential_id', ['credential_id'], unique=True)
