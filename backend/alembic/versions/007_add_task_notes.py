"""add task notes field

Revision ID: 007_add_task_notes
Revises: d5fb8791f38c
Create Date: 2026-01-11 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007_add_task_notes'
down_revision = 'd5fb8791f38c'
branch_labels = None
depends_on = None


def upgrade():
    # Add notes column to tasks table
    op.add_column('tasks', sa.Column('notes', sa.Text(), nullable=True))


def downgrade():
    # Remove notes column from tasks table
    op.drop_column('tasks', 'notes')
