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
    due_date: datetime | None = None

    def complete(self) -> None:
        """Mark the task as done. No-op if already done."""
        if self.status == Status.DONE:
            return
        self.status = Status.DONE
        self.completed_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        """Return a JSON-serializable dictionary of all fields."""
        return {
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "tags": list(self.tags),
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        """Reconstruct a Task from a dictionary."""
        return cls(
            title=data["title"],
            description=data.get("description", ""),
            priority=Priority(data["priority"]),
            status=Status(data["status"]),
            tags=list(data.get("tags", [])),
            created_at=datetime.fromisoformat(data["created_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
        )

    def is_overdue(self, deadline: datetime) -> bool:
        """Check if the task is past a given deadline."""
        if self.status == Status.DONE:
            return False
        return datetime.now(timezone.utc) > deadline
