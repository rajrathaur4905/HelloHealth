"""
Classifier Service — BART Zero-Shot Classification Wrapper.

Wraps the Hugging Face zero-shot classification pipeline with:
  - Lazy model loading (loads on first request, not at server startup)
  - Real confidence scores from the model (never hardcoded)
  - Timeout handling for slow inference
  - Feature flag to disable model entirely (for testing/dev)

Usage:
    from app.services.classifier import ClassifierService

    classifier = ClassifierService()
    result = await classifier.classify("I have a headache and nausea")
"""

import asyncio
import logging
import time
from functools import lru_cache

from app.config import settings

logger = logging.getLogger(__name__)


class ClassificationResult:
    """Structured result from the classifier."""

    def __init__(self, label: str, confidence: float, all_scores: dict[str, float]):
        self.label = label
        self.confidence = confidence
        self.all_scores = all_scores

    def __repr__(self) -> str:
        return f"ClassificationResult(label='{self.label}', confidence={self.confidence:.4f})"


class ClassifierService:
    """Zero-shot classification service using BART-MNLI.

    The model classifies free-text symptom descriptions against
    a set of candidate labels (condition names) and returns the
    best matching label with its real confidence score.
    """

    # Candidate labels the model classifies against
    CANDIDATE_LABELS = [
        "headache or migraine",
        "fever or viral infection",
        "cough or respiratory infection",
        "fatigue or tiredness",
        "nausea or digestive upset",
        "sore throat",
        "back pain",
        "stomach pain or abdominal pain",
        "dizziness or vertigo",
        "chest pain or discomfort",
        "anxiety or nervousness",
        "insomnia or sleep problems",
        "allergies",
        "diarrhea or food poisoning",
        "joint pain or arthritis",
        "skin rash or irritation",
        "shortness of breath",
        "constipation",
        "eye strain",
        "muscle pain or soreness",
        "ear pain or infection",
        "cold or flu",
        "dehydration",
        "heartburn or acid reflux",
        "toothache or dental pain",
        "urinary issues",
        "depression or low mood",
        "high blood pressure",
        "sunburn or skin burn",
    ]

    # Maps model labels to knowledge base condition IDs
    LABEL_TO_KB_ID: dict[str, str] = {
        "headache or migraine": "headache",
        "fever or viral infection": "fever",
        "cough or respiratory infection": "cough",
        "fatigue or tiredness": "fatigue",
        "nausea or digestive upset": "nausea",
        "sore throat": "sore_throat",
        "back pain": "back_pain",
        "stomach pain or abdominal pain": "stomach_pain",
        "dizziness or vertigo": "dizziness",
        "chest pain or discomfort": "chest_pain",
        "anxiety or nervousness": "anxiety",
        "insomnia or sleep problems": "insomnia",
        "allergies": "allergies",
        "diarrhea or food poisoning": "diarrhea",
        "joint pain or arthritis": "joint_pain",
        "skin rash or irritation": "rash",
        "shortness of breath": "shortness_of_breath",
        "constipation": "constipation",
        "eye strain": "eye_strain",
        "muscle pain or soreness": "muscle_pain",
        "ear pain or infection": "ear_pain",
        "cold or flu": "cold_flu",
        "dehydration": "dehydration",
        "heartburn or acid reflux": "heartburn",
        "toothache or dental pain": "toothache",
        "urinary issues": "urinary_issues",
        "depression or low mood": "depression_symptoms",
        "high blood pressure": "high_blood_pressure",
        "sunburn or skin burn": "skin_burn",
    }

    def __init__(self):
        self._pipeline = None
        self._model_loaded = False
        self._load_time: float | None = None

    @property
    def is_loaded(self) -> bool:
        return self._model_loaded

    @property
    def is_enabled(self) -> bool:
        return settings.MODEL_ENABLED

    def _load_model(self) -> None:
        """Load the model on first use (lazy initialization)."""
        if self._model_loaded:
            return

        if not settings.MODEL_ENABLED:
            logger.warning("AI model is disabled via MODEL_ENABLED=false")
            return

        logger.info("Loading AI model: %s (this may take 30-60 seconds)...", settings.MODEL_NAME)
        start = time.time()

        try:
            from transformers import pipeline

            self._pipeline = pipeline(
                "zero-shot-classification",
                model=settings.MODEL_NAME,
            )
            self._load_time = round(time.time() - start, 2)
            self._model_loaded = True
            logger.info("AI model loaded successfully in %.2fs", self._load_time)

        except Exception as e:
            logger.error("Failed to load AI model: %s", e)
            raise

    async def classify(self, text: str, timeout: float = 30.0) -> ClassificationResult | None:
        """Classify symptom text against candidate labels.

        Args:
            text: User's symptom description
            timeout: Maximum seconds to wait for inference

        Returns:
            ClassificationResult with label, confidence, and all scores.
            None if model is disabled or inference fails.
        """
        if not settings.MODEL_ENABLED:
            logger.info("Model disabled — skipping classification")
            return None

        # Lazy load the model
        self._load_model()

        if self._pipeline is None:
            return None

        try:
            # Run inference in a thread pool to avoid blocking the async event loop
            loop = asyncio.get_event_loop()
            start = time.time()

            result = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self._pipeline(text, self.CANDIDATE_LABELS, multi_label=False),
                ),
                timeout=timeout,
            )

            duration_ms = round((time.time() - start) * 1000)
            logger.info(
                "Classification completed in %dms: '%s' → %s (%.4f)",
                duration_ms,
                text[:50],
                result["labels"][0],
                result["scores"][0],
            )

            # Build scores dictionary for all labels
            all_scores = {
                label: round(score, 4)
                for label, score in zip(result["labels"], result["scores"])
            }

            return ClassificationResult(
                label=result["labels"][0],
                confidence=round(float(result["scores"][0]), 4),
                all_scores=all_scores,
            )

        except asyncio.TimeoutError:
            logger.error("Classification timed out after %.1fs for: '%s'", timeout, text[:50])
            return None
        except Exception as e:
            logger.error("Classification failed: %s", e)
            return None

    def get_kb_id_for_label(self, label: str) -> str | None:
        """Map a model label back to a knowledge base condition ID."""
        return self.LABEL_TO_KB_ID.get(label)


# ── Singleton & Dependency ───────────────────────────────────

_classifier_instance: ClassifierService | None = None


def get_classifier() -> ClassifierService:
    """FastAPI dependency — returns the shared ClassifierService instance."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = ClassifierService()
    return _classifier_instance
