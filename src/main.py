"""
GUI entry point for the Claude Code Configuration Switcher.
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import setup_logging
from utils.paths import detect_claude_config_path
from models.config import AppConfig, get_default_config_path
from gui.app import Application

def main():
    """Main GUI entry point."""
    parser = argparse.ArgumentParser(
        description="Claude Code Configuration Switcher - GUI Mode"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level"
    )
    parser.add_argument(
        "--config-path",
        type=str,
        help="Path to Claude Code settings.json"
    )
    parser.add_argument(
        "--app-config",
        type=str,
        help="Path to application configuration file"
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(level=args.log_level)
    logger.info("Starting Claude Code Configuration Switcher (GUI Mode)")

    try:
        # Load application configuration
        app_config_path = Path(args.app_config) if args.app_config else get_default_config_path()
        app_config = AppConfig.load_from_file(app_config_path)

        # Detect or use specified Claude config path
        claude_config_path = args.config_path or app_config.claude_config_path
        if claude_config_path:
            claude_config_path = Path(claude_config_path)
        else:
            claude_config_path = detect_claude_config_path()

        if not claude_config_path:
            logger.error("Claude Code configuration not found. Use --config-path to specify.")
            sys.exit(1)

        logger.info(f"Using Claude Code config: {claude_config_path}")

        # Start GUI application
        app = Application(
            claude_config_path=claude_config_path,
            app_config=app_config,
            app_config_path=app_config_path
        )
        app.run()

    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()