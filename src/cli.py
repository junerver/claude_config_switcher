"""
CLI entry point for the Claude Code Configuration Switcher.
"""

import argparse
import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import setup_logging
from utils.paths import detect_claude_config_path
from models.config import AppConfig, get_default_config_path
from services.profile_service import ProfileService
from services.config_service import ConfigService

def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Claude Code Configuration Switcher - CLI Mode",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Global options
    parser.add_argument(
        "--config-path",
        type=str,
        help="Override Claude Code settings.json path"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "yaml"],
        default="text",
        help="Output format"
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="claude-config-switcher 0.1.0"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Profile commands
    profile_parser = subparsers.add_parser("profile", help="Profile management")
    profile_subparsers = profile_parser.add_subparsers(dest="profile_command")

    # profile list
    list_parser = profile_subparsers.add_parser("list", help="List all profiles")
    list_parser.add_argument(
        "--active-only",
        action="store_true",
        help="Show only currently active profile"
    )
    list_parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format"
    )

    # profile show
    show_parser = profile_subparsers.add_parser("show", help="Show profile details")
    show_parser.add_argument(
        "profile_id_or_name",
        help="Profile ID or name"
    )
    show_parser.add_argument(
        "--show-secrets",
        action="store_true",
        help="Show full auth tokens"
    )
    show_parser.add_argument(
        "--format",
        choices=["yaml", "json"],
        default="yaml",
        help="Output format"
    )

    # profile create
    create_parser = profile_subparsers.add_parser("create", help="Create new profile")
    create_parser.add_argument(
        "name",
        help="Profile name"
    )
    create_parser.add_argument(
        "--file",
        type=str,
        help="Read JSON configuration from file"
    )
    create_parser.add_argument(
        "--json",
        type=str,
        help="JSON configuration string"
    )
    create_parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive mode with prompts"
    )

    # profile update
    update_parser = profile_subparsers.add_parser("update", help="Update profile")
    update_parser.add_argument(
        "profile_id_or_name",
        help="Profile ID or name"
    )
    update_parser.add_argument(
        "--name",
        type=str,
        help="New profile name"
    )
    update_parser.add_argument(
        "--file",
        type=str,
        help="Read JSON configuration from file"
    )
    update_parser.add_argument(
        "--json",
        type=str,
        help="JSON configuration string"
    )
    update_parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive mode"
    )

    # profile delete
    delete_parser = profile_subparsers.add_parser("delete", help="Delete profile")
    delete_parser.add_argument(
        "profile_id_or_name",
        help="Profile ID or name"
    )
    delete_parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt"
    )
    delete_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without deleting"
    )

    # profile apply
    apply_parser = profile_subparsers.add_parser("apply", help="Apply profile")
    apply_parser.add_argument(
        "profile_id_or_name",
        help="Profile ID or name"
    )
    apply_parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backup"
    )
    apply_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be applied without applying"
    )

    # profile duplicate
    duplicate_parser = profile_subparsers.add_parser("duplicate", help="Duplicate profile")
    duplicate_parser.add_argument(
        "source_id_or_name",
        help="Source profile ID or name"
    )
    duplicate_parser.add_argument(
        "new_name",
        help="Name for duplicated profile"
    )

    # Config commands
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_subparsers = config_parser.add_subparsers(dest="config_command")

    # config status
    config_parser.add_argument("status", help="Show configuration status")

    # config backup
    backup_parser = config_subparsers.add_parser("backup", help="Backup management")
    backup_parser.add_argument(
        "--list",
        action="store_true",
        help="List available backups"
    )
    backup_parser.add_argument(
        "--restore",
        type=str,
        help="Restore from backup"
    )
    backup_parser.add_argument(
        "--cleanup",
        type=int,
        help="Keep only N most recent backups"
    )

    return parser

def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(level=args.log_level, console_output=True)
    logger.debug(f"CLI arguments: {vars(args)}")

    # Initialize services
    try:
        claude_config_path = args.config_path
        if claude_config_path:
            claude_config_path = Path(claude_config_path)
        else:
            claude_config_path = detect_claude_config_path()

        if not claude_config_path:
            print("Error: Claude Code configuration not found", file=sys.stderr)
            print("Use --config-path to specify location", file=sys.stderr)
            sys.exit(3)

        config_service = ConfigService()
        profile_service = ProfileService()

        # Route to appropriate command handler
        if args.command == "profile":
            handle_profile_command(args, profile_service, config_service, claude_config_path)
        elif args.command == "config":
            handle_config_command(args, profile_service, config_service, claude_config_path)
        else:
            parser.print_help()
            sys.exit(2)

    except Exception as e:
        logger.error(f"CLI error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def handle_profile_command(args, profile_service, config_service, claude_config_path):
    """Handle profile-related commands."""
    if args.profile_command == "list":
        profiles = profile_service.get_all_profiles()
        if args.active_only:
            profiles = [p for p in profiles if p.get('is_active')]

        if args.format == "table":
            print(f"{'ID':<5} {'Name':<20} {'Base URL':<30} {'Active':<8} {'Updated':<20}")
            print("-" * 85)
            for profile in profiles:
                config = json.loads(profile['config_json'])
                base_url = config.get('env', {}).get('ANTHROPIC_BASE_URL', 'N/A')
                active = "✓" if profile['is_active'] else "✗"
                updated = profile['updated_at'][:19] if profile['updated_at'] else 'N/A'
                print(f"{profile['id']:<5} {profile['name']:<20} {base_url[:30]:<30} {active:<8} {updated:<20}")
        else:
            output = {"profiles": profiles, "total": len(profiles)}
            print(json.dumps(output, indent=2))

    elif args.profile_command == "show":
        profile = profile_service.get_profile_by_name_or_id(args.profile_id_or_name)
        if not profile:
            print(f"Error: Profile '{args.profile_id_or_name}' not found", file=sys.stderr)
            sys.exit(3)

        if args.format == "yaml":
            print(f"id: {profile['id']}")
            print(f"name: {profile['name']}")
            print(f"config_json: |")
            config_lines = profile['config_json'].split('\n')
            for line in config_lines:
                print(f"  {line}")
            print(f"created_at: {profile['created_at']}")
            print(f"updated_at: {profile['updated_at']}")
            print(f"is_active: {profile['is_active']}")
        else:
            print(json.dumps(profile, indent=2))

    elif args.profile_command == "create":
        if args.interactive:
            print(f"Enter profile name: {args.name}")
            print("Enter JSON configuration (press Ctrl+D when done):")
            config_content = sys.stdin.read()
        elif args.file:
            with open(args.file, 'r') as f:
                config_content = f.read()
        elif args.json:
            config_content = args.json
        else:
            print("Error: Must provide --file, --json, or --interactive", file=sys.stderr)
            sys.exit(2)

        # Validate JSON
        try:
            json.loads(config_content)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(5)

        profile_id = profile_service.create_profile(args.name, config_content)
        print(f"Profile created successfully!")
        print(f"ID: {profile_id}")
        print(f"Name: {args.name}")

    else:
        print(f"Error: Unknown profile command: {args.profile_command}", file=sys.stderr)
        sys.exit(2)

def handle_config_command(args, profile_service, config_service, claude_config_path):
    """Handle configuration-related commands."""
    if args.config_command == "status":
        print("Claude Code Configuration Status")
        print("=" * 40)
        print(f"Config Path: {claude_config_path}")

        active_profile = profile_service.get_active_profile()
        if active_profile:
            print(f"Active Profile: {active_profile['name']} (ID: {active_profile['id']})")
        else:
            print("Active Profile: None")

        # Get config modification time
        if claude_config_path.exists():
            import datetime
            mtime = datetime.datetime.fromtimestamp(claude_config_path.stat().st_mtime)
            print(f"Config Modified: {mtime}")

        # Count backups
        backup_dir = claude_config_path.parent / "backups"
        if backup_dir.exists():
            backup_files = list(backup_dir.glob("settings.json.backup.*"))
            print(f"Backup Count: {len(backup_files)}")

        print(f"Total Profiles: {len(profile_service.get_all_profiles())}")

    elif args.config_command == "backup":
        if args.list:
            backup_dir = claude_config_path.parent / "backups"
            if backup_dir.exists():
                backups = sorted(backup_dir.glob("settings.json.backup.*"), reverse=True)
                print("Available Backups:")
                for i, backup in enumerate(backups, 1):
                    mtime = datetime.datetime.fromtimestamp(backup.stat().st_mtime)
                    size = backup.stat().st_size
                    print(f"{i}. {backup.name} ({mtime}) - {size} bytes")
            else:
                print("No backups found")
        else:
            backup_path = config_service.create_backup(str(claude_config_path), str(claude_config_path.parent / "backups"))
            print(f"Backup created: {backup_path}")

    else:
        print(f"Error: Unknown config command: {args.config_command}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()