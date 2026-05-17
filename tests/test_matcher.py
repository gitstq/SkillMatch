"""Tests for the Skill Matching Engine (TF-IDF + BM25).

Tests cover TF-IDF computation, BM25 scoring, cosine similarity,
hybrid matching, and filtering by framework, tags, and capabilities.
"""

import unittest
import tempfile
import os
import json

from skillmatch.models import Skill, SearchResult
from skillmatch.matcher import TFIDFEngine, BM25Engine, SkillMatcher
from skillmatch.registry import SkillRegistry


class TestTFIDFEngine(unittest.TestCase):
    """Test cases for the TF-IDF engine."""

    def setUp(self):
        """Set up test fixtures with sample documents."""
        self.engine = TFIDFEngine()
        self.documents = [
            "python code review tool for static analysis",
            "javascript testing framework for unit tests",
            "python security scanner for vulnerability detection",
            "documentation generator for API docs",
            "code refactoring assistant for design patterns",
        ]

    def test_fit_empty_documents(self):
        """Test fitting with empty document list."""
        engine = TFIDFEngine()
        engine.fit([])
        self.assertEqual(len(engine.vocabulary), 0)
        self.assertEqual(len(engine.idf), 0)
        self.assertEqual(len(engine.tfidf_vectors), 0)

    def test_fit_builds_vocabulary(self):
        """Test that fitting builds a proper vocabulary."""
        self.engine.fit(self.documents)
        self.assertGreater(len(self.engine.vocabulary), 0)
        # Common terms should be in vocabulary
        self.assertIn("python", self.engine.vocabulary)
        self.assertIn("code", self.engine.vocabulary)

    def test_fit_builds_idf(self):
        """Test that IDF values are computed correctly."""
        self.engine.fit(self.documents)
        self.assertGreater(len(self.engine.idf), 0)
        # IDF should be positive
        for term, idf_val in self.engine.idf.items():
            self.assertGreater(idf_val, 0)

    def test_fit_builds_tfidf_vectors(self):
        """Test that TF-IDF vectors are generated for each document."""
        self.engine.fit(self.documents)
        self.assertEqual(len(self.engine.tfidf_vectors), len(self.documents))
        for vec in self.engine.tfidf_vectors:
            self.assertIsInstance(vec, dict)

    def test_query_returns_vector(self):
        """Test that querying returns a TF-IDF vector."""
        self.engine.fit(self.documents)
        result = self.engine.query("python code review")
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)

    def test_query_empty_string(self):
        """Test querying with empty string returns empty vector."""
        self.engine.fit(self.documents)
        result = self.engine.query("")
        self.assertEqual(result, {})

    def test_query_before_fit(self):
        """Test querying before fitting returns empty vector."""
        engine = TFIDFEngine()
        result = engine.query("test")
        self.assertEqual(result, {})

    def test_cosine_similarity_identical(self):
        """Test cosine similarity of identical vectors is 1.0."""
        vec = {"a": 1.0, "b": 2.0, "c": 3.0}
        sim = TFIDFEngine.cosine_similarity(vec, vec)
        self.assertAlmostEqual(sim, 1.0, places=5)

    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity of orthogonal vectors is 0.0."""
        vec_a = {"a": 1.0, "b": 2.0}
        vec_b = {"c": 3.0, "d": 4.0}
        sim = TFIDFEngine.cosine_similarity(vec_a, vec_b)
        self.assertAlmostEqual(sim, 0.0, places=5)

    def test_cosine_similarity_empty_vectors(self):
        """Test cosine similarity with empty vectors returns 0.0."""
        sim = TFIDFEngine.cosine_similarity({}, {"a": 1.0})
        self.assertAlmostEqual(sim, 0.0, places=5)

        sim = TFIDFEngine.cosine_similarity({"a": 1.0}, {})
        self.assertAlmostEqual(sim, 0.0, places=5)

    def test_cosine_similarity_partial_overlap(self):
        """Test cosine similarity with partial term overlap."""
        vec_a = {"a": 1.0, "b": 1.0}
        vec_b = {"b": 1.0, "c": 1.0}
        sim = TFIDFEngine.cosine_similarity(vec_a, vec_b)
        self.assertGreater(sim, 0.0)
        self.assertLess(sim, 1.0)


class TestBM25Engine(unittest.TestCase):
    """Test cases for the BM25 engine."""

    def setUp(self):
        """Set up test fixtures with sample documents."""
        self.engine = BM25Engine(k1=1.5, b=0.75)
        self.documents = [
            "python code review tool for static analysis",
            "javascript testing framework for unit tests",
            "python security scanner for vulnerability detection",
            "documentation generator for API docs",
            "code refactoring assistant for design patterns",
        ]

    def test_fit_empty_documents(self):
        """Test fitting with empty document list."""
        engine = BM25Engine()
        engine.fit([])
        self.assertEqual(len(engine.documents), 0)
        self.assertEqual(engine.avg_dl, 0)

    def test_fit_computes_avg_dl(self):
        """Test that average document length is computed."""
        self.engine.fit(self.documents)
        total = sum(len(d.split()) for d in self.documents)
        expected_avg = total / len(self.documents)
        self.assertAlmostEqual(self.engine.avg_dl, expected_avg, places=2)

    def test_fit_computes_doc_freq(self):
        """Test that document frequency is computed correctly."""
        self.engine.fit(self.documents)
        self.assertGreater(len(self.engine.doc_freq), 0)
        # "for" appears in all documents
        self.assertEqual(self.engine.doc_freq.get("for", 0), len(self.documents))

    def test_fit_computes_idf(self):
        """Test that IDF values are computed."""
        self.engine.fit(self.documents)
        self.assertGreater(len(self.engine.idf), 0)
        for term, idf_val in self.engine.idf.items():
            self.assertGreater(idf_val, 0)

    def test_score_returns_float(self):
        """Test that scoring returns a float."""
        self.engine.fit(self.documents)
        score = self.engine.score("python code", 0)
        self.assertIsInstance(score, float)

    def test_score_relevant_doc_higher(self):
        """Test that relevant documents score higher."""
        self.engine.fit(self.documents)
        # Document 0 is about "python code review"
        score_relevant = self.engine.score("python code review", 0)
        # Document 1 is about "javascript testing"
        score_irrelevant = self.engine.score("python code review", 1)
        self.assertGreater(score_relevant, score_irrelevant)

    def test_score_invalid_index(self):
        """Test scoring with invalid document index returns 0."""
        self.engine.fit(self.documents)
        score = self.engine.score("test", -1)
        self.assertEqual(score, 0.0)
        score = self.engine.score("test", 999)
        self.assertEqual(score, 0.0)

    def test_score_all_returns_sorted(self):
        """Test that score_all returns results sorted by score."""
        self.engine.fit(self.documents)
        results = self.engine.score_all("python code")
        scores = [s for _, s in results]
        # Should be sorted descending
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_score_all_correct_length(self):
        """Test that score_all returns one score per document."""
        self.engine.fit(self.documents)
        results = self.engine.score_all("test")
        self.assertEqual(len(results), len(self.documents))


class TestSkillMatcher(unittest.TestCase):
    """Test cases for the SkillMatcher hybrid engine."""

    def setUp(self):
        """Set up test fixtures with a temporary registry."""
        self.temp_dir = tempfile.mkdtemp()
        registry_path = os.path.join(self.temp_dir, "registry.json")
        self.registry = SkillRegistry(registry_path=registry_path)
        self.matcher = SkillMatcher(self.registry)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_search_returns_results(self):
        """Test that search returns results for valid queries."""
        results = self.matcher.search("code review")
        self.assertGreater(len(results), 0)

    def test_search_returns_search_results(self):
        """Test that search returns SearchResult objects."""
        results = self.matcher.search("testing")
        for result in results:
            self.assertIsInstance(result, SearchResult)
            self.assertIsInstance(result.skill, Skill)
            self.assertIsInstance(result.score, float)

    def test_search_results_sorted(self):
        """Test that search results are sorted by score descending."""
        results = self.matcher.search("security")
        scores = [r.score for r in results]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_search_respects_top_k(self):
        """Test that top_k limits the number of results."""
        results = self.matcher.search("code", top_k=3)
        self.assertLessEqual(len(results), 3)

    def test_search_filter_framework(self):
        """Test filtering by framework."""
        results = self.matcher.search("code", framework="claude")
        for result in results:
            self.assertIn("claude", [f.lower() for f in result.skill.framework_support])

    def test_search_filter_nonexistent_framework(self):
        """Test filtering by nonexistent framework returns empty."""
        results = self.matcher.search("code", framework="nonexistent_framework_xyz")
        self.assertEqual(len(results), 0)

    def test_search_filter_tags(self):
        """Test filtering by tags."""
        results = self.matcher.search("code", tags=["security"])
        for result in results:
            tag_names = [t.lower() for t in result.skill.tags]
            self.assertTrue(any("security" in t for t in tag_names))

    def test_search_filter_capability(self):
        """Test filtering by capability."""
        results = self.matcher.search("code", capability="bug-detection")
        for result in results:
            cap_names = [c.lower() for c in result.skill.capabilities]
            self.assertIn("bug-detection", cap_names)

    def test_search_empty_query(self):
        """Test that empty query returns empty results."""
        results = self.matcher.search("")
        self.assertEqual(len(results), 0)

    def test_search_matched_fields(self):
        """Test that matched fields are populated."""
        results = self.matcher.search("code review")
        if results:
            self.assertIsInstance(results[0].matched_fields, list)

    def test_rebuild(self):
        """Test that rebuild refreshes the index."""
        self.matcher.rebuild()
        results = self.matcher.search("code")
        self.assertGreater(len(results), 0)

    def test_search_specific_skill(self):
        """Test searching for a specific skill by name."""
        results = self.matcher.search("code-review")
        self.assertGreater(len(results), 0)
        # First result should be the code-review skill
        self.assertEqual(results[0].skill.name, "code-review")


if __name__ == "__main__":
    unittest.main()
