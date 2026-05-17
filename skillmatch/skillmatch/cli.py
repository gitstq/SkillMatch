"""Command Line Interface for SkillMatch.

Provides the main CLI entry point using argparse with subcommands for
searching, installing, listing, inspecting, removing, validating,
initializing, and exporting skills.
"""

import argparse
import json
import sys
import os

from skillmatch import __version__
from skillmatch.registry import SkillRegistry
from skillmatch.matcher import SkillMatcher
from skillmatch.indexer import SkillIndexer
from skillmatch.validator import SkillValidator
from skillmatch.installer import SkillInstaller
from skillmatch.tui import TUI
from skillmatch.utils import (
    Colors,
    ensure_dir,
    get_config_dir,
    get_registry_path,
    get_skills_dir,
    now_iso,
    write_json_file,
)


def cmd_init(args):
    """Initialize SkillMatch configuration.

    Creates the configuration directory, registry, and skills directory.

    Args:
        args: Parsed command-line arguments.
    """
    tui = TUI()
    config_dir = get_config_dir()
    registry_path = get_registry_path()
    skills_dir = get_skills_dir()

    ensure_dir(config_dir)
    ensure_dir(skills_dir)

    # Initialize registry with built-in skills
    registry = SkillRegistry(registry_path=registry_path)

    tui.print_init_success(config_dir)
    return 0


def cmd_search(args):
    """Search for skills matching a query.

    Uses the hybrid TF-IDF + BM25 matching engine to find relevant skills.

    Args:
        args: Parsed command-line arguments with 'query', 'framework',
              'tag', 'top', and 'all' attributes.
    """
    tui = TUI()
    registry = SkillRegistry()
    matcher = SkillMatcher(registry)

    try:
        results = matcher.search(
            query=args.query,
            top_k=args.top,
            framework=args.framework,
            tags=args.tag if args.tag else None,
        )
        tui.print_search_results(results, query=args.query)
    except Exception as e:
        tui.print_error(f"Search failed: {e}")
        return 1

    return 0


def cmd_install(args):
    """Install a skill by name.

    Args:
        args: Parsed command-line arguments with 'name' attribute.
    """
    tui = TUI()
    registry = SkillRegistry()
    installer = SkillInstaller(registry)

    try:
        skill = installer.install(args.name)
        tui.print_install_progress(
            skill.name,
            success=True,
            message=f"v{skill.version} installed to {skill.install_path}",
        )
    except ValueError as e:
        tui.print_error(str(e))
        return 1
    except Exception as e:
        tui.print_error(f"Installation failed: {e}")
        return 1

    return 0


def cmd_list(args):
    """List skills in the registry.

    Args:
        args: Parsed command-line arguments with 'all' attribute.
    """
    tui = TUI()
    registry = SkillRegistry()

    if args.all:
        skills = registry.list_all()
        tui.print_skill_list(skills, title="All Skills")
    else:
        skills = registry.list_installed()
        tui.print_skill_list(skills, title="Installed Skills")

    return 0


def cmd_info(args):
    """Display detailed information about a skill.

    Args:
        args: Parsed command-line arguments with 'name' attribute.
    """
    tui = TUI()
    registry = SkillRegistry()

    skill = registry.get(args.name)
    if skill is None:
        tui.print_error(f"Skill '{args.name}' not found in registry")
        return 1

    tui.print_skill_info(skill)
    return 0


def cmd_remove(args):
    """Uninstall a skill by name.

    Args:
        args: Parsed command-line arguments with 'name' attribute.
    """
    tui = TUI()
    registry = SkillRegistry()
    installer = SkillInstaller(registry)

    try:
        skill = installer.uninstall(args.name)
        tui.print_uninstall_progress(
            skill.name,
            success=True,
            message="Skill removed successfully",
        )
    except ValueError as e:
        tui.print_error(str(e))
        return 1
    except Exception as e:
        tui.print_error(f"Removal failed: {e}")
        return 1

    return 0


def cmd_validate(args):
    """Validate a skill file for security risks.

    Args:
        args: Parsed command-line arguments with 'path' attribute.
    """
    tui = TUI()
    validator = SkillValidator()

    try:
        result = validator.validate_file(args.path)
        tui.print_validation(result, target=args.path)
    except Exception as e:
        tui.print_error(f"Validation failed: {e}")
        return 1

    return 0


def cmd_export(args):
    """Export skill registry to a file.

    Args:
        args: Parsed command-line arguments with 'format' and 'output'
              attributes.
    """
    tui = TUI()
    registry = SkillRegistry()

    try:
        skills = registry.export_all()
        format_type = args.format.lower()

        if format_type == "json":
            output = args.output or "skillmatch_export.json"
            write_json_file(output, skills)
            tui.print_export_success("json", output)
        elif format_type == "yaml":
            output = args.output or "skillmatch_export.yaml"
            # Simple YAML-like output without PyYAML dependency
            lines = ["# SkillMatch Export", f"# Generated: {now_iso()}", ""]
            for skill_data in skills:
                lines.append(f"- name: {skill_data.get('name', 'unknown')}")
                lines.append(f"  version: \"{skill_data.get('version', '0.1.0')}\"")
                lines.append(f"  author: \"{skill_data.get('author', '')}\"")
                lines.append(f"  description: \"{skill_data.get('description', '')}\"")
                lines.append(f"  risk_level: {skill_data.get('risk_level', 'safe')}")
                lines.append(f"  source: {skill_data.get('source', 'local')}")
                lines.append(f"  installed: {str(skill_data.get('installed', False)).lower()}")
                if skill_data.get("tags"):
                    tags_str = ", ".join(skill_data["tags"])
                    lines.append(f"  tags: [{tags_str}]")
                if skill_data.get("capabilities"):
                    caps_str = ", ".join(skill_data["capabilities"])
                    lines.append(f"  capabilities: [{caps_str}]")
                if skill_data.get("framework_support"):
                    fws_str = ", ".join(skill_data["framework_support"])
                    lines.append(f"  framework_support: [{fws_str}]")
                lines.append("")
            with open(output, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            tui.print_export_success("yaml", output)
        else:
            tui.print_error(f"Unsupported format: {format_type}. Use 'json' or 'yaml'.")
            return 1

    except Exception as e:
        tui.print_error(f"Export failed: {e}")
        return 1

    return 0


def build_parser():
    """Build the argument parser with all subcommands.

    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="skillmatch",
        description=(
            "SkillMatch - AI Agent Skill Discovery, Matching & Orchestration Engine. "
            "Search, install, and manage AI agent skills intelligently."
        ),
        epilog="Use 'skillmatch <command> --help' for more information on a command.",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"SkillMatch v{__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init command
    sub_init = subparsers.add_parser(
        "init",
        help="Initialize SkillMatch configuration",
        description="Create configuration directory and initialize the skill registry.",
    )

    # search command
    sub_search = subparsers.add_parser(
        "search",
        help="Search for skills matching a query",
        description="Search the skill registry using natural language queries.",
    )
    sub_search.add_argument(
        "query",
        nargs="?",
        default="",
        help="Search query string (natural language)",
    )
    sub_search.add_argument(
        "--framework", "-f",
        default=None,
        help="Filter by framework name (e.g., claude, gpt4)",
    )
    sub_search.add_argument(
        "--tag", "-t",
        action="append",
        default=None,
        help="Filter by tag (can be specified multiple times)",
    )
    sub_search.add_argument(
        "--top", "-n",
        type=int,
        default=10,
        help="Number of results to return (default: 10)",
    )

    # install command
    sub_install = subparsers.add_parser(
        "install",
        help="Install a skill",
        description="Install a skill from the registry.",
    )
    sub_install.add_argument(
        "name",
        help="Name of the skill to install",
    )

    # list command
    sub_list = subparsers.add_parser(
        "list",
        help="List skills",
        description="List installed or all available skills.",
    )
    sub_list.add_argument(
        "--all", "-a",
        action="store_true",
        default=False,
        help="List all skills, not just installed ones",
    )

    # info command
    sub_info = subparsers.add_parser(
        "info",
        help="Show skill details",
        description="Display detailed information about a specific skill.",
    )
    sub_info.add_argument(
        "name",
        help="Name of the skill to inspect",
    )

    # remove command
    sub_remove = subparsers.add_parser(
        "remove",
        help="Uninstall a skill",
        description="Remove an installed skill.",
    )
    sub_remove.add_argument(
        "name",
        help="Name of the skill to remove",
    )

    # validate command
    sub_validate = subparsers.add_parser(
        "validate",
        help="Validate skill security",
        description="Check a skill file for security risks.",
    )
    sub_validate.add_argument(
        "path",
        help="Path to the skill file to validate",
    )

    # export command
    sub_export = subparsers.add_parser(
        "export",
        help="Export skill registry",
        description="Export the skill registry to a file.",
    )
    sub_export.add_argument(
        "--format", "-f",
        choices=["json", "yaml"],
        default="json",
        help="Export format (default: json)",
    )
    sub_export.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path (default: skillmatch_export.<format>)",
    )

    return parser


def main(argv=None):
    """Main entry point for the SkillMatch CLI.

    Parses command-line arguments and dispatches to the appropriate
    subcommand handler.

    Args:
        argv: Optional list of command-line arguments. Defaults to sys.argv[1:].

    Returns:
        int: Exit code (0 for success, non-zero for errors).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    # If no command is given, show help
    if not args.command:
        parser.print_help()
        return 0

    # Dispatch to command handler
    command_map = {
        "init": cmd_init,
        "search": cmd_search,
        "install": cmd_install,
        "list": cmd_list,
        "info": cmd_info,
        "remove": cmd_remove,
        "validate": cmd_validate,
        "export": cmd_export,
    }

    handler = command_map.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
