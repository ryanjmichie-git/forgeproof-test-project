"""In-memory task storage and retrieval."""

from __future__ import annotations

from .task import Priority, Status, Task


class TaskStore:
    """Simple in-memory store for tasks."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, task: Task) -> int:
        """Add a task and return its ID."""
        task_id = self._next_id
        self._tasks[task_id] = task
        self._next_id += 1
        return task_id

    def get(self, task_id: int) -> Task | None:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    def remove(self, task_id: int) -> bool:
        """Remove a task by ID. Returns True if found and removed."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def list_all(self) -> list[tuple[int, Task]]:
        """Return all tasks as (id, task) pairs."""
        return list(self._tasks.items())

    def filter_by_status(self, status: Status) -> list[tuple[int, Task]]:
        """Return tasks matching a given status."""
        return [(tid, t) for tid, t in self._tasks.items() if t.status == status]

    def filter_by_priority(self, priority: Priority) -> list[tuple[int, Task]]:
        """Return tasks matching a given priority."""
        return [(tid, t) for tid, t in self._tasks.items() if t.priority == priority]
