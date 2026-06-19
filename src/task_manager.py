"""
Task Manager API — implementation generated from spec.
Spec-driven: every function traces to a Gherkin scenario.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

VALID_PRIORITIES = {"low", "medium", "high"}
VALID_STATUSES = {"open", "in_progress", "done"}


@dataclass
class Task:
    title: str
    priority: str = "medium"
    status: str = "open"
    assignee: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class TaskManager:
    """Core task management — traces to all scenarios in task-manager.feature."""

    def __init__(self):
        self._tasks: dict[str, Task] = {}  # keyed by title

    # --- Scenario: Create a new task ---
    def create_task(self, title: str, priority: str = "medium") -> Task:
        """T1: Create a new task. Traces to 'Create a new task' + 'Prevent duplicate task titles'."""
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        if title in self._tasks:
            raise ValueError("Task with this title already exists")
        if priority not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority: {priority}")
        task = Task(title=title, priority=priority)
        self._tasks[title] = task
        return task

    # --- Scenario: Assign a task to a user ---
    def assign_task(self, title: str, assignee: str) -> Task:
        """T2: Assign task. Traces to 'Assign a task to a user' + 'Cannot assign a completed task'."""
        task = self._get_task(title)
        if task.status == "done":
            raise ValueError("Cannot assign a completed task")
        if not assignee or not assignee.strip():
            raise ValueError("Assignee cannot be empty")
        task.assignee = assignee
        task.status = "in_progress"
        return task

    # --- Scenario: Complete a task ---
    def complete_task(self, title: str) -> Task:
        """T3: Complete task. Traces to 'Complete a task'."""
        task = self._get_task(title)
        task.status = "done"
        task.completed_at = datetime.now(timezone.utc)
        return task

    # --- Scenario: List tasks by status ---
    def list_tasks(self, status: Optional[str] = None) -> list[Task]:
        """T4: List tasks. Traces to 'List tasks by status'."""
        if status is not None and status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        tasks = list(self._tasks.values())
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        return tasks

    # --- Scenario: Search tasks by keyword ---
    def search_tasks(self, keyword: str) -> list[Task]:
        """T5: Search tasks. Traces to 'Search tasks by keyword'."""
        if not keyword or not keyword.strip():
            return []
        kw = keyword.lower()
        return [t for t in self._tasks.values() if kw in t.title.lower()]

    # --- Scenario: Delete a task ---
    def delete_task(self, title: str) -> None:
        """T6: Delete task. Traces to 'Delete a task'."""
        self._get_task(title)  # validates existence
        del self._tasks[title]

    # --- Helpers ---
    def _get_task(self, title: str) -> Task:
        """Internal: fetch task by title, raise if not found."""
        if title not in self._tasks:
            raise ValueError(f"Task not found: {title}")
        return self._tasks[title]

    @property
    def task_count(self) -> int:
        return len(self._tasks)
