"""SkillMatch - AI Agent Skill Discovery, Matching and Orchestration Engine.

A lightweight CLI tool for intelligently discovering, matching, and managing
AI agent skills. Built with zero external dependencies using only Python
standard library.
"""

__version__ = "1.0.0"
__author__ = "SkillMatch Team"

from skillmatch.models import Skill, SearchResult, ValidationResult
from skillmatch.registry import SkillRegistry
from skillmatch.matcher import SkillMatcher
from skillmatch.indexer import SkillIndexer
from skillmatch.validator import SkillValidator
from skillmatch.installer import SkillInstaller

__all__ = [
    "Skill",
    "SearchResult",
    "ValidationResult",
    "SkillRegistry",
    "SkillMatcher",
    "SkillIndexer",
    "SkillValidator",
    "SkillInstaller",
]
