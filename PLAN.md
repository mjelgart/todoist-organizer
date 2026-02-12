# todoist-organizer Implementation Plan

## Context

A CLI tool to automate recurring Todoist maintenance tasks:
1. Bump overdue/end-of-day Meta tasks to the next business day
2. Auto-label unlabeled tasks using Claude 4.5 Haiku as a fallback classifier

The repo is fresh (just a README). We're building from scratch in Python.

---

## Project Structure

```
todoist-organizer/
├── README.md
├── pyproject.toml              # Package config, dependencies, CLI entry point
├── .env.example                # Template for required env vars
├── .gitignore                  # .env, __pycache__, .venv, etc.
├── src/
│   └── todoist_organizer/
│       ├── __init__.py
│       ├── cli.py              # CLI entry point (argparse)
│       ├── config.py           # Settings, env loading, constants
│       ├── client.py           # Todoist API wrapper (thin layer over SDK)
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── bump.py         # Meta task bumping logic
│       │   └── label.py        # Auto-labeling logic
│       └── llm.py              # Claude API integration for labeling
└── tests/                      # Future: unit tests
    └── __init__.py
```

---

## Dependencies

```toml
[project]
name = "todoist-organizer"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "todoist-api-python>=3.1.0,<4",
    "anthropic>=0.40.0,<1",
    "python-dotenv>=1.0.0,<2",
]

[project.scripts]
todoist-organizer = "todoist_organizer.cli:main"
```

---

## File-by-File Implementation

### 1. `src/todoist_organizer/config.py`

- Load `.env` file using `python-dotenv`
- Read `TODOIST_API_TOKEN` and `ANTHROPIC_API_KEY` from env
- Constants:
  - `TIMEZONE = "US/Central"`
  - `BUSINESS_HOUR_END = 18` (6pm)
  - `META_PROJECT_NAME = "Meta"`
  - `LABELS = ["home", "pc", "anywhere"]`
  - `NO_LABEL_FILTER = "no labels & !##Meta & !##Movies to Watch & !#World of Warcraft & !#Someday & !#Birthdays"`

### 2. `src/todoist_organizer/client.py`

Thin wrapper around `TodoistAPI`:
- `get_tasks(filter: str) -> list[Task]` — wraps `api.get_tasks(filter=...)`
- `update_task_due(task_id: str, date: str) -> None` — wraps `api.update_task(due_date=...)`
- `update_task_labels(task_id: str, labels: list[str]) -> None` — wraps `api.update_task(labels=...)`

### 3. `src/todoist_organizer/commands/bump.py` — Meta Task Bumping

**Logic:**
1. Determine `now` in US/Central timezone
2. Compute `next_business_day`:
   - If today is Friday → Monday
   - If today is Saturday → Monday
   - If today is Sunday → Monday
   - Otherwise → tomorrow
   - (Future: skip holidays)
3. Fetch overdue Meta tasks: `filter="##Meta & overdue"`
4. If current time is after 6pm CT, also fetch today's remaining: `filter="##Meta & today"`
5. Combine and deduplicate task lists
6. For each task:
   - In `--dry-run` mode: print what would change (task content, old due date → new due date)
   - In normal mode: call `update_task_due(task.id, next_business_day)` and print the change
7. Print summary: "Bumped X tasks to {next_business_day}"

### 4. `src/todoist_organizer/llm.py` — Claude Labeling

**Function: `classify_tasks(tasks: list[Task]) -> dict[str, str]`**
- Takes a batch of unlabeled tasks
- Builds a prompt like:

```
You are classifying Todoist tasks into exactly one label. The labels are:
- "home": Something that must be done physically at home (chores, home repair, cooking, etc.)
- "pc": Requires a desktop computer (coding, spreadsheets, detailed research, etc.)
- "anywhere": Can be done from a phone or anywhere (quick calls, messages, simple lookups, etc.)

For each task, return a JSON object mapping task ID to label.

Tasks:
- ID: 123 | Content: "Fix kitchen faucet" | Project: "Home Improvement"
- ID: 456 | Content: "Review PR for auth service" | Project: "Work"
...
```

- Calls Claude 4.5 Haiku (`claude-haiku-4-5-20251001`) with this prompt
- Parses the JSON response into `{task_id: label}`
- Batch tasks in groups of ~30 to stay within context limits and keep responses reliable

### 5. `src/todoist_organizer/commands/label.py` — Auto-Label Command

**Logic:**
1. Fetch unlabeled tasks using the filter: `"no labels & !##Meta & !##Movies to Watch & !#World of Warcraft & !#Someday & !#Birthdays"`
2. If no tasks found, print "No unlabeled tasks found" and exit
3. Pass tasks to `classify_tasks()` from `llm.py`
4. For each task + assigned label:
   - In `--dry-run` mode: print proposed label (task content → label)
   - In normal mode: call `update_task_labels(task.id, [label])` and print the change
5. Print a formatted summary table:

```
Auto-labeled 12 tasks:
  Task                          Project          Label
  ─────────────────────────────────────────────────────
  Fix kitchen faucet            Home Improvement  home
  Review PR for auth service    Work              pc
  Call dentist for appointment  Health            anywhere
  ...
```

### 6. `src/todoist_organizer/cli.py` — CLI Entry Point

Using `argparse` with subcommands:

```
todoist-organizer bump [--dry-run]
todoist-organizer label [--dry-run]
```

- `bump`: Runs the Meta task bumping command
- `label`: Runs the auto-labeling command
- `--dry-run`: Global flag, prints changes without applying them

### 7. Other Files

- **`.env.example`**: Template with `TODOIST_API_TOKEN=` and `ANTHROPIC_API_KEY=`
- **`.gitignore`**: `.env`, `__pycache__/`, `.venv/`, `*.egg-info/`, `dist/`
- **`README.md`**: Updated with setup instructions and usage examples

---

## Key Design Decisions

1. **Filter queries via API**: The Todoist Python SDK supports filter query syntax directly in `get_tasks(filter=...)`, so we can reuse the exact filter strings from the Todoist app. This means `##Meta` handles subprojects automatically.

2. **Dry-run by default? No.** Dry-run is opt-in via `--dry-run` flag, but the label command always prints what it changed so the user can review. We could revisit making dry-run the default for labeling later.

3. **Batching LLM calls**: Send ~30 tasks per Claude call to balance cost and reliability. Include task content and project name as context for better classification.

4. **Label assignment replaces (not appends)**: Since these tasks have no labels, setting `labels=[assigned_label]` is safe. If a task somehow already has labels, we should skip it (belt and suspenders).

5. **Simple Python package structure**: Using `pyproject.toml` with a `src/` layout. No framework overhead — just argparse for CLI. Easy to extend with new commands later.

---

## Verification / Testing

1. **Setup**: Clone repo, create `.env` with real tokens, `pip install -e .`
2. **Bump dry-run**: `todoist-organizer bump --dry-run` — verify it lists the correct overdue Meta tasks and the computed next business day
3. **Bump live**: `todoist-organizer bump` — verify tasks are actually moved in Todoist
4. **Label dry-run**: `todoist-organizer label --dry-run` — verify the LLM classifications look reasonable
5. **Label live**: `todoist-organizer label` — verify labels are applied in Todoist, review the printed summary
6. **Edge cases to test manually**:
   - Run bump on a Friday evening (should target Monday)
   - Run bump when there are no overdue tasks
   - Run label when there are no unlabeled tasks
   - Tasks with due times (not just dates) should preserve the time component if possible
