"""Todoist API client wrapper."""

from datetime import datetime
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task
from . import config


class TodoistClient:
    """Thin wrapper around TodoistAPI."""

    def __init__(self):
        config.validate_config()
        self.api = TodoistAPI(config.TODOIST_API_TOKEN)

    def get_tasks(self, filter: str) -> list[Task]:
        """Get tasks matching the filter query."""
        tasks = []
        for page in self.api.filter_tasks(query=filter):
            tasks.extend(page)
        return tasks

    def update_task_due(self, task_id: str, date: str) -> None:
        """Update task due date (YYYY-MM-DD format)."""
        due_datetime = datetime.strptime(date, "%Y-%m-%d")
        self.api.update_task(task_id=task_id, due_date=due_datetime)

    def update_task_labels(self, task_id: str, labels: list[str]) -> None:
        """Update task labels (replaces existing labels)."""
        self.api.update_task(task_id=task_id, labels=labels)
