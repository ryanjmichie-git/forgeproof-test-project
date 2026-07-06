"""Tests for Task priority levels (issue #9)."""

import pytest

from src.task import Priority, Status, Task
from src.task_store import TaskStore


# REQ-1: priority attribute with allowed values low, medium, high; default medium


def test_priority_defaults_to_medium():
    task = Task(title="No priority given")
    assert task.priority == Priority.MEDIUM


def test_priority_accepts_all_allowed_values():
    for priority in (Priority.LOW, Priority.MEDIUM, Priority.HIGH):
        task = Task(title="Explicit priority", priority=priority)
        assert task.priority == priority


def test_priority_accepts_allowed_strings():
    for value in ("low", "medium", "high"):
        task = Task(title="String priority", priority=value)
        assert task.priority == Priority(value)


# REQ-2: any other priority value raises ValueError


def test_invalid_priority_string_at_creation_raises():
    with pytest.raises(ValueError):
        Task(title="Bad", priority="urgent")


def test_invalid_priority_type_at_creation_raises():
    with pytest.raises(ValueError):
        Task(title="Bad", priority=3)


def test_invalid_priority_on_assignment_raises():
    task = Task(title="Good")
    with pytest.raises(ValueError):
        task.priority = "banana"


def test_valid_priority_on_assignment():
    task = Task(title="Good")
    task.priority = Priority.HIGH
    assert task.priority == Priority.HIGH
    task.priority = "low"
    assert task.priority == Priority.LOW


def test_invalid_priority_in_from_dict_raises():
    data = {
        "title": "Bad",
        "priority": "critical",
        "status": "todo",
        "tags": [],
        "created_at": "2026-01-01T00:00:00+00:00",
        "completed_at": None,
    }
    with pytest.raises(ValueError):
        Task.from_dict(data)


# REQ-3: TaskStore.filter_by_priority returns tasks matching the given priority


def test_filter_by_priority_returns_matches():
    store = TaskStore()
    low_id = store.add(Task(title="Low", priority=Priority.LOW))
    store.add(Task(title="Medium"))
    high_id = store.add(Task(title="High", priority=Priority.HIGH))

    high_tasks = store.filter_by_priority(Priority.HIGH)
    assert [(tid, t.title) for tid, t in high_tasks] == [(high_id, "High")]

    low_tasks = store.filter_by_priority(Priority.LOW)
    assert [(tid, t.title) for tid, t in low_tasks] == [(low_id, "Low")]


def test_filter_by_priority_no_match():
    store = TaskStore()
    store.add(Task(title="Medium only"))
    assert store.filter_by_priority(Priority.HIGH) == []


# REQ-4: existing behavior unchanged for tasks that never set a priority


def test_untouched_priority_creation_and_completion():
    task = Task(title="Plain task", description="desc", tags=["a"])
    assert task.priority == Priority.MEDIUM
    assert task.status == Status.TODO
    task.complete()
    assert task.status == Status.DONE
    assert task.completed_at is not None


def test_untouched_priority_serialization_round_trip():
    original = Task(title="Plain task")
    original.complete()
    d = original.to_dict()
    assert d["priority"] == "medium"
    rebuilt = Task.from_dict(d)
    assert rebuilt.priority == Priority.MEDIUM
    assert rebuilt.status == original.status
    assert rebuilt.completed_at == original.completed_at
