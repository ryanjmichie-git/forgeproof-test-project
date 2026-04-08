"""Tests for the TaskStore."""

from datetime import datetime, timezone, timedelta

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


def test_filter_overdue():
    store = TaskStore()
    past = datetime.now(timezone.utc) - timedelta(days=1)
    future = datetime.now(timezone.utc) + timedelta(days=1)
    store.add(Task(title="Overdue", due_date=past))
    store.add(Task(title="Not yet due", due_date=future))
    store.add(Task(title="No due date"))
    done_task = Task(title="Done overdue", due_date=past)
    done_task.complete()
    store.add(done_task)
    overdue = store.filter_overdue()
    assert len(overdue) == 1
    assert overdue[0][1].title == "Overdue"


def test_filter_overdue_empty():
    store = TaskStore()
    store.add(Task(title="No due date"))
    assert store.filter_overdue() == []


def test_filter_due_before():
    store = TaskStore()
    day1 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    day2 = datetime(2026, 6, 1, tzinfo=timezone.utc)
    day3 = datetime(2026, 12, 1, tzinfo=timezone.utc)
    store.add(Task(title="Early", due_date=day1))
    store.add(Task(title="Mid", due_date=day2))
    store.add(Task(title="Late", due_date=day3))
    store.add(Task(title="No date"))
    results = store.filter_due_before(datetime(2026, 7, 1, tzinfo=timezone.utc))
    assert len(results) == 2
    titles = {t.title for _, t in results}
    assert titles == {"Early", "Mid"}


def test_search_by_title():
    store = TaskStore()
    store.add(Task(title="Buy groceries"))
    store.add(Task(title="Write report"))
    store.add(Task(title="Buy birthday gift"))
    results = store.search("buy")
    assert len(results) == 2
    titles = {t.title for _, t in results}
    assert titles == {"Buy groceries", "Buy birthday gift"}


def test_search_case_insensitive():
    store = TaskStore()
    store.add(Task(title="Deploy API"))
    assert len(store.search("deploy")) == 1
    assert len(store.search("DEPLOY")) == 1
    assert len(store.search("Deploy")) == 1


def test_search_no_match():
    store = TaskStore()
    store.add(Task(title="Buy groceries"))
    assert store.search("report") == []


def test_search_empty_query():
    store = TaskStore()
    store.add(Task(title="A"))
    store.add(Task(title="B"))
    results = store.search("")
    assert len(results) == 2


def test_filter_by_tag():
    store = TaskStore()
    store.add(Task(title="Tagged", tags=["urgent", "home"]))
    store.add(Task(title="Other", tags=["work"]))
    store.add(Task(title="No tags"))
    results = store.filter_by_tag("urgent")
    assert len(results) == 1
    assert results[0][1].title == "Tagged"


def test_filter_by_tag_no_match():
    store = TaskStore()
    store.add(Task(title="Task", tags=["work"]))
    assert store.filter_by_tag("home") == []
