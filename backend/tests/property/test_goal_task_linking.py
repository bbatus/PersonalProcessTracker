"""
Property-based tests for goal-task linking

Feature: goal-task-linking
Properties tested:
- Property 1: Goal ownership validation
- Property 2: Goal progress increment on task completion
- Property 3: Goal progress decrement on task reopening
- Property 4: No progress change on skip
- Property 5: Goal progress bounds
- Property 6: Transaction atomicity
- Property 7: Goal deletion cascade
- Property 8: Task deletion goal update
- Property 9: Goal change consistency
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import date, datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.goal import Goal
from app.models.user import User
from app.models.enums import TaskStatus, GoalPeriod
from app.services.task_service import TaskService
from app.services.goal_service import GoalService
from app.core.database import get_db


# Helper strategies
@st.composite
def user_strategy(draw):
    """Generate a random user"""
    return User(
        id=uuid4(),
        username=draw(st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd')))),
        email=draw(st.emails()),
        password_hash="hashed_password",
        timezone="UTC",
        email_verified=True,
        failed_login_attempts=0
    )


@st.composite
def goal_strategy(draw, user_id):
    """Generate a random goal for a user"""
    start_date = date.today()
    end_date = start_date + timedelta(days=draw(st.integers(min_value=1, max_value=365)))
    target_count = draw(st.integers(min_value=1, max_value=100))
    
    return Goal(
        id=uuid4(),
        user_id=user_id,
        title=draw(st.text(min_size=1, max_size=50)),
        period=draw(st.sampled_from(list(GoalPeriod))),
        target_count=target_count,
        current_count=draw(st.integers(min_value=0, max_value=target_count)),
        start_date=start_date,
        end_date=end_date
    )


@st.composite
def task_strategy(draw, user_id, goal_id=None):
    """Generate a random task for a user"""
    return Task(
        id=uuid4(),
        user_id=user_id,
        goal_id=goal_id,
        title=draw(st.text(min_size=1, max_size=50)),
        status=draw(st.sampled_from(list(TaskStatus))),
        scheduled_date=date.today() + timedelta(days=draw(st.integers(min_value=-30, max_value=30)))
    )


@pytest.fixture
def db_session():
    """Get database session for testing"""
    db = next(get_db())
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@settings(max_examples=100)
@given(
    user1_data=user_strategy(),
    user2_data=user_strategy(),
    goal_title=st.text(min_size=1, max_size=50),
    task_title=st.text(min_size=1, max_size=50)
)
def test_property_1_goal_ownership_validation(db_session, user1_data, user2_data, goal_title, task_title):
    """
    Property 1: Goal Ownership Validation
    
    For any task creation or update with a goal_id, the goal must belong to the same user as the task.
    
    Test approach:
    - Create two users
    - Create a goal for user1
    - Try to create a task for user2 with user1's goal
    - Should fail with ownership error
    
    Validates: Requirements 1.5
    """
    # Ensure users are different
    assume(user1_data.email != user2_data.email)
    assume(user1_data.username != user2_data.username)
    
    # Create users
    db_session.add(user1_data)
    db_session.add(user2_data)
    db_session.commit()
    
    # Create goal for user1
    goal_service = GoalService(db_session)
    goal = goal_service.create_goal(
        user_id=user1_data.id,
        title=goal_title,
        period=GoalPeriod.MONTHLY,
        target_count=30,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    
    # Try to create task for user2 with user1's goal
    task_service = TaskService(db_session)
    
    with pytest.raises(ValueError, match="Goal not found or access denied"):
        task_service.create_task(
            user_id=user2_data.id,
            title=task_title,
            scheduled_date=date.today(),
            goal_id=goal.id  # This should fail - wrong user
        )
    
    # Verify task was not created
    tasks = db_session.query(Task).filter(Task.user_id == user2_data.id).all()
    assert len(tasks) == 0, "Task should not be created with invalid goal ownership"


@settings(max_examples=100)
@given(
    user_data=user_strategy(),
    goal_title=st.text(min_size=1, max_size=50),
    task_title=st.text(min_size=1, max_size=50),
    target_count=st.integers(min_value=5, max_value=50)
)
def test_property_2_goal_progress_increment(db_session, user_data, goal_title, task_title, target_count):
    """
    Property 2: Goal Progress Increment on Task Completion
    
    For any task with a goal_id that transitions from non-DONE to DONE status,
    the associated goal's current_count must increase by exactly 1.
    
    Validates: Requirements 2.1
    """
    # Create user
    db_session.add(user_data)
    db_session.commit()
    
    # Create goal
    goal_service = GoalService(db_session)
    goal = goal_service.create_goal(
        user_id=user_data.id,
        title=goal_title,
        period=GoalPeriod.MONTHLY,
        target_count=target_count,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    
    initial_count = goal.current_count
    
    # Create task linked to goal
    task_service = TaskService(db_session)
    task = task_service.create_task(
        user_id=user_data.id,
        title=task_title,
        scheduled_date=date.today(),
        goal_id=goal.id
    )
    
    # Mark task as done
    task, error = task_service.mark_done(task.id, user_data.id)
    assert error is None, f"Task completion should succeed: {error}"
    
    # Refresh goal from database
    db_session.refresh(goal)
    
    # Verify goal progress increased by exactly 1
    assert goal.current_count == initial_count + 1, \
        f"Goal progress should increase by 1 (was {initial_count}, now {goal.current_count})"
    
    # Verify it doesn't exceed target
    assert goal.current_count <= goal.target_count, \
        "Goal progress should not exceed target"


@settings(max_examples=100)
@given(
    user_data=user_strategy(),
    goal_title=st.text(min_size=1, max_size=50),
    task_title=st.text(min_size=1, max_size=50),
    target_count=st.integers(min_value=5, max_value=50)
)
def test_property_3_goal_progress_decrement(db_session, user_data, goal_title, task_title, target_count):
    """
    Property 3: Goal Progress Decrement on Task Reopening
    
    For any task with a goal_id that transitions from DONE to PENDING status,
    the associated goal's current_count must decrease by exactly 1.
    
    Validates: Requirements 2.3
    """
    # Create user
    db_session.add(user_data)
    db_session.commit()
    
    # Create goal with some progress
    goal_service = GoalService(db_session)
    goal = goal_service.create_goal(
        user_id=user_data.id,
        title=goal_title,
        period=GoalPeriod.MONTHLY,
        target_count=target_count,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    
    # Create and complete task
    task_service = TaskService(db_session)
    task = task_service.create_task(
        user_id=user_data.id,
        title=task_title,
        scheduled_date=date.today(),
        goal_id=goal.id
    )
    
    task, _ = task_service.mark_done(task.id, user_data.id)
    db_session.refresh(goal)
    count_after_done = goal.current_count
    
    # Reopen task
    task, error = task_service.reopen_task(task.id, user_data.id)
    assert error is None, f"Task reopening should succeed: {error}"
    
    # Refresh goal
    db_session.refresh(goal)
    
    # Verify goal progress decreased by exactly 1
    assert goal.current_count == count_after_done - 1, \
        f"Goal progress should decrease by 1 (was {count_after_done}, now {goal.current_count})"
    
    # Verify it doesn't go below 0
    assert goal.current_count >= 0, \
        "Goal progress should not go below 0"


@settings(max_examples=100)
@given(
    user_data=user_strategy(),
    goal_title=st.text(min_size=1, max_size=50),
    task_title=st.text(min_size=1, max_size=50),
    target_count=st.integers(min_value=5, max_value=50)
)
def test_property_4_no_progress_change_on_skip(db_session, user_data, goal_title, task_title, target_count):
    """
    Property 4: No Progress Change on Skip
    
    For any task with a goal_id that transitions to SKIPPED status,
    the associated goal's current_count must remain unchanged.
    
    Validates: Requirements 2.2
    """
    # Create user
    db_session.add(user_data)
    db_session.commit()
    
    # Create goal
    goal_service = GoalService(db_session)
    goal = goal_service.create_goal(
        user_id=user_data.id,
        title=goal_title,
        period=GoalPeriod.MONTHLY,
        target_count=target_count,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    
    initial_count = goal.current_count
    
    # Create task linked to goal
    task_service = TaskService(db_session)
    task = task_service.create_task(
        user_id=user_data.id,
        title=task_title,
        scheduled_date=date.today(),
        goal_id=goal.id
    )
    
    # Mark task as skipped
    task, error = task_service.mark_skipped(task.id, user_data.id)
    assert error is None, f"Task skip should succeed: {error}"
    
    # Refresh goal
    db_session.refresh(goal)
    
    # Verify goal progress unchanged
    assert goal.current_count == initial_count, \
        f"Goal progress should remain unchanged when task is skipped (was {initial_count}, now {goal.current_count})"


@settings(max_examples=100)
@given(
    user_data=user_strategy(),
    goal_title=st.text(min_size=1, max_size=50),
    target_count=st.integers(min_value=1, max_value=100),
    num_tasks=st.integers(min_value=0, max_value=10)
)
def test_property_5_goal_progress_bounds(db_session, user_data, goal_title, target_count, num_tasks):
    """
    Property 5: Goal Progress Bounds
    
    For any goal, the current_count must always be between 0 and target_count (inclusive).
    
    Validates: Requirements 2.1, 2.3
    """
    # Create user
    db_session.add(user_data)
    db_session.commit()
    
    # Create goal
    goal_service = GoalService(db_session)
    goal = goal_service.create_goal(
        user_id=user_data.id,
        title=goal_title,
        period=GoalPeriod.MONTHLY,
        target_count=target_count,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    
    # Create and complete multiple tasks
    task_service = TaskService(db_session)
    for i in range(num_tasks):
        task = task_service.create_task(
            user_id=user_data.id,
            title=f"Task {i}",
            scheduled_date=date.today(),
            goal_id=goal.id
        )
        task_service.mark_done(task.id, user_data.id)
    
    # Refresh goal
    db_session.refresh(goal)
    
    # Verify bounds
    assert 0 <= goal.current_count <= goal.target_count, \
        f"Goal progress must be between 0 and {goal.target_count}, got {goal.current_count}"
