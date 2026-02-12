"""Configuration and environment loading."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# API credentials
TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Timezone and business hours
TIMEZONE = "US/Central"
BUSINESS_HOUR_END = 18  # 6pm

# Project and label constants
META_PROJECT_NAME = "Meta"
LABELS = ["home", "pc", "anywhere"]

# Filter for unlabeled tasks
NO_LABEL_FILTER = "no labels & !##Meta & !##Movies to Watch & !#World of Warcraft & !#Someday & !#Birthdays"


def validate_config():
    """Validate required environment variables are set."""
    missing = []
    if not TODOIST_API_TOKEN:
        missing.append("TODOIST_API_TOKEN")
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Please set them in your .env file or environment."
        )
