"""Claude API integration for task classification."""

import json
from anthropic import Anthropic
from todoist_api_python.models import Task
from . import config


def classify_tasks(tasks: list[Task]) -> dict[str, str]:
    """
    Classify tasks using Claude 4.5 Haiku.

    Returns a dict mapping task_id -> label ("home", "pc", or "anywhere").
    """
    if not tasks:
        return {}

    config.validate_config()
    client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

    # Build the prompt
    prompt = """You are classifying Todoist tasks into exactly one label. The labels are:
- "home": Something that must be done physically at home (chores, home repair, cooking, etc.)
- "pc": Requires a desktop computer (coding, spreadsheets, detailed research, etc.)
- "anywhere": Can be done from a phone or anywhere (quick calls, messages, simple lookups, etc.)

For each task, return a JSON object mapping task ID to label.

Tasks:
"""

    for task in tasks:
        project_name = getattr(task, "project_id", "Unknown")
        prompt += f'- ID: {task.id} | Content: "{task.content}" | Project: "{project_name}"\n'

    prompt += '\nReturn ONLY a JSON object like: {"task_id_1": "label", "task_id_2": "label", ...}'

    # Call Claude
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    # Parse response
    response_text = message.content[0].text.strip()

    # Try to extract JSON if wrapped in markdown
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()

    try:
        classifications = json.loads(response_text)
        return classifications
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM response as JSON: {response_text[:200]}") from e


def classify_tasks_batched(tasks: list[Task], batch_size: int = 30) -> dict[str, str]:
    """
    Classify tasks in batches to stay within context limits.

    Returns a dict mapping task_id -> label.
    """
    results = {}

    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i + batch_size]
        batch_results = classify_tasks(batch)
        results.update(batch_results)

    return results
