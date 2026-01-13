"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-01-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('timezone', sa.String(length=50), nullable=False),
        sa.Column('email_verified', sa.Boolean(), nullable=False),
        sa.Column('email_verification_token', sa.String(length=255), nullable=True),
        sa.Column('password_reset_token', sa.String(length=255), nullable=True),
        sa.Column('password_reset_expires', sa.DateTime(), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False),
        sa.Column('account_locked_until', sa.DateTime(), nullable=True),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create categories table
    op.create_table('categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)

    # Create tasks table
    op.create_table('tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'DONE', 'SKIPPED', name='taskstatus'), nullable=False),
        sa.Column('scheduled_date', sa.Date(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)
    op.create_index(op.f('ix_tasks_user_id'), 'tasks', ['user_id'], unique=False)
    op.create_index(op.f('ix_tasks_category_id'), 'tasks', ['category_id'], unique=False)
    op.create_index(op.f('ix_tasks_status'), 'tasks', ['status'], unique=False)
    op.create_index(op.f('ix_tasks_scheduled_date'), 'tasks', ['scheduled_date'], unique=False)
    op.create_index('ix_tasks_user_date', 'tasks', ['user_id', 'scheduled_date'], unique=False)
    op.create_index('ix_tasks_user_status', 'tasks', ['user_id', 'status'], unique=False)
    op.create_index('ix_tasks_user_category', 'tasks', ['user_id', 'category_id'], unique=False)

    # Create goals table
    op.create_table('goals',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('period', sa.Enum('DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY', name='goalperiod'), nullable=False),
        sa.Column('target_count', sa.Integer(), nullable=False),
        sa.Column('current_count', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_goals_id'), 'goals', ['id'], unique=False)
    op.create_index(op.f('ix_goals_user_id'), 'goals', ['user_id'], unique=False)
    op.create_index(op.f('ix_goals_period'), 'goals', ['period'], unique=False)
    op.create_index(op.f('ix_goals_end_date'), 'goals', ['end_date'], unique=False)
    op.create_index('ix_goals_user_period', 'goals', ['user_id', 'period'], unique=False)
    op.create_index('ix_goals_user_end_date', 'goals', ['user_id', 'end_date'], unique=False)

    # Create habits table
    op.create_table('habits',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('frequency', sa.Enum('DAILY', 'WEEKLY', name='habitfrequency'), nullable=False),
        sa.Column('target_days', sa.Integer(), nullable=True),
        sa.Column('current_streak', sa.Integer(), nullable=False),
        sa.Column('longest_streak', sa.Integer(), nullable=False),
        sa.Column('last_completed', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_habits_id'), 'habits', ['id'], unique=False)
    op.create_index(op.f('ix_habits_user_id'), 'habits', ['user_id'], unique=False)

    # Create habit_logs table
    op.create_table('habit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('habit_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('completed_date', sa.Date(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['habit_id'], ['habits.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('habit_id', 'completed_date', name='uq_habit_log_date')
    )
    op.create_index(op.f('ix_habit_logs_id'), 'habit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_habit_logs_habit_id'), 'habit_logs', ['habit_id'], unique=False)
    op.create_index(op.f('ix_habit_logs_completed_date'), 'habit_logs', ['completed_date'], unique=False)

    # Create monthly_summaries table
    op.create_table('monthly_summaries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('month', sa.Date(), nullable=False),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('total_tasks', sa.Integer(), nullable=True),
        sa.Column('completed_tasks', sa.Integer(), nullable=True),
        sa.Column('what_went_well', sa.Text(), nullable=False),
        sa.Column('what_went_bad', sa.Text(), nullable=False),
        sa.Column('what_to_change', sa.Text(), nullable=False),
        sa.Column('average_mood', sa.Float(), nullable=True),
        sa.CheckConstraint('average_mood >= 1 AND average_mood <= 10', name='ck_average_mood_range'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'month', name='uq_user_month')
    )
    op.create_index(op.f('ix_monthly_summaries_id'), 'monthly_summaries', ['id'], unique=False)
    op.create_index(op.f('ix_monthly_summaries_user_id'), 'monthly_summaries', ['user_id'], unique=False)

    # Create mood_logs table
    op.create_table('mood_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('mood_score', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.CheckConstraint('mood_score >= 1 AND mood_score <= 10', name='ck_mood_score_range'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'date', name='uq_user_mood_date')
    )
    op.create_index(op.f('ix_mood_logs_id'), 'mood_logs', ['id'], unique=False)
    op.create_index(op.f('ix_mood_logs_user_id'), 'mood_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_mood_logs_date'), 'mood_logs', ['date'], unique=False)

    # Insert default categories
    op.execute("""
        INSERT INTO categories (id, created_at, updated_at, name, color) VALUES
        (gen_random_uuid(), NOW(), NOW(), 'Work', '#3B82F6'),
        (gen_random_uuid(), NOW(), NOW(), 'Sport', '#10B981'),
        (gen_random_uuid(), NOW(), NOW(), 'Personal', '#F59E0B'),
        (gen_random_uuid(), NOW(), NOW(), 'Learning', '#8B5CF6')
    """)


def downgrade() -> None:
    op.drop_table('mood_logs')
    op.drop_table('monthly_summaries')
    op.drop_table('habit_logs')
    op.drop_table('habits')
    op.drop_table('goals')
    op.drop_table('tasks')
    op.drop_table('categories')
    op.drop_table('users')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS taskstatus')
    op.execute('DROP TYPE IF EXISTS goalperiod')
    op.execute('DROP TYPE IF EXISTS habitfrequency')
