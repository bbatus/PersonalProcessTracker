"""add_habit_id_to_tasks

Revision ID: cef467df4b0e
Revises: b30fd05bf435
Create Date: 2026-01-11 10:47:04.175668

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cef467df4b0e'
down_revision = 'b30fd05bf435'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add habit_id column to tasks table
    op.add_column('tasks', sa.Column('habit_id', sa.UUID(), nullable=True))
    op.create_index(op.f('ix_tasks_habit_id'), 'tasks', ['habit_id'], unique=False)
    op.create_foreign_key('fk_tasks_habit_id', 'tasks', 'habits', ['habit_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    # Remove habit_id column from tasks table
    op.drop_constraint('fk_tasks_habit_id', 'tasks', type_='foreignkey')
    op.drop_index(op.f('ix_tasks_habit_id'), table_name='tasks')
    op.drop_column('tasks', 'habit_id')
