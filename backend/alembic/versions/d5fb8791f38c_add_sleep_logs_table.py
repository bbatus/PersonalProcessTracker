"""add_sleep_logs_table

Revision ID: d5fb8791f38c
Revises: cef467df4b0e
Create Date: 2026-01-11 12:26:29.484084

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5fb8791f38c'
down_revision = 'cef467df4b0e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create sleep_logs table
    op.create_table(
        'sleep_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('sleep_time', sa.Time(), nullable=False),
        sa.Column('wake_time', sa.Time(), nullable=False),
        sa.Column('duration_hours', sa.Float(), nullable=False),
        sa.Column('quality_score', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Create indexes
    op.create_index(op.f('ix_sleep_logs_user_id'), 'sleep_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_sleep_logs_date'), 'sleep_logs', ['date'], unique=False)
    op.create_index('ix_sleep_logs_user_date', 'sleep_logs', ['user_id', 'date'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_sleep_logs_user_date', table_name='sleep_logs')
    op.drop_index(op.f('ix_sleep_logs_date'), table_name='sleep_logs')
    op.drop_index(op.f('ix_sleep_logs_user_id'), table_name='sleep_logs')
    
    # Drop table
    op.drop_table('sleep_logs')
