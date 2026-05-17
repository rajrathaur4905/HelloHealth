"""
Knowledge Base Service.

Loads the structured health knowledge base from JSON and provides
fuzzy keyword matching to find relevant conditions from user input.
This is the primary lookup mechanism — fast, deterministic, and safe.
The AI classifier is used only as a fallback when no KB match is found.

Usage:
    from app.services.knowledge_base import KnowledgeBaseService

    kb = KnowledgeBaseService()
    result = kb.search("I have a bad headache and feel dizzy")
"""

import json
import logging
import random
from difflib import SequenceMatcher
from pathlib import Path

logger = logging.getLogger(__name__)

# Path to the knowledge base JSON file
_KB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_base.json"


class KBMatch:
    """Represents a matched condition from the knowledge base."""

    def __init__(self, condition: dict, score: float):
        self.condition = condition
        self.score = score

    @property
    def confidence(self) -> float:
        """Generate a realistic confidence based on match score and condition's range."""
        low, high = self.condition.get("confidence_range", [0.5, 0.7])
        # Scale the confidence range by match quality
        return round(low + (high - low) * min(self.score, 1.0), 4)


class KnowledgeBaseService:
    """Service for searching the health knowledge base.

    Performs keyword matching with fuzzy similarity scoring
    to find the best matching condition for user-described symptoms.
    """

    def __init__(self, kb_path: Path | None = None):
        self._kb_path = kb_path or _KB_PATH
        self._conditions: list[dict] = []
        self._fallback: dict = {}
        self._disclaimer: str = ""
        self._loaded = False

    def _load(self) -> None:
        """Load the knowledge base from disk (lazy, one-time)."""
        if self._loaded:
            return

        try:
            with open(self._kb_path, encoding="utf-8") as f:
                data = json.load(f)

            self._conditions = data.get("conditions", [])
            self._fallback = data.get("fallback", {})
            self._disclaimer = data.get("disclaimer", "")
            self._loaded = True

            logger.info(
                "Knowledge base loaded: %d conditions from %s",
                len(self._conditions),
                self._kb_path.name,
            )
        except FileNotFoundError:
            logger.error("Knowledge base file not found: %s", self._kb_path)
            raise
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in knowledge base: %s", e)
            raise

    @property
    def disclaimer(self) -> str:
        """Return the medical disclaimer text."""
        self._load()
        return self._disclaimer

    @property
    def condition_count(self) -> int:
        """Return the number of conditions in the knowledge base."""
        self._load()
        return len(self._conditions)

    def search(self, query: str) -> KBMatch | None:
        """Search for the best matching condition.

        Uses a two-pass approach:
          1. Exact keyword matching (fast, precise)
          2. Fuzzy similarity matching (catches typos, partial matches)

        Returns the best match if score exceeds threshold, else None.
        """
        self._load()

        query_lower = query.lower().strip()
        if not query_lower:
            return None

        best_match: dict | None = None
        best_score: float = 0.0

        for condition in self._conditions:
            score = self._calculate_match_score(query_lower, condition)
            if score > best_score:
                best_score = score
                best_match = condition

        # Minimum threshold — below this, the match is too weak
        if best_score < 0.25 or best_match is None:
            return None

        logger.info(
            "KB match: '%s' → %s (score=%.3f)",
            query[:50],
            best_match["id"],
            best_score,
        )
        return KBMatch(condition=best_match, score=best_score)

    def get_fallback(self) -> dict:
        """Return the fallback response when no condition matches."""
        self._load()
        return self._fallback

    def list_conditions(self) -> list[dict]:
        """Return a summary list of all conditions (for API/frontend)."""
        self._load()
        return [
            {"id": c["id"], "name": c["name"], "severity": c["severity"]}
            for c in self._conditions
        ]

    def _calculate_match_score(self, query: str, condition: dict) -> float:
        """Calculate how well a query matches a condition.

        Scoring:
          - Exact keyword found in query:  0.8-1.0 (based on keyword length)
          - Fuzzy match (>0.7 similarity):  0.4-0.7
          - Symptom term match:             0.2-0.5

        Multiple matches are combined (capped at 1.0).
        """
        score = 0.0
        keywords = condition.get("keywords", [])
        symptoms = condition.get("symptoms", [])

        # Pass 1: Exact keyword matching
        for keyword in keywords:
            if keyword in query:
                # Longer keywords are more specific → higher score
                keyword_weight = min(len(keyword) / 15, 1.0)
                score = max(score, 0.6 + 0.4 * keyword_weight)

        # Pass 2: Fuzzy matching on keywords (catches typos)
        if score < 0.6:
            query_words = query.split()
            for keyword in keywords:
                for word in query_words:
                    similarity = SequenceMatcher(None, word, keyword).ratio()
                    if similarity > 0.75:
                        score = max(score, 0.4 + 0.3 * similarity)

        # Pass 3: Symptom term matching (weaker signal)
        for symptom in symptoms:
            symptom_words = symptom.lower().split()
            for sw in symptom_words:
                if len(sw) > 3 and sw in query:
                    score = min(score + 0.15, 1.0)

        return round(min(score, 1.0), 4)
