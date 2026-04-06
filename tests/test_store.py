"""Tests for the TaskStore."""

from src.task import Priority, Status, Task
from src.task_store import TaskStore


def test_add_and_get():
    store = TaskStore()
    task = Task(title="Test task")
    task_id = store.add(task)
    assert store.get(task_id) is task


def test_remove():
    store = TaskStore()
    task_id = store.add(Task(title="To remove"))
    assert store.remove(task_id) is True
    assert store.get(task_id) is None


def test_remove_nonexistent():
    store = TaskStore()
    assert store.remove(999) is False


def test_list_all():
    store = TaskStore()
    store.add(Task(title="A"))
    store.add(Task(title="B"))
    all_tasks = store.list_all()
    assert len(all_tasks) == 2


def test_filter_by_status():
    store = TaskStore()
    t1 = Task(title="Todo")
    t2 = Task(title="Done")
    t2.complete()
    store.add(t1)
    store.add(t2)
    done_tasks = store.filter_by_status(Status.DONE)
    assert len(done_tasks) == 1
    assert done_tasks[0][1].title == "Done"


def test_filter_by_priority():
    store = TaskStore()
    store.add(Task(title="Low", priority=Priority.LOW))
    store.add(Task(title="High", priority=Priority.HIGH))
    high_tasks = store.filter_by_priority(Priority.HIGH)
    assert len(high_tasks) == 1
    assert high_tasks[0][1].title == "High"
