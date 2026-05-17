"""Tests for the Skill Registry.

Tests cover CRUD operations, search by tag/capability/framework,
import from GitHub, export, and persistence.
"""

import unittest
import tempfile
import os
import json

from skillmatch.models import Skill
from skillmatch.registry import SkillRegistry


class TestSkillRegistry(unittest.TestCase):
    """Test cases for the SkillRegistry class."""

    def setUp(self):
        """Set up test fixtures with a temporary registry."""
        self.temp_dir = tempfile.mkdtemp()
        self.registry_path = os.path.join(self.temp_dir, "registry.json")
        self.registry = SkillRegistry(registry_path=self.registry_path)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_creates_registry(self):
        """Test that initialization creates a registry file."""
        self.assertTrue(os.path.exists(self.registry_path))
        with open(self.registry_path) as f:
            data = json.load(f)
        self.assertIn("skills", data)
        self.assertGreater(len(data["skills"]), 0)

    def test_init_loads_builtins(self):
        """Test that initialization loads built-in skills."""
        self.assertGreater(len(self.registry), 0)
        # Check for known built-in skills
        self.assertIn("code-review", self.registry)

    def test_count(self):
        """Test skill count."""
        count = self.registry.count()
        self.assertGreater(count, 0)
        self.assertEqual(count, len(self.registry))

    def test_get_existing(self):
        """Test retrieving an existing skill."""
        skill = self.registry.get("code-review")
        self.assertIsNotNone(skill)
        self.assertEqual(skill.name, "code-review")
        self.assertIsInstance(skill, Skill)

    def test_get_nonexistent(self):
        """Test retrieving a nonexistent skill returns None."""
        skill = self.registry.get("nonexistent-skill-xyz")
        self.assertIsNone(skill)

    def test_add_new_skill(self):
        """Test adding a new skill to the registry."""
        new_skill = Skill(
            name="test-skill",
            description="A test skill for unit testing",
            author="Test Author",
            version="0.1.0",
            tags=["test"],
        )
        self.registry.add(new_skill)
        self.assertIn("test-skill", self.registry)
        retrieved = self.registry.get("test-skill")
        self.assertEqual(retrieved.description, "A test skill for unit testing")

    def test_add_duplicate_raises(self):
        """Test that adding a duplicate skill raises ValueError."""
        skill = Skill(name="code-review", description="duplicate")
        with self.assertRaises(ValueError):
            self.registry.add(skill)

    def test_update_skill(self):
        """Test updating an existing skill."""
        updated = self.registry.update(
            "code-review",
            description="Updated description",
            version="2.0.0",
        )
        self.assertEqual(updated.description, "Updated description")
        self.assertEqual(updated.version, "2.0.0")

    def test_update_nonexistent_raises(self):
        """Test that updating a nonexistent skill raises KeyError."""
        with self.assertRaises(KeyError):
            self.registry.update("nonexistent", description="test")

    def test_remove_skill(self):
        """Test removing a skill from the registry."""
        # Add a skill first
        skill = Skill(name="to-remove", description="will be removed")
        self.registry.add(skill)
        self.assertIn("to-remove", self.registry)

        # Remove it
        removed = self.registry.remove("to-remove")
        self.assertEqual(removed.name, "to-remove")
        self.assertNotIn("to-remove", self.registry)

    def test_remove_nonexistent_raises(self):
        """Test that removing a nonexistent skill raises KeyError."""
        with self.assertRaises(KeyError):
            self.registry.remove("nonexistent-skill-xyz")

    def test_search_by_tag(self):
        """Test searching skills by tag."""
        results = self.registry.search_by_tag("security")
        self.assertGreater(len(results), 0)
        for skill in results:
            self.assertTrue(
                any("security" in t.lower() for t in skill.tags)
            )

    def test_search_by_nonexistent_tag(self):
        """Test searching by a tag that doesn't exist."""
        results = self.registry.search_by_tag("nonexistent-tag-xyz")
        self.assertEqual(len(results), 0)

    def test_search_by_capability(self):
        """Test searching skills by capability."""
        results = self.registry.search_by_capability("bug-detection")
        self.assertGreater(len(results), 0)
        for skill in results:
            self.assertTrue(
                any("bug-detection" in c.lower() for c in skill.capabilities)
            )

    def test_search_by_framework(self):
        """Test searching skills by framework."""
        results = self.registry.search_by_framework("claude")
        self.assertGreater(len(results), 0)
        for skill in results:
            self.assertIn("claude", [f.lower() for f in skill.framework_support])

    def test_list_all(self):
        """Test listing all skills."""
        all_skills = self.registry.list_all()
        self.assertEqual(len(all_skills), self.registry.count())

    def test_list_installed(self):
        """Test listing installed skills (initially empty)."""
        installed = self.registry.list_installed()
        self.assertEqual(len(installed), 0)

    def test_mark_installed(self):
        """Test marking a skill as installed."""
        self.registry.mark_installed("code-review", "/tmp/test")
        skill = self.registry.get("code-review")
        self.assertTrue(skill.installed)
        self.assertEqual(skill.install_path, "/tmp/test")

    def test_mark_uninstalled(self):
        """Test marking a skill as uninstalled."""
        self.registry.mark_installed("code-review")
        self.registry.mark_uninstalled("code-review")
        skill = self.registry.get("code-review")
        self.assertFalse(skill.installed)

    def test_contains(self):
        """Test the 'in' operator."""
        self.assertIn("code-review", self.registry)
        self.assertNotIn("nonexistent", self.registry)

    def test_iter(self):
        """Test iterating over the registry."""
        skills = list(self.registry)
        self.assertGreater(len(skills), 0)
        for skill in skills:
            self.assertIsInstance(skill, Skill)

    def test_export_all(self):
        """Test exporting all skills."""
        exported = self.registry.export_all()
        self.assertIsInstance(exported, list)
        self.assertGreater(len(exported), 0)
        for item in exported:
            self.assertIsInstance(item, dict)
            self.assertIn("name", item)

    def test_persistence(self):
        """Test that the registry persists to disk."""
        # Modify registry
        self.registry.add(
            Skill(name="persist-test", description="persistence test")
        )
        # Create new registry instance from same path
        new_registry = SkillRegistry(registry_path=self.registry_path)
        self.assertIn("persist-test", new_registry)
        self.assertEqual(
            new_registry.get("persist-test").description,
            "persistence test",
        )


if __name__ == "__main__":
    unittest.main()
