"""
FragMapper CLI - Command-line interface for FragMapper.

Version: 1.0.0
Last-Updated: 2026-01-10

Usage:
    fragmapper --mode DESC_TO_PARFUMO_URL --input "Dior Sauvage EDP 100ml"
    fragmapper --version
    fragmapper --list-modes
"""

import argparse
import sys
from pathlib import Path

from fragmapper.router import FragMapperRouter
from fragmapper.models.schemas import Mode


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="fragmapper",
        description="Map fragrance descriptions to canonical database URLs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fragmapper --mode DESC_TO_PARFUMO_URL --input "Dior Sauvage EDP 100ml"
  fragmapper --mode DESC_TO_PARFUMO_URL -i "Chanel Bleu EDT for men"
  fragmapper --list-modes
  fragmapper --version
        """,
    )

    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Show version information and exit",
    )

    parser.add_argument(
        "--list-modes", "-l",
        action="store_true",
        help="List all supported modes and exit",
    )

    parser.add_argument(
        "--mode", "-m",
        type=str,
        choices=[m.value for m in Mode],
        help="The mode to execute (e.g., DESC_TO_PARFUMO_URL)",
    )

    parser.add_argument(
        "--input", "-i",
        type=str,
        help="The input text to process",
    )

    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output full JSON response instead of simple output",
    )

    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to custom config file (fragmapper_rules.yml)",
    )

    return parser


def main() -> int:
    """Main CLI entrypoint."""
    parser = create_parser()
    args = parser.parse_args()

    # Initialize router
    config_path = Path(args.config) if args.config else None
    try:
        router = FragMapperRouter(config_path=config_path)
    except Exception as e:
        print(f"Error initializing router: {e}", file=sys.stderr)
        return 1

    # Handle --version
    if args.version:
        version_info = router.get_version_info()
        print(f"FragMapper v{version_info['router']}")
        print(f"Config version: {version_info['config_version']}")
        for key, value in version_info.items():
            if key.startswith("skill_"):
                skill_name = key.replace("skill_", "")
                print(f"  {skill_name}: v{value}")
        return 0

    # Handle --list-modes
    if args.list_modes:
        print("Supported modes:")
        for mode in router.supported_modes:
            print(f"  {mode.value}")
        return 0

    # Validate required arguments for processing
    if not args.mode:
        parser.error("--mode is required when processing input")
    if not args.input:
        parser.error("--input is required when processing input")

    # Process input
    try:
        mode = Mode(args.mode)
        result = router.route(mode, args.input)

        if args.json:
            print(result.model_dump_json(indent=2))
        else:
            print(result.to_simple_output())

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
