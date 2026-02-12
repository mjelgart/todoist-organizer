# todoist-organizer

A CLI tool to automate recurring Todoist maintenance tasks:
- **Bump overdue tasks**: Move overdue Meta tasks to the next business day
- **Auto-label tasks**: Classify unlabeled tasks using Claude 4.5 Haiku

## Setup

1. Clone the repository:
```bash
git clone https://github.com/mjelgart/todoist-organizer.git
cd todoist-organizer
```

2. Create a `.env` file with your API tokens:
```bash
cp .env.example .env
# Edit .env and add your tokens
```

Required environment variables:
- `TODOIST_API_TOKEN`: Your Todoist API token (Settings → Integrations → Developer)
- `ANTHROPIC_API_KEY`: Your Anthropic API key

3. Install the package:
```bash
pip install -e .
```

## Usage

### Bump overdue Meta tasks

Move overdue tasks in the Meta project (and subprojects) to the next business day:

```bash
# Dry run (see what would change)
todoist-organizer bump --dry-run

# Apply changes
todoist-organizer bump
```

After 6pm CT, this also moves today's remaining Meta tasks to the next business day.

### Auto-label unlabeled tasks

Classify unlabeled tasks into `home`, `pc`, or `anywhere` labels:

```bash
# Dry run (see proposed labels)
todoist-organizer label --dry-run

# Apply labels
todoist-organizer label
```

Label definitions:
- **home**: Tasks that must be done physically at home (chores, repairs, cooking)
- **pc**: Tasks requiring a desktop computer (coding, spreadsheets, detailed work)
- **anywhere**: Tasks that can be done from a phone (calls, messages, quick lookups)

## Development

The project uses a simple Python package structure with `pyproject.toml`. Key files:

- `src/todoist_organizer/cli.py`: CLI entry point
- `src/todoist_organizer/config.py`: Configuration and environment loading
- `src/todoist_organizer/client.py`: Todoist API wrapper
- `src/todoist_organizer/llm.py`: Claude API integration
- `src/todoist_organizer/commands/`: Command implementations

## Requirements

- Python 3.11+
- todoist-api-python
- anthropic
- python-dotenv
