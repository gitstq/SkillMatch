"""Data model definitions for SkillMatch.

Defines the core data structures used throughout the application including
Skill, SearchResult, and ValidationResult. Uses plain Python classes for
maximum compatibility (no dataclasses dependency on Python 3.6).
"""

import json
import copy


class Skill:
    """Represents an AI agent skill with metadata and capabilities.

    Attributes:
        name: Unique identifier for the skill.
        description: Human-readable description of what the skill does.
        author: Creator or maintainer of the skill.
        version: Semantic version string (e.g., "1.0.0").
        tags: List of category tags for classification.
        capabilities: List of specific capabilities the skill provides.
        framework_support: List of AI frameworks this skill supports.
        install_cmd: Command or instructions to install the skill.
        risk_level: Risk assessment level (safe, low, medium, high).
        source: Origin of the skill definition (local, github, builtin).
        installed: Whether the skill is currently installed.
        install_path: Filesystem path where the skill is installed.
        created_at: ISO format timestamp of creation.
        updated_at: ISO format timestamp of last update.
    """

    def __init__(
        self,
        name="",
        description="",
        author="",
        version="0.1.0",
        tags=None,
        capabilities=None,
        framework_support=None,
        install_cmd="",
        risk_level="safe",
        source="local",
        installed=False,
        install_path="",
        created_at="",
        updated_at="",
    ):
        """Initialize a Skill instance.

        Args:
            name: Unique skill name/identifier.
            description: Detailed description of the skill.
            author: Author or maintainer name.
            version: Version string following semantic versioning.
            tags: List of string tags for categorization.
            capabilities: List of capability strings.
            framework_support: List of supported framework names.
            install_cmd: Installation command or instructions.
            risk_level: One of 'safe', 'low', 'medium', 'high'.
            source: Origin source ('local', 'github', 'builtin').
            installed: Boolean indicating installation status.
            install_path: Path where skill files are installed.
            created_at: Creation timestamp (ISO format).
            updated_at: Last update timestamp (ISO format).
        """
        self.name = name
        self.description = description
        self.author = author
        self.version = version
        self.tags = tags if tags is not None else []
        self.capabilities = capabilities if capabilities is not None else []
        self.framework_support = (
            framework_support if framework_support is not None else []
        )
        self.install_cmd = install_cmd
        self.risk_level = risk_level
        self.source = source
        self.installed = installed
        self.install_path = install_path
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        """Serialize the skill to a dictionary.

        Returns:
            dict: Dictionary representation of the skill.
        """
        return {
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "version": self.version,
            "tags": list(self.tags),
            "capabilities": list(self.capabilities),
            "framework_support": list(self.framework_support),
            "install_cmd": self.install_cmd,
            "risk_level": self.risk_level,
            "source": self.source,
            "installed": self.installed,
            "install_path": self.install_path,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize a skill from a dictionary.

        Args:
            data: Dictionary containing skill data.

        Returns:
            Skill: A new Skill instance populated from the dictionary.
        """
        skill = cls()
        for key, value in data.items():
            if hasattr(skill, key):
                setattr(skill, key, value)
        return skill

    def to_json(self):
        """Serialize the skill to a JSON string.

        Returns:
            str: JSON representation of the skill.
        """
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str):
        """Deserialize a skill from a JSON string.

        Args:
            json_str: JSON string containing skill data.

        Returns:
            Skill: A new Skill instance populated from the JSON.
        """
        return cls.from_dict(json.loads(json_str))

    def copy(self):
        """Create a deep copy of this skill.

        Returns:
            Skill: A deep copy of the skill.
        """
        return copy.deepcopy(self)

    def __repr__(self):
        """Return a string representation of the skill.

        Returns:
            str: String representation including name and version.
        """
        return f"Skill(name={self.name!r}, version={self.version!r})"

    def __eq__(self, other):
        """Check equality based on name and version.

        Args:
            other: Another object to compare against.

        Returns:
            bool: True if the other object is a Skill with the same name.
        """
        if not isinstance(other, Skill):
            return False
        return self.name == other.name

    def __hash__(self):
        """Return hash based on skill name.

        Returns:
            int: Hash value for the skill.
        """
        return hash(self.name)


class SearchResult:
    """Represents a skill search result with relevance scoring.

    Attributes:
        skill: The matched Skill instance.
        score: Relevance score (higher is more relevant).
        matched_fields: List of fields that contributed to the match.
    """

    def __init__(self, skill=None, score=0.0, matched_fields=None):
        """Initialize a SearchResult instance.

        Args:
            skill: The matched Skill object.
            score: Float relevance score.
            matched_fields: List of field names that matched.
        """
        self.skill = skill
        self.score = score
        self.matched_fields = matched_fields if matched_fields is not None else []

    def to_dict(self):
        """Serialize the search result to a dictionary.

        Returns:
            dict: Dictionary representation of the search result.
        """
        return {
            "skill": self.skill.to_dict() if self.skill else None,
            "score": self.score,
            "matched_fields": list(self.matched_fields),
        }

    def __repr__(self):
        """Return string representation of the search result.

        Returns:
            str: String including skill name and score.
        """
        skill_name = self.skill.name if self.skill else "None"
        return f"SearchResult(skill={skill_name!r}, score={self.score:.4f})"

    def __lt__(self, other):
        """Enable sorting by score (descending).

        Args:
            other: Another SearchResult to compare against.

        Returns:
            bool: True if this result has a lower score than the other.
        """
        return self.score < other.score


class ValidationResult:
    """Represents the result of a skill security validation.

    Attributes:
        risk_level: Assessed risk level (safe, low, medium, high).
        warnings: List of warning messages about potential risks.
        suggestions: List of suggestions for risk mitigation.
        details: Additional validation details.
    """

    RISK_LEVELS = ("safe", "low", "medium", "high")

    def __init__(
        self,
        risk_level="safe",
        warnings=None,
        suggestions=None,
        details=None,
    ):
        """Initialize a ValidationResult instance.

        Args:
            risk_level: One of 'safe', 'low', 'medium', 'high'.
            warnings: List of warning strings.
            suggestions: List of suggestion strings.
            details: Dictionary of additional details.
        """
        if risk_level not in self.RISK_LEVELS:
            raise ValueError(
                f"Invalid risk_level '{risk_level}'. "
                f"Must be one of {self.RISK_LEVELS}"
            )
        self.risk_level = risk_level
        self.warnings = warnings if warnings is not None else []
        self.suggestions = suggestions if suggestions is not None else []
        self.details = details if details is not None else {}

    def to_dict(self):
        """Serialize the validation result to a dictionary.

        Returns:
            dict: Dictionary representation of the validation result.
        """
        return {
            "risk_level": self.risk_level,
            "warnings": list(self.warnings),
            "suggestions": list(self.suggestions),
            "details": dict(self.details),
        }

    def is_safe(self):
        """Check if the validation result indicates the skill is safe.

        Returns:
            bool: True if risk_level is 'safe' or 'low'.
        """
        return self.risk_level in ("safe", "low")

    def __repr__(self):
        """Return string representation of the validation result.

        Returns:
            str: String including risk level and warning count.
        """
        return (
            f"ValidationResult(risk_level={self.risk_level!r}, "
            f"warnings={len(self.warnings)})"
        )
