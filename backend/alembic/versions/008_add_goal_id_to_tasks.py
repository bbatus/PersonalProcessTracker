"""Add goal_id to tasks

Revision ID: 008
Revises: d5fb8791f38c
Create Date: 2026-01-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007_add_task_notes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add goal_id column to tasks table
    op.add_column('tasks',
        sa.Column('goal_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    
    # Add foreign key constraint with ON DELETE SET NULL
    # When a goal is deleted, task.goal_id will be set to NULL
    op.create_foreign_key(
        'fk_tasks_goal_id',
        'tasks', 'goals',
        ['goal_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Add index for performance on goal_id lookups
    op.create_index(
        'ix_tasks_goal_id',
        'tasks',
        ['goal_id']
    )
    
    # Add composite index for user + goal queries
    # This optimizes queries like "get all tasks for user X and goal Y"
    op.create_index(
        'ix_tasks_user_goal',
        'tasks',
        ['user_id', 'goal_id']
    )


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('ix_tasks_user_goal', 'tasks')
    op.drop_index('ix_tasks_goal_id', 'tasks')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_tasks_goal_id', 'tasks', type_='foreignkey')
    
    # Drop column
    op.drop_column('tasks', 'goal_id')
