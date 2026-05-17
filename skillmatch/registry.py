"""Skill Registry Management for SkillMatch.

Manages the local skill registry stored as a JSON file. Supports CRUD
operations on skills and includes 20+ built-in skill definitions covering
code review, test generation, documentation, refactoring, security scanning,
and more.
"""

import os
import copy
import json

from skillmatch.models import Skill
from skillmatch.utils import (
    ensure_dir,
    read_json_file,
    write_json_file,
    get_registry_path,
    now_iso,
    is_github_url,
    fetch_url,
    parse_github_url,
)


def _builtin_skills():
    """Return the built-in skill definitions.

    Provides 20+ pre-configured skills covering common AI agent use cases
    including code review, testing, documentation, refactoring, security,
    and more.

    Returns:
        list: List of Skill objects representing built-in skills.
    """
    return [
        Skill(
            name="code-review",
            description=(
                "Automated code review agent that analyzes source code for "
                "bugs, style violations, performance issues, and best practice "
                "adherence. Supports multiple programming languages and can "
                "provide inline comments and summary reports."
            ),
            author="SkillMatch Core",
            version="1.2.0",
            tags=["code-quality", "review", "analysis", "best-practices"],
            capabilities=[
                "bug-detection",
                "style-checking",
                "performance-analysis",
                "security-review",
                "inline-comments",
                "summary-report",
            ],
            framework_support=["claude", "gpt4", "gemini", "codellama"],
            install_cmd="skillmatch install code-review",
            risk_level="safe",
            source="builtin",
        ),
        Skill(
            name="test-generation",
            description=(
                "Generate comprehensive unit tests and integration tests from "
                "existing source code. Analyzes code structure, identifies "
                "edge cases, and produces tests with proper assertions and "
                "mocking. Supports pytest, unittest, jest, and other frameworks."
            ),
            author="SkillMatch Core",
            version="1.1.0",
            tags=["testing", "unit-test", "integration-test", "coverage"],
            capabilities=[
                "unit-test-gen",
                "integration-test-gen",
                "edge-case-detection",
                "mock-generation",
                "coverage-analysis",
            ],
            framework_support=["claude", "gpt4", "gemini", "copilot"],
            install_cmd="skillmatch install test-generation",
            risk_level="safe",
            source="builtin",
        ),
        Skill(
            name="doc-writer",
            description=(
                "Automatically generate and maintain project documentation "
                "including API docs, README files, changelogs, and inline "
                "code comments. Follows documentation best practices and "
                "supports multiple output formats."
            ),
            author="SkillMatch Core",
            version="1.0.0",
            tags=["documentation", "api-docs", "readme", "comments"],
            capabilities=[
                "api-documentation",
                "readme-generation",
                "changelog-generation",
                "inline-comments",
                "docstring-generation",
            ],
            framework_support=["claude", "gpt4", "gemini"],
            install_cmd="skillmatch install doc-writer",
            risk_level="safe",
            source="builtin",
        ),
        Skill(
            name="refactor-agent",
            description=(
                "Intelligent code refactoring agent that suggests and applies "
                "code improvements including design pattern adoption, dead code "
                "removal, complexity reduction, and architectural improvements "
                "while preserving existing behavior."
            ),
            author="SkillMatch Core",
            version="1.0.0",
            tags=["refactoring", "code-quality", "design-patterns"],
            capabilities=[
                "pattern-suggestion",
                "dead-code-removal",
                "complexity-reduction",
                "rename-refactor",
                "extract-method",
            ],
            framework_support=["claude", "gpt4", "gemini", "codellama"],
            install_cmd="skillmatch install refactor-agent",
            risk_level="medium",
            source="builtin",
        ),
        Skill(
            name="security-scanner",
            description=(
                "Security vulnerability scanner that detects common security "
                "issues including SQL injection, XSS, CSRF, insecure deserialization, "
                "hardcoded secrets, and misconfigured permissions. Generates "
                "detailed security reports with severity ratings."
            ),
            author="SkillMatch Core",
            version="1.3.0",
            tags=["security", "vulnerability", "scanning", "owasp"],
            capabilities=[
                "sqli-detection",
                "xss-detection",
                "csrf-detection",
                "secret-detection",
                "dependency-audit",
                "severity-rating",
            ],
            framework_support=["claude", "gpt4", "gemini"],
            install_cmd="skillmatch install security-scanner",
            risk_level="low",
            source="builtin",
        ),
        Skill(
            name="api-designer",
            description=(
                "REST API and GraphQL schema design agent. Helps design clean, "
                "consistent APIs with proper error handling, pagination, "
                "authentication, and versioning. Generates OpenAPI specs and "
                "GraphQL schemas."
            ),
            author="SkillMatch Core",
            version="1.0.0",
            tags=["api", "rest", "graphql", "design"],
            capabilities=[
                "rest-api-design",
                "graphql-schema",
                "openapi-spec",
                "error-handling",
                "pagination-design",
            ],
            framework_support=["claude", "gpt4", "gemini"],
            install_cmd="skillmatch install api-designer",
            risk_level="safe",
            source="builtin",
        ),
        Skill(
            name="db-migration",
            description=(
                "Database schema migration assistant that generates migration "
                "scripts, analyzes schema changes for potential data loss, "
                "and provides rollback strategies. Supports PostgreSQL, MySQL, "
                "SQLite, and other databases."
            ),
            author="SkillMatch Core",
            version="1.0.0",
            tags=["database", "migration", "schema", "sql"],
            capabilities=[
                "migration-gen",
                "schema-analysis",
                "rollback-strategy",
                "data-loss-check",
                "index-optimization",
            ],
            framework_support=["claude", "gpt4", "gemini"],
            install_cmd="skillmatch install db-migration",
            risk_level="high",
            source="builtin",
        ),
        Skill(
            name="perf-analyzer",
            description=(
                "Performance analysis agent that identifies bottlenecks, "
                "memory leaks, and inefficient algorithms. Provides optimization "
                "suggestions with estimated impact and generates benchmarking "
                "code for validation."
            ),
            author="SkillMatch Core",
            version="1.1.0",
            tags=["performance", "optimization", "profiling", "benchmarking"],
            capabilities=[
                "bottleneck-detection",
                "memory-analysis",
                "algorithm-optimization",
                "benchmark-gen",
                "complexity-analysis",
            ],
            framework_support=["claude", "gpt4", "gemini"],
            install_cmd="skillmatch install perf-analyzer",
            risk_level="safe",
            source="builtin",
        ),
        Skill(
            name="git-workflow",
            description=(
                "Git workflow automation agent that helps with branch management, "
                "commit message generation, PR descriptions, merge conflict "
                "resolution suggestions, and release management."
            ),
            author="SkillMatch Core",
            version="1.0.0",
            tags=["git", "workflow", "version-control", "ci-cd"],
            capabilities=[
                "commit-gen",
                "pr-description",
                "branch-management",
                "conflict-resolution",
                "release-notes",
            ],
            framework_support=["claude", "gpt4", "gemini", "copilot"],
            install_cmd="skillmatch install git-workflow",
            risk_level="low",
            source="builtin",
        ),
        Skill(
            name="i18n-helper",
            description=(
                "Internationalization and localization helper that extracts "
                "hardcoded strings, generates translation files, manages locale "
                "data, and ensures proper Unicode handling across the project."
            ),
            author="SkillMatch Core",
            version="1.0.0",
            tags=["i18n", "localization", "translation", "unicode"],
            capabilities=[
                "string-extraction",
                "translation-file-gen",
                "locale-management",
                "unicode-check",
                "pluralization",
            ],
            framework_support=["claude", "gpt4", "gemini"],
            install_cmd="skillmatch install i18n-helper",
            risk_level="safe",
            source="builtin",
        ),
        Skill(
            name="logging-setup",
            description=(
                "Logging and observability setup agent that configures structured "
                "logging, sets up log rotation, integrates with monitoring systems, "
                "and establishes alerting rules for production environments."
            ),
            author="SkillMatch Core",
            version="1.0.0",
            tags=["logging", "monitoring", "observability", "alerting"],
            capabilities=[
                "structured-logging",
                "log-rotation",
                "monitoring-setup",
                "alerting-rules",
                "dashboard-gen",
            ],
            framework_support=["claude", "gpt4", "gemini"],
            install_cmd="skillmatch install logging-setup",
            risk_level="low",
            source="builtin",
        ),
        Skill(
            name="config-manager",
            description=(
                "Configuration management agent that handles environment-specific "
                "configs, secret management, feature flags, and configuration "
                "validation. Supports YAML, JSON, TOML, and .env formats."
            ),
            author="SkillMatch Core",
            version="1.0.0",
            tags=["config", "secrets", "feature-flags", "env"],
            capabilities=[
                "config-validation",
                "secret-management",
                "feature-flags",
                "env-management",
                "schema-validation",
            ],
            framework_support=["claude", "gpt4", "gemini"],
            install_cmd="skillmatch install config-manager",
            risk_level="medium",
            source="builtin",
        ),
        Skill(
            name="code-explainer",
            description=(
                "Code explanation agent that analyzes complex codebases and "
                "provides clear, contextual explanations of code logic, "
                "architecture decisions, and data flow. Useful for onboarding "
                "and knowledge transfer."
            ),
            author="SkillMatch Core",
            version="1.0.0",
            tags=["explanation", "documentation", "onboarding", "learning"],
            capabilities=[
                "code-explanation",
                "architecture-doc",
                "data-flow-analysis",
                "dependency-mapping",
                "knowledge-base",
            ],
            framework_support=["claude", "gpt4", "gemini", "copilot"],
            install_cmd="skillmatch install code-explainer",
            risk_level="safe",
            source="builtin",
        ),
        Skill(
            name="dependency-updater",
            description=(
                "Dependency management agent that checks for outdated packages, "
                "analyzes compatibility, generates update plans, and creates "
                "pull requests for dependency updates with changelog summaries."
            ),
            author="SkillMatch Core",
            version="1.0.0",
            tags=["dependencies", "updates", "packages", "maintenance"],
            capabilities=[
                "outdated-check",
                "compatibility-analysis",
                "update-plan",
                "changelog-summary",
                "breaking-change-detection",
            ],
            framework_support=["claude", "gpt4", "gemini"],
            install_cmd="skillmatch install dependency-updater",
            risk_level="medium",
            source="builtin",
        ),
        Skill(
            name="error-handler",
            description=(
                "Error handling and resilience patterns agent that implements "
                "proper error handling, retry logic, circuit breakers, and "
                "graceful degradation strategies across the codebase."
            ),
            author="SkillMatch Core",
            version="1.0.0",
            tags=["error-handling", "resilience", "retry", "fault-tolerance"],
            capabilities=[
                "error-handling-patterns",
                "retry-logic",
                "circuit-breaker",
                "graceful-degradation",
                "error-reporting",
            ],
            framework_support=["claude", "gpt4", "gemini"],
            install_cmd="skillmatch install error-handler",
            risk_level="safe",
            source="builtin",
        ),
        Skill(
            name="mock-generator",
            description=(
                "Mock data and service generator for development and testing. "
                "Creates realistic mock objects, fake API responses, test "
                "fixtures, and seed data based on schema definitions."
            ),
            author="SkillMatch Core",
            version="1.0.0",
            tags=["mocking", "testing", "fixtures", "fake-data"],
            capabilities=[
                "mock-object-gen",
                "fake-api-responses",
                "test-fixtures",
                "seed-data-gen",
                "schema-based-gen",
            ],
            framework_support=["claude", "gpt4", "gemini", "copilot"],
            install_cmd="skillmatch install mock-generator",
            risk_level="safe",
            source="builtin",
        ),
        Skill(
            name="ci-pipeline",
            description=(
                "CI/CD pipeline configuration agent that generates and optimizes "
                "build pipelines for GitHub Actions, GitLab CI, Jenkins, and "
                "other CI systems. Includes testing, linting, and deployment stages."
            ),
            author="SkillMatch Core",
            version="1.0.0",
            tags=["ci-cd", "pipeline", "automation", "deployment"],
            capabilities=[
                "pipeline-gen",
                "build-optimization",
                "test-integration",
                "deploy-config",
                "cache-strategy",
            ],
            framework_support=["claude", "gpt4", "gemini"],
            install_cmd="skillmatch install ci-pipeline",
            risk_level="medium",
            source="builtin",
        ),
        Skill(
            name="data-validator",
            description=(
                "Data validation and schema enforcement agent that generates "
                "validation logic, data sanitization code, and schema definitions "
                "for APIs and databases. Supports JSON Schema, Pydantic, and "
                "custom validation rules."
            ),
            author="SkillMatch Core",
            version="1.0.0",
            tags=["validation", "schema", "data-quality", "sanitization"],
            capabilities=[
                "schema-gen",
                "validation-logic",
                "data-sanitization",
                "type-checking",
                "constraint-gen",
            ],
            framework_support=["claude", "gpt4", "gemini"],
            install_cmd="skillmatch install data-validator",
            risk_level="safe",
            source="builtin",
        ),
        Skill(
            name="accessibility-checker",
            description=(
                "Web accessibility audit agent that checks for WCAG compliance, "
                "generates accessible markup, provides ARIA label suggestions, "
                "and ensures keyboard navigation and screen reader compatibility."
            ),
            author="SkillMatch Core",
            version="1.0.0",
            tags=["accessibility", "a11y", "wcag", "web"],
            capabilities=[
                "wcag-audit",
                "aria-suggestions",
                "keyboard-nav-check",
                "color-contrast",
                "screen-reader-test",
            ],
            framework_support=["claude", "gpt4", "gemini"],
            install_cmd="skillmatch install accessibility-checker",
            risk_level="safe",
            source="builtin",
        ),
        Skill(
            name="prompt-optimizer",
            description=(
                "AI prompt engineering and optimization agent that analyzes, "
                "improves, and tests prompts for better AI model performance. "
                "Includes prompt templates, chain-of-thought strategies, and "
                "evaluation frameworks."
            ),
            author="SkillMatch Core",
            version="1.1.0",
            tags=["prompt-engineering", "ai", "optimization", "llm"],
            capabilities=[
                "prompt-analysis",
                "prompt-improvement",
                "template-gen",
                "chain-of-thought",
                "evaluation-framework",
            ],
            framework_support=["claude", "gpt4", "gemini"],
            install_cmd="skillmatch install prompt-optimizer",
            risk_level="safe",
            source="builtin",
        ),
        Skill(
            name="code-formatter",
            description=(
                "Code formatting and style enforcement agent that applies "
                "consistent formatting rules, organizes imports, sorts "
                "code elements, and enforces project-specific style guides "
                "across multiple languages."
            ),
            author="SkillMatch Core",
            version="1.0.0",
            tags=["formatting", "style", "linting", "clean-code"],
            capabilities=[
                "auto-formatting",
                "import-sorting",
                "style-enforcement",
                "lint-rule-gen",
                "prettier-config",
            ],
            framework_support=["claude", "gpt4", "gemini", "copilot"],
            install_cmd="skillmatch install code-formatter",
            risk_level="low",
            source="builtin",
        ),
        Skill(
            name="microservice-scaffold",
            description=(
                "Microservice scaffolding agent that generates complete "
                "microservice projects with routing, middleware, database "
                "connections, health checks, and Docker configuration. "
                "Supports multiple frameworks and architectures."
            ),
            author="SkillMatch Core",
            version="1.0.0",
            tags=["microservice", "scaffolding", "architecture", "docker"],
            capabilities=[
                "project-scaffold",
                "docker-config",
                "middleware-setup",
                "health-checks",
                "api-routing",
            ],
            framework_support=["claude", "gpt4", "gemini"],
            install_cmd="skillmatch install microservice-scaffold",
            risk_level="medium",
            source="builtin",
        ),
    ]


class SkillRegistry:
    """Manages the local skill registry with CRUD operations.

    The registry is persisted as a JSON file at ~/.skillmatch/registry.json.
    Supports adding, removing, updating, and querying skills. Initializes
    with 20+ built-in skill definitions on first use.

    Attributes:
        registry_path: Path to the registry JSON file.
        skills: Dictionary mapping skill names to Skill objects.
    """

    def __init__(self, registry_path=None):
        """Initialize the skill registry.

        Args:
            registry_path: Optional custom path to the registry file.
                          Defaults to ~/.skillmatch/registry.json.
        """
        self.registry_path = registry_path or get_registry_path()
        self.skills = {}
        self._load()

    def _load(self):
        """Load the registry from disk, or initialize with built-in skills.

        Creates the registry directory and file if they do not exist.
        Populates with built-in skills on first initialization.
        """
        if os.path.exists(self.registry_path):
            try:
                data = read_json_file(self.registry_path)
                for name, skill_data in data.get("skills", {}).items():
                    self.skills[name] = Skill.from_dict(skill_data)
            except (json.JSONDecodeError, KeyError, TypeError):
                self._init_builtins()
        else:
            self._init_builtins()

    def _init_builtins(self):
        """Initialize the registry with built-in skill definitions."""
        timestamp = now_iso()
        for skill in _builtin_skills():
            skill.created_at = timestamp
            skill.updated_at = timestamp
            self.skills[skill.name] = skill
        self.save()

    def save(self):
        """Persist the current registry state to disk.

        Creates the parent directory if it does not exist.
        """
        data = {
            "version": "1.0",
            "skills": {
                name: skill.to_dict() for name, skill in self.skills.items()
            },
        }
        write_json_file(self.registry_path, data)

    def add(self, skill):
        """Add a new skill to the registry.

        Args:
            skill: Skill object to add.

        Raises:
            ValueError: If a skill with the same name already exists.
        """
        if skill.name in self.skills:
            raise ValueError(f"Skill '{skill.name}' already exists in registry")
        timestamp = now_iso()
        skill.created_at = timestamp
        skill.updated_at = timestamp
        self.skills[skill.name] = skill
        self.save()

    def update(self, name, **kwargs):
        """Update an existing skill's attributes.

        Args:
            name: Name of the skill to update.
            **kwargs: Attribute key-value pairs to update.

        Returns:
            Skill: The updated Skill object.

        Raises:
            KeyError: If the skill name is not found.
        """
        if name not in self.skills:
            raise KeyError(f"Skill '{name}' not found in registry")
        skill = self.skills[name]
        for key, value in kwargs.items():
            if hasattr(skill, key):
                setattr(skill, key, value)
        skill.updated_at = now_iso()
        self.save()
        return skill

    def remove(self, name):
        """Remove a skill from the registry.

        Args:
            name: Name of the skill to remove.

        Returns:
            Skill: The removed Skill object.

        Raises:
            KeyError: If the skill name is not found.
        """
        if name not in self.skills:
            raise KeyError(f"Skill '{name}' not found in registry")
        skill = self.skills.pop(name)
        self.save()
        return skill

    def get(self, name):
        """Retrieve a skill by name.

        Args:
            name: Name of the skill to retrieve.

        Returns:
            Skill or None: The Skill object, or None if not found.
        """
        return self.skills.get(name)

    def search_by_tag(self, tag):
        """Find all skills that have a specific tag.

        Args:
            tag: Tag string to search for.

        Returns:
            list: List of Skill objects matching the tag.
        """
        return [
            s for s in self.skills.values() if tag.lower() in [t.lower() for t in s.tags]
        ]

    def search_by_capability(self, capability):
        """Find all skills that have a specific capability.

        Args:
            capability: Capability string to search for.

        Returns:
            list: List of Skill objects matching the capability.
        """
        return [
            s
            for s in self.skills.values()
            if capability.lower() in [c.lower() for c in s.capabilities]
        ]

    def search_by_framework(self, framework):
        """Find all skills that support a specific framework.

        Args:
            framework: Framework name to filter by.

        Returns:
            list: List of Skill objects supporting the framework.
        """
        return [
            s
            for s in self.skills.values()
            if framework.lower() in [f.lower() for f in s.framework_support]
        ]

    def list_all(self, installed_only=False):
        """List all skills in the registry.

        Args:
            installed_only: If True, only return installed skills.

        Returns:
            list: List of all (or installed) Skill objects.
        """
        skills = list(self.skills.values())
        if installed_only:
            skills = [s for s in skills if s.installed]
        return skills

    def list_installed(self):
        """List all installed skills.

        Returns:
            list: List of installed Skill objects.
        """
        return self.list_all(installed_only=True)

    def mark_installed(self, name, install_path=""):
        """Mark a skill as installed.

        Args:
            name: Name of the skill to mark as installed.
            install_path: Filesystem path where the skill is installed.

        Raises:
            KeyError: If the skill name is not found.
        """
        self.update(name, installed=True, install_path=install_path)

    def mark_uninstalled(self, name):
        """Mark a skill as uninstalled.

        Args:
            name: Name of the skill to mark as uninstalled.

        Raises:
            KeyError: If the skill name is not found.
        """
        self.update(name, installed=False, install_path="")

    def import_from_github(self, url):
        """Import a skill definition from a GitHub repository.

        Attempts to fetch a skillmatch.json or skill.json file from the
        repository root.

        Args:
            url: GitHub repository URL.

        Returns:
            Skill: The imported Skill object.

        Raises:
            ValueError: If the URL is not a valid GitHub URL.
            Exception: If fetching or parsing the skill definition fails.
        """
        if not is_github_url(url):
            raise ValueError(f"Invalid GitHub URL: {url}")

        owner, repo = parse_github_url(url)
        raw_url = (
            f"https://raw.githubusercontent.com/{owner}/{repo}/main/skillmatch.json"
        )

        try:
            content = fetch_url(raw_url)
            skill_data = json.loads(content)
            skill = Skill.from_dict(skill_data)
            skill.source = "github"
            self.add(skill)
            return skill
        except Exception:
            # Try master branch as fallback
            raw_url = (
                f"https://raw.githubusercontent.com/{owner}/{repo}/master/skillmatch.json"
            )
            content = fetch_url(raw_url)
            skill_data = json.loads(content)
            skill = Skill.from_dict(skill_data)
            skill.source = "github"
            self.add(skill)
            return skill

    def export_all(self):
        """Export all skills as a list of dictionaries.

        Returns:
            list: List of skill dictionaries.
        """
        return [skill.to_dict() for skill in self.skills.values()]

    def count(self):
        """Return the total number of skills in the registry.

        Returns:
            int: Number of skills.
        """
        return len(self.skills)

    def __len__(self):
        """Return the number of skills in the registry.

        Returns:
            int: Number of skills.
        """
        return len(self.skills)

    def __contains__(self, name):
        """Check if a skill exists in the registry.

        Args:
            name: Skill name to check.

        Returns:
            bool: True if the skill exists.
        """
        return name in self.skills

    def __iter__(self):
        """Iterate over all skills in the registry.

        Yields:
            Skill: Each skill in the registry.
        """
        return iter(self.skills.values())
