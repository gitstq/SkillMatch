"""Tests for the Skill Indexer.

Tests cover index building, full-text search, tag/capability/framework
search, index persistence, and statistics.
"""

import unittest
import tempfile
import os

from skillmatch.models import Skill
from skillmatch.indexer import SkillIndexer


class TestSkillIndexer(unittest.TestCase):
    """Test cases for the SkillIndexer class."""

    def setUp(self):
        """Set up test fixtures with sample skills."""
        self.temp_dir = tempfile.mkdtemp()
        self.index_path = os.path.join(self.temp_dir, "index.json")
        self.indexer = SkillIndexer(index_path=self.index_path)

        self.skills = [
            Skill(
                name="code-review",
                description="Automated code review tool for static analysis",
                tags=["code-quality", "review"],
                capabilities=["bug-detection", "style-checking"],
                framework_support=["claude", "gpt4"],
            ),
            Skill(
                name="test-gen",
                description="Unit test generation from source code",
                tags=["testing", "unit-test"],
                capabilities=["unit-test-gen", "mock-generation"],
                framework_support=["claude", "gemini"],
            ),
            Skill(
                name="security-scan",
                description="Security vulnerability scanner for web apps",
                tags=["security", "vulnerability"],
                capabilities=["sqli-detection", "xss-detection"],
                framework_support=["claude", "gpt4", "gemini"],
            ),
            Skill(
                name="doc-writer",
                description="Documentation generator for API and README",
                tags=["documentation", "api-docs"],
                capabilities=["api-documentation", "readme-generation"],
                framework_support=["claude"],
            ),
        ]

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_build_index(self):
        """Test that building the index creates all index types."""
        self.indexer.build(self.skills)
        self.assertGreater(len(self.indexer.inverted_index), 0)
        self.assertGreater(len(self.indexer.tag_index), 0)
        self.assertGreater(len(self.indexer.capability_index), 0)
        self.assertGreater(len(self.indexer.framework_index), 0)
        self.assertEqual(len(self.indexer.skills), len(self.skills))

    def test_build_empty(self):
        """Test building index with empty skill list."""
        self.indexer.build([])
        self.assertEqual(len(self.indexer.skills), 0)
        self.assertEqual(len(self.indexer.inverted_index), 0)

    def test_search_fulltext(self):
        """Test full-text search."""
        self.indexer.build(self.skills)
        results = self.indexer.search("code review")
        self.assertGreater(len(results), 0)
        # First result should be code-review
        self.assertEqual(results[0].skill.name, "code-review")

    def test_search_empty_query(self):
        """Test search with empty query returns empty."""
        self.indexer.build(self.skills)
        results = self.indexer.search("")
        self.assertEqual(len(results), 0)

    def test_search_top_k(self):
        """Test that top_k limits results."""
        self.indexer.build(self.skills)
        results = self.indexer.search("tool", top_k=2)
        self.assertLessEqual(len(results), 2)

    def test_search_by_tag(self):
        """Test search by tag."""
        self.indexer.build(self.skills)
        results = self.indexer.search_by_tag("security")
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertEqual(r.skill.name, "security-scan")

    def test_search_by_tag_case_insensitive(self):
        """Test tag search is case insensitive."""
        self.indexer.build(self.skills)
        results = self.indexer.search_by_tag("Security")
        self.assertGreater(len(results), 0)

    def test_search_by_nonexistent_tag(self):
        """Test search by nonexistent tag returns empty."""
        self.indexer.build(self.skills)
        results = self.indexer.search_by_tag("nonexistent")
        self.assertEqual(len(results), 0)

    def test_search_by_capability(self):
        """Test search by capability."""
        self.indexer.build(self.skills)
        results = self.indexer.search_by_capability("bug-detection")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].skill.name, "code-review")

    def test_search_by_framework(self):
        """Test search by framework."""
        self.indexer.build(self.skills)
        results = self.indexer.search_by_framework("claude")
        self.assertEqual(len(results), 4)  # All skills support claude

    def test_search_by_framework_partial(self):
        """Test search by framework that only some skills support."""
        self.indexer.build(self.skills)
        results = self.indexer.search_by_framework("gemini")
        self.assertEqual(len(results), 2)  # test-gen, security-scan

    def test_save_and_load(self):
        """Test index persistence save and load."""
        self.indexer.build(self.skills)
        self.indexer.save()

        # Create new indexer and load
        new_indexer = SkillIndexer(index_path=self.index_path)
        loaded = new_indexer.load()
        self.assertTrue(loaded)
        self.assertEqual(len(new_indexer.skills), len(self.skills))
        self.assertEqual(len(new_indexer.inverted_index), len(self.indexer.inverted_index))

    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file returns False."""
        new_indexer = SkillIndexer(index_path="/nonexistent/index.json")
        loaded = new_indexer.load()
        self.assertFalse(loaded)

    def test_stats(self):
        """Test index statistics."""
        self.indexer.build(self.skills)
        stats = self.indexer.stats()
        self.assertEqual(stats["total_skills"], 4)
        self.assertGreater(stats["unique_terms"], 0)
        self.assertGreater(stats["unique_tags"], 0)
        self.assertGreater(stats["unique_capabilities"], 0)
        self.assertGreater(stats["unique_frameworks"], 0)

    def test_name_boost_in_search(self):
        """Test that exact name matches are boosted."""
        self.indexer.build(self.skills)
        results = self.indexer.search("code-review")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].skill.name, "code-review")
        self.assertGreater(results[0].score, 0)


if __name__ == "__main__":
    unittest.main()
