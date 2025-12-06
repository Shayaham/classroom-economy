"""Add join_code to related tables for complete period-level isolation

Revision ID: b1c2d3e4f5g6
Revises: a1b2c3d4e5f7
Create Date: 2025-12-06

CRITICAL: This migration completes the P0 fix for multi-period isolation by adding
join_code to all remaining tables that need it. This ensures students enrolled in
multiple periods with the same teacher see properly isolated data.

Note: The transaction table already has join_code (added in migration 00212c18b0ac).

Tables updated:
- student_items: Store purchases scoped by class period
- student_insurance: Insurance enrollments scoped by class period
- hall_pass_logs: Hall pass requests scoped by class period
- rent_payments: Rent payments scoped by class period

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1c2d3e4f5g6'
down_revision = 'a1b2c3d4e5f7'
branch_labels = None
depends_on = None


def column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def index_exists(table_name, index_name):
    """Check if an index exists on a table."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    indexes = [idx['name'] for idx in inspector.get_indexes(table_name)]
    return index_name in indexes


def upgrade():
    """Add join_code columns to related tables."""

    # 1. Add join_code to student_items table
    if not column_exists('student_items', 'join_code'):
        op.add_column('student_items',
            sa.Column('join_code', sa.String(20), nullable=True)
        )
        print("✅ Added join_code column to student_items table")
    else:
        print("⚠️  Column 'join_code' already exists on 'student_items', skipping...")

    if not index_exists('student_items', 'ix_student_items_join_code'):
        op.create_index(
            'ix_student_items_join_code',
            'student_items',
            ['join_code']
        )
        print("✅ Added index ix_student_items_join_code")
    else:
        print("⚠️  Index 'ix_student_items_join_code' already exists, skipping...")

    # 2. Add join_code to student_insurance table
    if not column_exists('student_insurance', 'join_code'):
        op.add_column('student_insurance',
            sa.Column('join_code', sa.String(20), nullable=True)
        )
        print("✅ Added join_code column to student_insurance table")
    else:
        print("⚠️  Column 'join_code' already exists on 'student_insurance', skipping...")

    if not index_exists('student_insurance', 'ix_student_insurance_join_code'):
        op.create_index(
            'ix_student_insurance_join_code',
            'student_insurance',
            ['join_code']
        )
        print("✅ Added index ix_student_insurance_join_code")
    else:
        print("⚠️  Index 'ix_student_insurance_join_code' already exists, skipping...")

    # 3. Add join_code to hall_pass_logs table
    if not column_exists('hall_pass_logs', 'join_code'):
        op.add_column('hall_pass_logs',
            sa.Column('join_code', sa.String(20), nullable=True)
        )
        print("✅ Added join_code column to hall_pass_logs table")
    else:
        print("⚠️  Column 'join_code' already exists on 'hall_pass_logs', skipping...")

    if not index_exists('hall_pass_logs', 'ix_hall_pass_logs_join_code'):
        op.create_index(
            'ix_hall_pass_logs_join_code',
            'hall_pass_logs',
            ['join_code']
        )
        print("✅ Added index ix_hall_pass_logs_join_code")
    else:
        print("⚠️  Index 'ix_hall_pass_logs_join_code' already exists, skipping...")

    # 4. Add join_code to rent_payments table
    if not column_exists('rent_payments', 'join_code'):
        op.add_column('rent_payments',
            sa.Column('join_code', sa.String(20), nullable=True)
        )
        print("✅ Added join_code column to rent_payments table")
    else:
        print("⚠️  Column 'join_code' already exists on 'rent_payments', skipping...")

    if not index_exists('rent_payments', 'ix_rent_payments_join_code'):
        op.create_index(
            'ix_rent_payments_join_code',
            'rent_payments',
            ['join_code']
        )
        print("✅ Added index ix_rent_payments_join_code")
    else:
        print("⚠️  Index 'ix_rent_payments_join_code' already exists, skipping...")

    print("")
    print("⚠️  WARNING: Existing records will have NULL join_code")
    print("⚠️  Action required: Backfill join_code for historical data")
    print("⚠️  See docs/security/CRITICAL_SAME_TEACHER_LEAK.md for backfill strategy")
    print("")
    print("✅ Migration complete - P0 multi-period isolation schema ready")


def downgrade():
    """Remove join_code columns from related tables."""

    # Drop indexes and columns in reverse order

    # 4. rent_payments
    if index_exists('rent_payments', 'ix_rent_payments_join_code'):
        op.drop_index('ix_rent_payments_join_code', table_name='rent_payments')
        print("❌ Dropped index ix_rent_payments_join_code")

    if column_exists('rent_payments', 'join_code'):
        op.drop_column('rent_payments', 'join_code')
        print("❌ Removed join_code column from rent_payments table")

    # 3. hall_pass_logs
    if index_exists('hall_pass_logs', 'ix_hall_pass_logs_join_code'):
        op.drop_index('ix_hall_pass_logs_join_code', table_name='hall_pass_logs')
        print("❌ Dropped index ix_hall_pass_logs_join_code")

    if column_exists('hall_pass_logs', 'join_code'):
        op.drop_column('hall_pass_logs', 'join_code')
        print("❌ Removed join_code column from hall_pass_logs table")

    # 2. student_insurance
    if index_exists('student_insurance', 'ix_student_insurance_join_code'):
        op.drop_index('ix_student_insurance_join_code', table_name='student_insurance')
        print("❌ Dropped index ix_student_insurance_join_code")

    if column_exists('student_insurance', 'join_code'):
        op.drop_column('student_insurance', 'join_code')
        print("❌ Removed join_code column from student_insurance table")

    # 1. student_items
    if index_exists('student_items', 'ix_student_items_join_code'):
        op.drop_index('ix_student_items_join_code', table_name='student_items')
        print("❌ Dropped index ix_student_items_join_code")

    if column_exists('student_items', 'join_code'):
        op.drop_column('student_items', 'join_code')
        print("❌ Removed join_code column from student_items table")
