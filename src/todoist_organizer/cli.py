"""CLI entry point for todoist-organizer."""

import argparse
import sys
from .commands.bump import run_bump
from .commands.label import run_label


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="todoist-organizer",
        description="Automate Todoist task management",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Bump command
    bump_parser = subparsers.add_parser(
        "bump",
        help="Bump overdue Meta tasks to next business day",
    )
    bump_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making actual changes",
    )

    # Label command
    label_parser = subparsers.add_parser(
        "label",
        help="Auto-label unlabeled tasks using Claude",
    )
    label_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making actual changes",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "bump":
            run_bump(dry_run=args.dry_run)
        elif args.command == "label":
            run_label(dry_run=args.dry_run)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
