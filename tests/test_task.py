"""Tests for the Task model."""

import json
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


def test_task_due_date_default():
    task = Task(title="No due date")
    assert task.due_date is None


def test_task_due_date_set():
    due = datetime(2026, 12, 31, tzinfo=timezone.utc)
    task = Task(title="With due date", due_date=due)
    assert task.due_date == due


def test_to_dict_all_fields():
    created = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    task = Task(
        title="Test task",
        description="A description",
        priority=Priority.HIGH,
        status=Status.TODO,
        tags=["urgent", "work"],
        created_at=created,
    )
    d = task.to_dict()
    assert d["title"] == "Test task"
    assert d["description"] == "A description"
    assert d["priority"] == "high"
    assert d["status"] == "todo"
    assert d["tags"] == ["urgent", "work"]
    assert d["created_at"] == "2026-01-15T12:00:00+00:00"
    assert d["completed_at"] is None


def test_to_dict_enum_values():
    task = Task(title="X", priority=Priority.LOW, status=Status.IN_PROGRESS)
    d = task.to_dict()
    assert d["priority"] == "low"
    assert d["status"] == "in_progress"


def test_to_dict_completed_at_iso():
    task = Task(title="Done")
    task.complete()
    d = task.to_dict()
    assert isinstance(d["completed_at"], str)
    datetime.fromisoformat(d["completed_at"])


def test_to_dict_json_serializable():
    task = Task(title="Serialize me", tags=["a"])
    d = task.to_dict()
    json_str = json.dumps(d)
    assert isinstance(json_str, str)


def test_from_dict():
    data = {
        "title": "Rebuilt",
        "description": "From dict",
        "priority": "high",
        "status": "done",
        "tags": ["test"],
        "created_at": "2026-03-01T09:00:00+00:00",
        "completed_at": "2026-03-01T10:00:00+00:00",
    }
    task = Task.from_dict(data)
    assert task.title == "Rebuilt"
    assert task.description == "From dict"
    assert task.priority == Priority.HIGH
    assert task.status == Status.DONE
    assert task.tags == ["test"]
    assert task.created_at == datetime(2026, 3, 1, 9, 0, 0, tzinfo=timezone.utc)
    assert task.completed_at == datetime(2026, 3, 1, 10, 0, 0, tzinfo=timezone.utc)


def test_from_dict_completed_at_none():
    data = {
        "title": "Incomplete",
        "priority": "medium",
        "status": "todo",
        "tags": [],
        "created_at": "2026-01-01T00:00:00+00:00",
        "completed_at": None,
    }
    task = Task.from_dict(data)
    assert task.completed_at is None


def test_round_trip():
    original = Task(
        title="Round trip",
        description="Full cycle",
        priority=Priority.HIGH,
        status=Status.IN_PROGRESS,
        tags=["a", "b"],
        created_at=datetime(2026, 6, 15, 8, 30, 0, tzinfo=timezone.utc),
    )
    rebuilt = Task.from_dict(original.to_dict())
    assert rebuilt.title == original.title
    assert rebuilt.description == original.description
    assert rebuilt.priority == original.priority
    assert rebuilt.status == original.status
    assert rebuilt.tags == original.tags
    assert rebuilt.created_at == original.created_at
    assert rebuilt.completed_at == original.completed_at


def test_round_trip_with_completed():
    original = Task(title="Done task")
    original.complete()
    rebuilt = Task.from_dict(original.to_dict())
    assert rebuilt.status == Status.DONE
    assert rebuilt.completed_at == original.completed_at
