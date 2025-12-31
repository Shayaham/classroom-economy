"""update passkey credential_id to text

Revision ID: $(python3 -c "import uuid; print(uuid.uuid4().hex[:12])")
Revises: ed9de5ef6f79
Create Date: $(date -u +"%Y-%m-%d %H:%M:%S.%6N")

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '$(python3 -c "import uuid; print(uuid.uuid4().hex[:12])")'
down_revision = 'ed9de5ef6f79'
branch_labels = None
depends_on = None


def upgrade():
    # Drop unique constraint and index on admin_credentials.credential_id if they exist
    op.drop_index('ix_admin_credentials_credential_id', table_name='admin_credentials', if_exists=True)
    
    # Drop unique constraint on system_admin_credentials.credential_id if it exists
    op.drop_index('ix_system_admin_credentials_credential_id', table_name='system_admin_credentials', if_exists=True)
    
    # Alter admin_credentials.credential_id: VARCHAR(255) NOT NULL -> TEXT NULL
    with op.batch_alter_table('admin_credentials', schema=None) as batch_op:
        batch_op.alter_column('credential_id',
                              existing_type=sa.String(length=255),
                              type_=sa.Text(),
                              existing_nullable=False,
                              nullable=True)
    
    # Alter system_admin_credentials.credential_id: VARCHAR(255) NOT NULL -> TEXT NULL
    with op.batch_alter_table('system_admin_credentials', schema=None) as batch_op:
        batch_op.alter_column('credential_id',
                              existing_type=sa.String(length=255),
                              type_=sa.Text(),
                              existing_nullable=False,
                              nullable=True)


def downgrade():
    # Revert system_admin_credentials.credential_id: TEXT NULL -> VARCHAR(255) NOT NULL
    with op.batch_alter_table('system_admin_credentials', schema=None) as batch_op:
        batch_op.alter_column('credential_id',
                              existing_type=sa.Text(),
                              type_=sa.String(length=255),
                              existing_nullable=True,
                              nullable=False)
    
    # Revert admin_credentials.credential_id: TEXT NULL -> VARCHAR(255) NOT NULL
    with op.batch_alter_table('admin_credentials', schema=None) as batch_op:
        batch_op.alter_column('credential_id',
                              existing_type=sa.Text(),
                              type_=sa.String(length=255),
                              existing_nullable=True,
                              nullable=False)
    
    # Re-create unique indexes
    op.create_index('ix_admin_credentials_credential_id', 'admin_credentials', ['credential_id'], unique=True)
    op.create_index('ix_system_admin_credentials_credential_id', 'system_admin_credentials', ['credential_id'], unique=True)
