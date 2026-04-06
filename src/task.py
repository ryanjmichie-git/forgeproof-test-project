"""Task model for the taskflow library."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Status(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


@dataclass
class Task:
    """Represents a single task."""

    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    status: Status = Status.TODO
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None

    def complete(self) -> None:
        """Mark the task as done."""
        self.status = Status.DONE
        self.completed_at = datetime.now(timezone.utc)

    def is_overdue(self, deadline: datetime) -> bool:
        """Check if the task is past a given deadline."""
        if self.status == Status.DONE:
            return False
        return datetime.now(timezone.utc) > deadline
