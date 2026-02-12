"""Bump Meta tasks to next business day."""

from datetime import datetime, timedelta
import zoneinfo
from ..client import TodoistClient
from .. import config


def get_next_business_day(now: datetime) -> str:
    """
    Calculate the next business day from the given datetime.

    Returns date in YYYY-MM-DD format.
    """
    weekday = now.weekday()  # Monday=0, Sunday=6

    if weekday == 4:  # Friday
        days_ahead = 3
    elif weekday == 5:  # Saturday
        days_ahead = 2
    elif weekday == 6:  # Sunday
        days_ahead = 1
    else:  # Monday-Thursday
        days_ahead = 1

    next_day = now + timedelta(days=days_ahead)
    return next_day.strftime("%Y-%m-%d")


def run_bump(dry_run: bool = False):
    """
    Bump overdue Meta tasks to next business day.

    If after business hours, also bump today's remaining tasks.
    """
    tz = zoneinfo.ZoneInfo(config.TIMEZONE)
    now = datetime.now(tz)

    client = TodoistClient()

    # Fetch overdue Meta tasks
    overdue_tasks = client.get_tasks(filter="##Meta & overdue")

    # If after business hours, also fetch today's tasks
    tasks_to_bump = list(overdue_tasks)
    if now.hour >= config.BUSINESS_HOUR_END:
        today_tasks = client.get_tasks(filter="##Meta & today")
        # Deduplicate by task ID
        existing_ids = {task.id for task in tasks_to_bump}
        for task in today_tasks:
            if task.id not in existing_ids:
                tasks_to_bump.append(task)

    if not tasks_to_bump:
        print("No Meta tasks to bump.")
        return

    next_business_day = get_next_business_day(now)

    print(f"{'[DRY RUN] ' if dry_run else ''}Bumping {len(tasks_to_bump)} task(s) to {next_business_day}:\n")

    for task in tasks_to_bump:
        old_due = task.due.date if task.due else "No due date"
        print(f"  - {task.content[:60]}")
        print(f"    {old_due} → {next_business_day}")

        if not dry_run:
            client.update_task_due(task.id, next_business_day)

    print(f"\n{'Would bump' if dry_run else 'Bumped'} {len(tasks_to_bump)} task(s) to {next_business_day}")
