"""Tests for the Task model."""

from datetime import datetime, timezone, timedelta

from src.task import Priority, Status, Task


def test_task_defaults():
    task = Task(title="Buy groceries")
    assert task.title == "Buy groceries"
    assert task.priority == Priority.MEDIUM
    assert task.status == Status.TODO
    assert task.tags == []
    assert task.completed_at is None


def test_task_complete():
    task = Task(title="Write report")
    task.complete()
    assert task.status == Status.DONE
    assert task.completed_at is not None


def test_task_not_overdue_when_done():
    task = Task(title="Done task")
    task.complete()
    past = datetime.now(timezone.utc) - timedelta(days=1)
    assert not task.is_overdue(past)


def test_task_overdue():
    task = Task(title="Late task")
    past = datetime.now(timezone.utc) - timedelta(days=1)
    assert task.is_overdue(past)


def test_task_not_overdue():
    task = Task(title="Future task")
    future = datetime.now(timezone.utc) + timedelta(days=1)
    assert not task.is_overdue(future)


def test_complete_idempotent():
    """REQ-1: Calling complete() on a DONE task should be a no-op."""
    task = Task(title="Already done")
    task.complete()
    original_completed_at = task.completed_at
    task.complete()
    assert task.status == Status.DONE
    assert task.completed_at is original_completed_at


def test_complete_from_in_progress():
    """REQ-2: complete() from IN_PROGRESS sets DONE and records completed_at."""
    task = Task(title="In progress task")
    task.status = Status.IN_PROGRESS
    assert task.completed_at is None
    task.complete()
    assert task.status == Status.DONE
    assert task.completed_at is not None
