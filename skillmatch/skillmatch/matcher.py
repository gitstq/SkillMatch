"""Core Skill Matching Engine for SkillMatch.

Implements a hybrid TF-IDF + BM25 matching algorithm for intelligent
skill discovery. Pure Python implementation using only standard library
modules (math, collections, re). No external dependencies required.
"""

import math
import re
from collections import Counter, defaultdict

from skillmatch.models import Skill, SearchResult
from skillmatch.utils import tokenize, normalize_text


class TFIDFEngine:
    """Pure Python TF-IDF implementation for text similarity scoring.

    Computes Term Frequency-Inverse Document Frequency scores to measure
    the importance of terms in skill descriptions relative to the corpus.

    Attributes:
        documents: List of tokenized document lists.
        vocabulary: Set of all unique terms across documents.
        idf: Dictionary mapping terms to their IDF values.
        tfidf_vectors: List of TF-IDF vectors for each document.
    """

    def __init__(self):
        """Initialize the TF-IDF engine with empty state."""
        self.documents = []
        self.vocabulary = set()
        self.idf = {}
        self.tfidf_vectors = []

    def fit(self, documents):
        """Build the TF-IDF model from a list of text documents.

        Computes IDF values for all terms and generates TF-IDF vectors
        for each document.

        Args:
            documents: List of text strings to index.
        """
        self.documents = [tokenize(doc) for doc in documents]

        # Build vocabulary
        self.vocabulary = set()
        for doc_tokens in self.documents:
            self.vocabulary.update(doc_tokens)

        # Compute IDF: log(N / df(t)) where df(t) = number of docs containing t
        n_docs = len(self.documents)
        if n_docs == 0:
            self.idf = {}
            self.tfidf_vectors = []
            return

        doc_freq = Counter()
        for doc_tokens in self.documents:
            unique_tokens = set(doc_tokens)
            for token in unique_tokens:
                doc_freq[token] += 1

        self.idf = {}
        for term in self.vocabulary:
            df = doc_freq.get(term, 0)
            # Use smoothed IDF to avoid division by zero
            self.idf[term] = math.log((n_docs + 1) / (df + 1)) + 1

        # Compute TF-IDF vectors for each document
        self.tfidf_vectors = []
        for doc_tokens in self.documents:
            tf = Counter(doc_tokens)
            max_tf = max(tf.values()) if tf else 1
            vector = {}
            for term, count in tf.items():
                # Normalized TF * IDF
                normalized_tf = 0.5 + 0.5 * (count / max_tf)
                vector[term] = normalized_tf * self.idf.get(term, 0)
            self.tfidf_vectors.append(vector)

    def query(self, text):
        """Compute TF-IDF vector for a query string.

        Args:
            text: Query text string.

        Returns:
            dict: TF-IDF vector for the query.
        """
        tokens = tokenize(text)
        if not tokens or not self.idf:
            return {}

        tf = Counter(tokens)
        max_tf = max(tf.values()) if tf else 1
        vector = {}
        for term, count in tf.items():
            if term in self.idf:
                normalized_tf = 0.5 + 0.5 * (count / max_tf)
                vector[term] = normalized_tf * self.idf.get(term, 0)
        return vector

    @staticmethod
    def cosine_similarity(vec_a, vec_b):
        """Compute cosine similarity between two sparse vectors.

        Args:
            vec_a: First sparse vector (dict).
            vec_b: Second sparse vector (dict).

        Returns:
            float: Cosine similarity score between 0 and 1.
        """
        if not vec_a or not vec_b:
            return 0.0

        # Dot product (only common terms)
        common_terms = set(vec_a.keys()) & set(vec_b.keys())
        dot = sum(vec_a[t] * vec_b[t] for t in common_terms)

        # Magnitudes
        mag_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
        mag_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))

        if mag_a == 0 or mag_b == 0:
            return 0.0

        return dot / (mag_a * mag_b)


class BM25Engine:
    """Pure Python BM25 (Okapi BM25) implementation for text ranking.

    BM25 is a ranking function used by search engines to estimate the
    relevance of documents to a given query. It improves upon TF-IDF
    by incorporating document length normalization.

    Attributes:
        k1: Term frequency saturation parameter.
        b: Length normalization parameter.
        documents: List of tokenized document lists.
        avg_dl: Average document length.
        doc_freq: Term document frequency counts.
        idf: Dictionary mapping terms to IDF values.
    """

    def __init__(self, k1=1.5, b=0.75):
        """Initialize the BM25 engine.

        Args:
            k1: Controls term frequency saturation (default: 1.5).
                 Higher values increase the impact of term frequency.
            b: Controls length normalization (default: 0.75).
               0 means no normalization, 1 means full normalization.
        """
        self.k1 = k1
        self.b = b
        self.documents = []
        self.avg_dl = 0
        self.doc_freq = Counter()
        self.idf = {}

    def fit(self, documents):
        """Build the BM25 model from a list of text documents.

        Args:
            documents: List of text strings to index.
        """
        self.documents = [tokenize(doc) for doc in documents]
        n_docs = len(self.documents)

        if n_docs == 0:
            self.avg_dl = 0
            self.doc_freq = Counter()
            self.idf = {}
            return

        # Compute average document length
        total_length = sum(len(doc) for doc in self.documents)
        self.avg_dl = total_length / n_docs

        # Compute document frequency for each term
        self.doc_freq = Counter()
        for doc_tokens in self.documents:
            unique_tokens = set(doc_tokens)
            for token in unique_tokens:
                self.doc_freq[token] += 1

        # Compute IDF using Robertson-Sparck Jones formula:
        # IDF(t) = log((N - n(t) + 0.5) / (n(t) + 0.5) + 1)
        self.idf = {}
        for term, df in self.doc_freq.items():
            self.idf[term] = math.log((n_docs - df + 0.5) / (df + 0.5) + 1)

    def score(self, query_text, doc_index):
        """Compute BM25 score for a query against a specific document.

        Args:
            query_text: Query text string.
            doc_index: Index of the document to score against.

        Returns:
            float: BM25 relevance score.
        """
        if doc_index < 0 or doc_index >= len(self.documents):
            return 0.0

        query_tokens = tokenize(query_text)
        doc_tokens = self.documents[doc_index]
        doc_len = len(doc_tokens)

        tf = Counter(doc_tokens)
        score = 0.0

        for term in query_tokens:
            if term not in self.idf:
                continue

            term_tf = tf.get(term, 0)
            idf_val = self.idf[term]

            # BM25 term score
            numerator = term_tf * (self.k1 + 1)
            denominator = term_tf + self.k1 * (
                1 - self.b + self.b * (doc_len / max(self.avg_dl, 1))
            )
            score += idf_val * (numerator / denominator)

        return score

    def score_all(self, query_text):
        """Compute BM25 scores for a query against all documents.

        Args:
            query_text: Query text string.

        Returns:
            list: List of (doc_index, score) tuples sorted by score descending.
        """
        scores = []
        for i in range(len(self.documents)):
            s = self.score(query_text, i)
            scores.append((i, s))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores


class SkillMatcher:
    """Hybrid TF-IDF + BM25 skill matching engine.

    Combines TF-IDF cosine similarity with BM25 scoring to provide
    accurate skill matching from natural language queries. Supports
    filtering by framework, tags, and capabilities.

    Attributes:
        registry: Reference to the SkillRegistry instance.
        tfidf: TF-IDF engine instance.
        bm25: BM25 engine instance.
        skills: List of Skill objects used for matching.
        tfidf_weight: Weight for TF-IDF scores in hybrid scoring.
        bm25_weight: Weight for BM25 scores in hybrid scoring.
    """

    def __init__(self, registry, tfidf_weight=0.4, bm25_weight=0.6):
        """Initialize the skill matcher.

        Args:
            registry: SkillRegistry instance containing skills to match against.
            tfidf_weight: Weight for TF-IDF component (default: 0.4).
            bm25_weight: Weight for BM25 component (default: 0.6).
        """
        self.registry = registry
        self.tfidf = TFIDFEngine()
        self.bm25 = BM25Engine()
        self.skills = []
        self.tfidf_weight = tfidf_weight
        self.bm25_weight = bm25_weight
        self._build_index()

    def _build_index(self):
        """Build the TF-IDF and BM25 indexes from registry skills.

        Creates a combined text representation for each skill by joining
        its name, description, tags, and capabilities.
        """
        self.skills = list(self.registry.skills.values())
        documents = []
        for skill in self.skills:
            combined = self._skill_to_text(skill)
            documents.append(combined)

        self.tfidf.fit(documents)
        self.bm25.fit(documents)

    def _skill_to_text(self, skill):
        """Convert a skill to a searchable text representation.

        Combines the skill's name, description, tags, and capabilities
        into a single text string for indexing.

        Args:
            skill: Skill object to convert.

        Returns:
            str: Combined text representation.
        """
        parts = [
            skill.name,
            skill.description,
            " ".join(skill.tags),
            " ".join(skill.capabilities),
            " ".join(skill.framework_support),
        ]
        return " ".join(parts)

    def _find_matched_fields(self, skill, query_tokens):
        """Identify which fields of a skill matched the query.

        Args:
            skill: Skill object to check.
            query_tokens: List of query token strings.

        Returns:
            list: List of field names that had matching tokens.
        """
        matched = []
        query_set = set(query_tokens)

        # Check name
        name_tokens = set(tokenize(skill.name))
        if name_tokens & query_set:
            matched.append("name")

        # Check description
        desc_tokens = set(tokenize(skill.description))
        if desc_tokens & query_set:
            matched.append("description")

        # Check tags
        tag_tokens = set()
        for tag in skill.tags:
            tag_tokens.update(tokenize(tag))
        if tag_tokens & query_set:
            matched.append("tags")

        # Check capabilities
        cap_tokens = set()
        for cap in skill.capabilities:
            cap_tokens.update(tokenize(cap))
        if cap_tokens & query_set:
            matched.append("capabilities")

        # Check framework support
        fw_tokens = set()
        for fw in skill.framework_support:
            fw_tokens.update(tokenize(fw))
        if fw_tokens & query_set:
            matched.append("framework_support")

        return matched

    def search(
        self,
        query,
        top_k=10,
        framework=None,
        tags=None,
        capability=None,
    ):
        """Search for skills matching a natural language query.

        Uses a hybrid TF-IDF + BM25 scoring approach. Results can be
        filtered by framework, tags, and capabilities.

        Args:
            query: Natural language search query string.
            top_k: Maximum number of results to return (default: 10).
            framework: Optional framework name to filter by.
            tags: Optional list of tags to filter by.
            capability: Optional capability to filter by.

        Returns:
            list: List of SearchResult objects sorted by relevance score.
        """
        query_tokens = tokenize(query)

        if not query_tokens or not self.skills:
            return []

        # Compute TF-IDF scores
        query_vec = self.tfidf.query(query)
        tfidf_scores = []
        for i, skill in enumerate(self.skills):
            doc_vec = self.tfidf.tfidf_vectors[i] if i < len(self.tfidf.tfidf_vectors) else {}
            sim = self.tfidf.cosine_similarity(query_vec, doc_vec)
            tfidf_scores.append((i, sim))

        # Compute BM25 scores
        bm25_scores = self.bm25.score_all(query)
        bm25_dict = {idx: score for idx, score in bm25_scores}

        # Combine scores
        combined_scores = []
        for i, skill in enumerate(self.skills):
            tfidf_score = tfidf_scores[i][1] if i < len(tfidf_scores) else 0
            bm25_score = bm25_dict.get(i, 0)

            # Normalize scores to [0, 1] range
            tfidf_norm = min(tfidf_score, 1.0)
            bm25_norm = min(bm25_score / max(self.bm25.avg_dl, 1), 1.0)

            # Weighted hybrid score
            hybrid_score = (
                self.tfidf_weight * tfidf_norm + self.bm25_weight * bm25_norm
            )

            # Apply filters
            if framework and framework.lower() not in [
                f.lower() for f in skill.framework_support
            ]:
                continue

            if tags:
                skill_tags_lower = [t.lower() for t in skill.tags]
                if not any(t.lower() in skill_tags_lower for t in tags):
                    continue

            if capability and capability.lower() not in [
                c.lower() for c in skill.capabilities
            ]:
                continue

            matched_fields = self._find_matched_fields(skill, query_tokens)

            combined_scores.append(
                SearchResult(
                    skill=skill,
                    score=hybrid_score,
                    matched_fields=matched_fields,
                )
            )

        # Sort by score descending
        combined_scores.sort(key=lambda x: x.score, reverse=True)

        return combined_scores[:top_k]

    def rebuild(self):
        """Rebuild the search index from the current registry state.

        Call this after modifying the registry to update the search index.
        """
        self._build_index()
