"""Skill Index Builder and Search for SkillMatch.

Implements an inverted index for fast full-text search over skills,
along with exact matching support for tags and capabilities. The index
can be persisted to and loaded from a local JSON file.
"""

import os
import json
from collections import defaultdict

from skillmatch.models import Skill, SearchResult
from skillmatch.utils import (
    tokenize,
    normalize_text,
    read_json_file,
    write_json_file,
    get_index_path,
    ensure_dir,
)


class SkillIndexer:
    """Builds and manages an inverted index for skill search.

    Supports full-text search across skill names and descriptions,
    as well as exact matching for tags, capabilities, and framework
    support. The index can be persisted to disk for fast loading.

    Attributes:
        index_path: Path to the persisted index file.
        inverted_index: Dict mapping terms to sets of skill names.
        tag_index: Dict mapping tags to sets of skill names.
        capability_index: Dict mapping capabilities to sets of skill names.
        framework_index: Dict mapping frameworks to sets of skill names.
        skills: Dict mapping skill names to Skill objects.
    """

    def __init__(self, index_path=None):
        """Initialize the skill indexer.

        Args:
            index_path: Optional custom path for the index file.
                        Defaults to ~/.skillmatch/index.json.
        """
        self.index_path = index_path or get_index_path()
        self.inverted_index = defaultdict(set)
        self.tag_index = defaultdict(set)
        self.capability_index = defaultdict(set)
        self.framework_index = defaultdict(set)
        self.skills = {}

    def build(self, skills):
        """Build the inverted index from a list of skills.

        Indexes skill names, descriptions, tags, capabilities, and
        framework support for fast retrieval.

        Args:
            skills: Iterable of Skill objects to index.
        """
        self.inverted_index = defaultdict(set)
        self.tag_index = defaultdict(set)
        self.capability_index = defaultdict(set)
        self.framework_index = defaultdict(set)
        self.skills = {}

        for skill in skills:
            self.skills[skill.name] = skill

            # Index name tokens
            name_tokens = tokenize(skill.name)
            for token in name_tokens:
                self.inverted_index[token].add(skill.name)

            # Index description tokens
            desc_tokens = tokenize(skill.description)
            for token in desc_tokens:
                self.inverted_index[token].add(skill.name)

            # Index tags (exact and tokenized)
            for tag in skill.tags:
                tag_lower = tag.lower()
                self.tag_index[tag_lower].add(skill.name)
                for token in tokenize(tag):
                    self.inverted_index[token].add(skill.name)

            # Index capabilities (exact and tokenized)
            for cap in skill.capabilities:
                cap_lower = cap.lower()
                self.capability_index[cap_lower].add(skill.name)
                for token in tokenize(cap):
                    self.inverted_index[token].add(skill.name)

            # Index framework support (exact)
            for fw in skill.framework_support:
                fw_lower = fw.lower()
                self.framework_index[fw_lower].add(skill.name)

    def search(self, query, top_k=10):
        """Full-text search across indexed skills.

        Searches the inverted index for skills matching the query terms.
        Results are ranked by the number of matching terms.

        Args:
            query: Search query string.
            top_k: Maximum number of results to return.

        Returns:
            list: List of SearchResult objects sorted by relevance.
        """
        query_tokens = tokenize(query)

        if not query_tokens:
            return []

        # Count matching terms per skill
        match_counts = defaultdict(int)
        for token in query_tokens:
            token_lower = token.lower()
            if token_lower in self.inverted_index:
                for skill_name in self.inverted_index[token_lower]:
                    match_counts[skill_name] += 1

        # Also check for exact query match in name
        query_lower = query.lower().strip()
        for skill_name in self.skills:
            if query_lower in skill_name.lower():
                match_counts[skill_name] += 3  # Boost exact name matches

        # Build results
        max_count = max(match_counts.values()) if match_counts else 1
        results = []
        for skill_name, count in match_counts.items():
            skill = self.skills.get(skill_name)
            if skill:
                score = count / max_count
                results.append(
                    SearchResult(
                        skill=skill,
                        score=score,
                        matched_fields=["fulltext"],
                    )
                )

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def search_by_tag(self, tag, top_k=10):
        """Search for skills by exact tag match.

        Args:
            tag: Tag string to search for.
            top_k: Maximum number of results.

        Returns:
            list: List of SearchResult objects.
        """
        tag_lower = tag.lower()
        skill_names = self.tag_index.get(tag_lower, set())
        results = []
        for name in skill_names:
            skill = self.skills.get(name)
            if skill:
                results.append(
                    SearchResult(
                        skill=skill,
                        score=1.0,
                        matched_fields=["tags"],
                    )
                )
        return results[:top_k]

    def search_by_capability(self, capability, top_k=10):
        """Search for skills by exact capability match.

        Args:
            capability: Capability string to search for.
            top_k: Maximum number of results.

        Returns:
            list: List of SearchResult objects.
        """
        cap_lower = capability.lower()
        skill_names = self.capability_index.get(cap_lower, set())
        results = []
        for name in skill_names:
            skill = self.skills.get(name)
            if skill:
                results.append(
                    SearchResult(
                        skill=skill,
                        score=1.0,
                        matched_fields=["capabilities"],
                    )
                )
        return results[:top_k]

    def search_by_framework(self, framework, top_k=10):
        """Search for skills by framework support.

        Args:
            framework: Framework name to filter by.
            top_k: Maximum number of results.

        Returns:
            list: List of SearchResult objects.
        """
        fw_lower = framework.lower()
        skill_names = self.framework_index.get(fw_lower, set())
        results = []
        for name in skill_names:
            skill = self.skills.get(name)
            if skill:
                results.append(
                    SearchResult(
                        skill=skill,
                        score=1.0,
                        matched_fields=["framework_support"],
                    )
                )
        return results[:top_k]

    def save(self, index_path=None):
        """Persist the index to a JSON file.

        Args:
            index_path: Optional custom path. Defaults to self.index_path.
        """
        path = index_path or self.index_path
        data = {
            "inverted_index": {
                k: list(v) for k, v in self.inverted_index.items()
            },
            "tag_index": {
                k: list(v) for k, v in self.tag_index.items()
            },
            "capability_index": {
                k: list(v) for k, v in self.capability_index.items()
            },
            "framework_index": {
                k: list(v) for k, v in self.framework_index.items()
            },
            "skills": {
                name: skill.to_dict() for name, skill in self.skills.items()
            },
        }
        write_json_file(path, data)

    def load(self, index_path=None):
        """Load the index from a JSON file.

        Args:
            index_path: Optional custom path. Defaults to self.index_path.

        Returns:
            bool: True if loading was successful, False otherwise.
        """
        path = index_path or self.index_path
        if not os.path.exists(path):
            return False

        try:
            data = read_json_file(path)

            self.inverted_index = defaultdict(set)
            for k, v in data.get("inverted_index", {}).items():
                self.inverted_index[k] = set(v)

            self.tag_index = defaultdict(set)
            for k, v in data.get("tag_index", {}).items():
                self.tag_index[k] = set(v)

            self.capability_index = defaultdict(set)
            for k, v in data.get("capability_index", {}).items():
                self.capability_index[k] = set(v)

            self.framework_index = defaultdict(set)
            for k, v in data.get("framework_index", {}).items():
                self.framework_index[k] = set(v)

            self.skills = {}
            for name, skill_data in data.get("skills", {}).items():
                self.skills[name] = Skill.from_dict(skill_data)

            return True
        except (json.JSONDecodeError, KeyError, TypeError):
            return False

    def stats(self):
        """Return statistics about the index.

        Returns:
            dict: Dictionary with index statistics.
        """
        return {
            "total_skills": len(self.skills),
            "unique_terms": len(self.inverted_index),
            "unique_tags": len(self.tag_index),
            "unique_capabilities": len(self.capability_index),
            "unique_frameworks": len(self.framework_index),
        }
