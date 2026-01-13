from enum import Enum


class TaskStatus(str, Enum):
    """Task status enum"""
    PENDING = "PENDING"
    DONE = "DONE"
    SKIPPED = "SKIPPED"


class GoalPeriod(str, Enum):
    """Goal period enum"""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class HabitFrequency(str, Enum):
    """Habit frequency enum"""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
