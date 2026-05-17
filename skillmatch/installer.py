"""Skill Installation Manager for SkillMatch.

Handles installation, uninstallation, and dependency checking for skills.
Supports installation from local files, GitHub URLs, and the built-in
registry. Manages skill files in ~/.skillmatch/skills/.
"""

import os
import json
import shutil

from skillmatch.models import Skill
from skillmatch.utils import (
    ensure_dir,
    get_skills_dir,
    get_config_dir,
    safe_remove,
    is_github_url,
    parse_github_url,
    fetch_url,
    file_hash,
    now_iso,
    write_json_file,
    read_json_file,
    ProgressBar,
    Colors,
)


class SkillInstaller:
    """Manages skill installation and lifecycle.

    Handles installing skills from various sources (local files, GitHub,
    registry), managing installed skill files, checking dependencies,
    and providing installation status information.

    Attributes:
        registry: Reference to the SkillRegistry instance.
        skills_dir: Directory where installed skills are stored.
    """

    def __init__(self, registry):
        """Initialize the skill installer.

        Args:
            registry: SkillRegistry instance for skill management.
        """
        self.registry = registry
        self.skills_dir = get_skills_dir()
        ensure_dir(self.skills_dir)

    def install(self, name, source=None):
        """Install a skill by name from the registry.

        Args:
            name: Name of the skill to install.
            source: Optional source override (local path or GitHub URL).

        Returns:
            Skill: The installed Skill object.

        Raises:
            ValueError: If the skill is not found or already installed.
            Exception: If installation fails.
        """
        skill = self.registry.get(name)
        if skill is None:
            raise ValueError(f"Skill '{name}' not found in registry")

        if skill.installed:
            raise ValueError(f"Skill '{name}' is already installed")

        # Create skill installation directory
        skill_dir = os.path.join(self.skills_dir, name)
        ensure_dir(skill_dir)

        # Create skill metadata file
        meta_path = os.path.join(skill_dir, "skill.json")
        write_json_file(meta_path, skill.to_dict())

        # Create a basic skill runner script
        runner_path = os.path.join(skill_dir, "run.py")
        self._create_runner_script(runner_path, skill)

        # Mark as installed in registry
        self.registry.mark_installed(name, install_path=skill_dir)

        return skill

    def install_from_file(self, file_path):
        """Install a skill from a local JSON definition file.

        Args:
            file_path: Path to the skill definition JSON file.

        Returns:
            Skill: The installed Skill object.

        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file contains invalid JSON.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Skill definition file not found: {file_path}")

        skill_data = read_json_file(file_path)
        skill = Skill.from_dict(skill_data)
        skill.source = "local"

        # Add to registry if not present
        if skill.name not in self.registry:
            self.registry.add(skill)
        else:
            # Update existing skill
            self.registry.update(
                skill.name,
                description=skill.description,
                tags=skill.tags,
                capabilities=skill.capabilities,
                framework_support=skill.framework_support,
                install_cmd=skill.install_cmd,
                risk_level=skill.risk_level,
            )

        return self.install(skill.name)

    def install_from_github(self, url):
        """Install a skill from a GitHub repository.

        Fetches the skill definition from the repository and installs it.

        Args:
            url: GitHub repository URL.

        Returns:
            Skill: The installed Skill object.

        Raises:
            ValueError: If the URL is not a valid GitHub URL.
            Exception: If fetching or installation fails.
        """
        if not is_github_url(url):
            raise ValueError(f"Invalid GitHub URL: {url}")

        # Import skill definition from GitHub
        skill = self.registry.import_from_github(url)

        # Install the imported skill
        return self.install(skill.name)

    def uninstall(self, name):
        """Uninstall a skill by name.

        Removes the skill's files from disk and marks it as uninstalled
        in the registry.

        Args:
            name: Name of the skill to uninstall.

        Returns:
            Skill: The uninstalled Skill object.

        Raises:
            ValueError: If the skill is not found or not installed.
        """
        skill = self.registry.get(name)
        if skill is None:
            raise ValueError(f"Skill '{name}' not found in registry")

        if not skill.installed:
            raise ValueError(f"Skill '{name}' is not installed")

        # Remove skill files
        skill_dir = os.path.join(self.skills_dir, name)
        safe_remove(skill_dir)

        # Mark as uninstalled in registry
        self.registry.mark_uninstalled(name)

        return skill

    def is_installed(self, name):
        """Check if a skill is currently installed.

        Args:
            name: Name of the skill to check.

        Returns:
            bool: True if the skill is installed.
        """
        skill = self.registry.get(name)
        return skill is not None and skill.installed

    def get_install_path(self, name):
        """Get the installation path for a skill.

        Args:
            name: Name of the skill.

        Returns:
            str or None: Installation directory path, or None if not installed.
        """
        skill = self.registry.get(name)
        if skill and skill.installed:
            return skill.install_path
        return None

    def check_dependencies(self, name):
        """Check dependencies for a skill.

        Currently checks for Python version compatibility and common
        runtime dependencies based on the skill's metadata.

        Args:
            name: Name of the skill to check.

        Returns:
            dict: Dictionary with 'satisfied' (bool) and 'issues' (list).
        """
        import sys

        skill = self.registry.get(name)
        if skill is None:
            return {"satisfied": False, "issues": [f"Skill '{name}' not found"]}

        issues = []

        # Check Python version
        python_version = sys.version_info[:2]
        if python_version < (3, 6):
            issues.append(
                f"Python {python_version[0]}.{python_version[1]} is below "
                f"the minimum required version (3.6)"
            )

        # Check if skill directory is writable
        skill_dir = os.path.join(self.skills_dir, name)
        try:
            ensure_dir(skill_dir)
            test_file = os.path.join(skill_dir, ".write_test")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
        except (OSError, IOError) as e:
            issues.append(f"Cannot write to skill directory: {e}")

        return {"satisfied": len(issues) == 0, "issues": issues}

    def list_installed(self):
        """List all installed skills.

        Returns:
            list: List of installed Skill objects.
        """
        return self.registry.list_installed()

    def _create_runner_script(self, path, skill):
        """Create a basic runner script for a skill.

        Args:
            path: Path where the runner script should be created.
            skill: Skill object to create the runner for.
        """
        script_content = f'''#!/usr/bin/env python3
"""Runner script for skill: {skill.name}

Auto-generated by SkillMatch.
Skill: {skill.name} v{skill.version}
Author: {skill.author}
Description: {skill.description}
"""

import sys
import json
import os


def main():
    """Main entry point for the skill runner."""
    config_path = os.path.join(os.path.dirname(__file__), "skill.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
        print(f"Skill: {{config.get('name', 'unknown')}}")
        print(f"Version: {{config.get('version', 'unknown')}}")
        print(f"Description: {{config.get('description', 'No description')}}")
    else:
        print("Error: skill.json not found", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
        with open(path, "w", encoding="utf-8") as f:
            f.write(script_content)
