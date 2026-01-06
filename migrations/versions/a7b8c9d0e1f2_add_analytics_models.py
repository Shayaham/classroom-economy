"""Add analytics models for system health metrics

Revision ID: a7b8c9d0e1f2
Revises: z2a3b4c5d6e7
Create Date: 2026-01-06 07:30:00.000000

This migration adds three new tables for the analytics feature:

1. analytics_snapshots: Stores precomputed analytics metrics cached by time window
   - System health metrics (participation rate, money velocity, CWI deviation, budget survival)
   - Trend indicators (improving/stable/worsening)
   - All metrics are CWI-relative per analytics spec

2. analytics_events: Tracks significant economy events for chart annotations
   - Rent changes, wage changes, inflation events, holidays
   - Provides context for understanding metric changes

3. analytics_alerts: Visual alerts for anomalies and threshold violations
   - Explains what changed, why it matters, suggests interventions
   - Never shames students or prescribes discipline

All tables properly scoped by join_code for multi-tenancy compliance.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7b8c9d0e1f2'
down_revision = 'z2a3b4c5d6e7'
branch_labels = None
depends_on = None


def upgrade():
    # Create analytics_snapshots table
    op.create_table(
        'analytics_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=False),
        sa.Column('join_code', sa.String(length=20), nullable=False),
        sa.Column('window_type', sa.String(length=20), nullable=False),
        sa.Column('window_start', sa.DateTime(), nullable=False),
        sa.Column('window_end', sa.DateTime(), nullable=False),
        
        # System Health Metrics
        sa.Column('participation_rate', sa.Float(), nullable=True),
        sa.Column('money_velocity', sa.Float(), nullable=True),
        sa.Column('cwi_deviation_within_20pct', sa.Float(), nullable=True),
        sa.Column('budget_survival_pass_rate', sa.Float(), nullable=True),
        
        # CWI Context
        sa.Column('cwi_value', sa.Float(), nullable=False),
        sa.Column('avg_student_balance', sa.Float(), nullable=True),
        
        # Trend Indicators
        sa.Column('balance_trend', sa.String(length=20), nullable=True),
        sa.Column('velocity_trend', sa.String(length=20), nullable=True),
        sa.Column('participation_trend', sa.String(length=20), nullable=True),
        
        # Additional Context
        sa.Column('total_students', sa.Integer(), nullable=False),
        sa.Column('active_students', sa.Integer(), nullable=True),
        sa.Column('total_transactions', sa.Integer(), nullable=True),
        
        # Metadata
        sa.Column('computed_at', sa.DateTime(), nullable=False),
        sa.Column('is_complete', sa.Boolean(), nullable=False, server_default='true'),
        
        sa.ForeignKeyConstraint(['teacher_id'], ['admins.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for analytics_snapshots
    op.create_index('ix_analytics_join_code_window', 'analytics_snapshots', 
                    ['join_code', 'window_type', 'window_start'])
    op.create_index('ix_analytics_teacher_window', 'analytics_snapshots',
                    ['teacher_id', 'window_type', 'window_start'])
    op.create_index('ix_analytics_computed_at', 'analytics_snapshots', ['computed_at'])
    
    # Create analytics_events table
    op.create_table(
        'analytics_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=False),
        sa.Column('join_code', sa.String(length=20), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('event_date', sa.DateTime(), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('old_value', sa.Float(), nullable=True),
        sa.Column('new_value', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by_admin', sa.Boolean(), nullable=False, server_default='true'),
        
        sa.ForeignKeyConstraint(['teacher_id'], ['admins.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for analytics_events
    op.create_index('ix_analytics_events_join_code_date', 'analytics_events',
                    ['join_code', 'event_date'])
    op.create_index('ix_analytics_events_teacher_date', 'analytics_events',
                    ['teacher_id', 'event_date'])
    op.create_index('ix_analytics_events_type', 'analytics_events', ['event_type'])
    
    # Create analytics_alerts table
    op.create_table(
        'analytics_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=False),
        sa.Column('join_code', sa.String(length=20), nullable=False),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('what_changed', sa.String(length=255), nullable=False),
        sa.Column('why_it_matters', sa.Text(), nullable=False),
        sa.Column('suggested_action', sa.Text(), nullable=True),
        sa.Column('metric_name', sa.String(length=100), nullable=True),
        sa.Column('current_value', sa.Float(), nullable=True),
        sa.Column('threshold_value', sa.Float(), nullable=True),
        sa.Column('triggered_at', sa.DateTime(), nullable=False),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        
        sa.ForeignKeyConstraint(['teacher_id'], ['admins.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for analytics_alerts
    op.create_index('ix_analytics_alerts_join_code_active', 'analytics_alerts',
                    ['join_code', 'is_active'])
    op.create_index('ix_analytics_alerts_teacher_active', 'analytics_alerts',
                    ['teacher_id', 'is_active'])
    op.create_index('ix_analytics_alerts_severity', 'analytics_alerts',
                    ['severity', 'is_active'])
    op.create_index('ix_analytics_alerts_triggered', 'analytics_alerts', ['triggered_at'])


def downgrade():
    # Drop analytics_alerts
    op.drop_index('ix_analytics_alerts_triggered', 'analytics_alerts')
    op.drop_index('ix_analytics_alerts_severity', 'analytics_alerts')
    op.drop_index('ix_analytics_alerts_teacher_active', 'analytics_alerts')
    op.drop_index('ix_analytics_alerts_join_code_active', 'analytics_alerts')
    op.drop_table('analytics_alerts')
    
    # Drop analytics_events
    op.drop_index('ix_analytics_events_type', 'analytics_events')
    op.drop_index('ix_analytics_events_teacher_date', 'analytics_events')
    op.drop_index('ix_analytics_events_join_code_date', 'analytics_events')
    op.drop_table('analytics_events')
    
    # Drop analytics_snapshots
    op.drop_index('ix_analytics_computed_at', 'analytics_snapshots')
    op.drop_index('ix_analytics_teacher_window', 'analytics_snapshots')
    op.drop_index('ix_analytics_join_code_window', 'analytics_snapshots')
    op.drop_table('analytics_snapshots')
