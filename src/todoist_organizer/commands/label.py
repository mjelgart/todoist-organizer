"""Auto-label unlabeled tasks using Claude."""

from ..client import TodoistClient
from ..llm import classify_tasks_batched
from .. import config


def run_label(dry_run: bool = False):
    """
    Auto-label unlabeled tasks using Claude 4.5 Haiku.

    Prints a summary of all changes.
    """
    client = TodoistClient()

    # Fetch unlabeled tasks
    tasks = client.get_tasks(filter=config.NO_LABEL_FILTER)

    if not tasks:
        print("No unlabeled tasks found.")
        return

    # Skip tasks that already have labels (belt and suspenders)
    unlabeled_tasks = [task for task in tasks if not task.labels]

    if not unlabeled_tasks:
        print("No unlabeled tasks found (all tasks have labels).")
        return

    print(f"{'[DRY RUN] ' if dry_run else ''}Classifying {len(unlabeled_tasks)} task(s)...\n")

    # Classify tasks
    classifications = classify_tasks_batched(unlabeled_tasks)

    # Apply labels and print summary
    print(f"{'Would label' if dry_run else 'Auto-labeled'} {len(classifications)} task(s):\n")
    print(f"  {'Task':<50} {'Project':<20} {'Label':<10}")
    print(f"  {'-' * 82}")

    for task in unlabeled_tasks:
        label = classifications.get(task.id)
        if not label:
            print(f"  WARNING: No label assigned for task {task.id}")
            continue

        # Truncate task content for display
        task_display = task.content[:47] + "..." if len(task.content) > 50 else task.content
        project_display = str(task.project_id)[:17] + "..." if len(str(task.project_id)) > 20 else str(task.project_id)

        print(f"  {task_display:<50} {project_display:<20} {label:<10}")

        if not dry_run:
            client.update_task_labels(task.id, [label])

    print(f"\n{'Would label' if dry_run else 'Labeled'} {len(classifications)} task(s)")
