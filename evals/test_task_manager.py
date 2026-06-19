"""
Evaluation tests for Task Manager — each test maps to a Gherkin scenario.
Run: python -m pytest evals/test_task_manager.py -v
"""
import pytest
from datetime import datetime
from src.task_manager import TaskManager, Task, VALID_PRIORITIES


@pytest.fixture
def empty_tm():
    """Background: Given the system is initialized with an empty task list."""
    return TaskManager()


# --- Scenario: Create a new task ---
def test_create_new_task(empty_tm):
    """When I create a task → Then task list contains 1 task with correct fields."""
    tm = empty_tm
    task = tm.create_task("Design login page", "high")
    assert tm.task_count == 1
    assert task.title == "Design login page"
    assert task.priority == "high"
    assert task.status == "open"
    assert task.assignee is None


# --- Scenario: Assign a task to a user ---
def test_assign_task(empty_tm):
    """Given a task exists → When I assign → Then assignee set, status in_progress."""
    tm = empty_tm
    tm.create_task("Fix navigation bug", "medium")
    task = tm.assign_task("Fix navigation bug", "alice@example.com")
    assert task.assignee == "alice@example.com"
    assert task.status == "in_progress"


# --- Scenario: Complete a task ---
def test_complete_task(empty_tm):
    """Given assigned task → When completed → Then status done, completed_at set."""
    tm = empty_tm
    tm.create_task("Update dependencies", "low")
    tm.assign_task("Update dependencies", "bob@example.com")
    task = tm.complete_task("Update dependencies")
    assert task.status == "done"
    assert task.completed_at is not None
    assert isinstance(task.completed_at, datetime)


# --- Scenario: List tasks by status ---
def test_list_tasks_by_status(empty_tm):
    """Given multiple tasks → When list by status → Then correct count and titles."""
    tm = empty_tm
    tm.create_task("Design login page", "high")
    tm.create_task("Fix navigation bug", "medium")
    tm.create_task("Update deps", "low")
    tm.assign_task("Fix navigation bug", "alice@example.com")
    tm.complete_task("Update deps")

    open_tasks = tm.list_tasks("open")
    assert len(open_tasks) == 1
    assert open_tasks[0].title == "Design login page"


# --- Scenario: Prevent duplicate task titles ---
def test_prevent_duplicate(empty_tm):
    """Given task exists → When create same title → Then error, count unchanged."""
    tm = empty_tm
    tm.create_task("Setup CI pipeline")
    with pytest.raises(ValueError, match="already exists"):
        tm.create_task("Setup CI pipeline")
    assert tm.task_count == 1


# --- Scenario Outline: Validate task priority ---
@pytest.mark.parametrize("priority", ["urgent", "critical", "unknown"])
def test_validate_priority(empty_tm, priority):
    """When create with invalid priority → Then error."""
    tm = empty_tm
    with pytest.raises(ValueError, match=f"Invalid priority: {priority}"):
        tm.create_task("Test task", priority)


# --- Scenario: Search tasks by keyword ---
def test_search_tasks(empty_tm):
    """Given multiple tasks → When search 'design' → Then 2 results."""
    tm = empty_tm
    tm.create_task("Design login page", "high")
    tm.create_task("Fix navigation bug", "medium")
    tm.create_task("Design user dashboard", "medium")

    results = tm.search_tasks("design")
    assert len(results) == 2
    titles = {t.title for t in results}
    assert "Design login page" in titles
    assert "Design user dashboard" in titles


# --- Scenario: Delete a task ---
def test_delete_task(empty_tm):
    """Given task exists → When delete → Then 0 tasks."""
    tm = empty_tm
    tm.create_task("Old feature request")
    tm.delete_task("Old feature request")
    assert tm.task_count == 0


# --- Scenario: Cannot assign a completed task ---
def test_cannot_assign_completed(empty_tm):
    """Given completed task → When assign → Then error, no assignee."""
    tm = empty_tm
    tm.create_task("Already done")
    tm.complete_task("Already done")
    with pytest.raises(ValueError, match="Cannot assign a completed task"):
        tm.assign_task("Already done", "charlie@example.com")
    # Verify task still has no assignee
    tasks = tm.list_tasks()
    assert tasks[0].assignee is None


# --- Edge cases (security/validation) ---
def test_empty_title_rejected(empty_tm):
    """Input validation: empty title."""
    with pytest.raises(ValueError, match="Title cannot be empty"):
        empty_tm.create_task("")


def test_whitespace_title_rejected(empty_tm):
    """Input validation: whitespace-only title."""
    with pytest.raises(ValueError, match="Title cannot be empty"):
        empty_tm.create_task("   ")


def test_empty_assignee_rejected(empty_tm):
    """Input validation: empty assignee."""
    empty_tm.create_task("Test")
    with pytest.raises(ValueError, match="Assignee cannot be empty"):
        empty_tm.assign_task("Test", "")


def test_delete_nonexistent_task(empty_tm):
    """Delete non-existent task raises error."""
    with pytest.raises(ValueError, match="Task not found"):
        empty_tm.delete_task("Ghost task")


def test_invalid_status_filter(empty_tm):
    """List with invalid status raises error."""
    with pytest.raises(ValueError, match="Invalid status"):
        empty_tm.list_tasks("archived")
