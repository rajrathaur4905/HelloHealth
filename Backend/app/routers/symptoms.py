"""
Symptom Analysis Router.

POST /api/v1/symptoms/check — the core feature endpoint.

Analysis flow:
  1. Validate & sanitize input (Pydantic handles this)
  2. Check Redis cache for identical query
  3. Search the knowledge base (fast, deterministic)
  4. If KB misses, fall back to AI model classification
  5. Cache the result for future identical queries
  6. Save to history if user is authenticated
  7. Return structured response with source tracking
"""

import hashlib
import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_optional_user
from app.database import get_db
from app.models.schemas import (
    AnalysisSource,
    Severity,
    SymptomRequest,
    SymptomResponse,
)
from app.models.symptom_query import SymptomQuery
from app.services.classifier import ClassifierService, get_classifier
from app.services.knowledge_base import KnowledgeBaseService

router = APIRouter(prefix="/api/v1/symptoms", tags=["symptoms"])
logger = logging.getLogger(__name__)

# ── Service Singletons ───────────────────────────────────────
_kb_service: KnowledgeBaseService | None = None


def get_kb_service() -> KnowledgeBaseService:
    """FastAPI dependency for the knowledge base service."""
    global _kb_service
    if _kb_service is None:
        _kb_service = KnowledgeBaseService()
    return _kb_service


# ── Simple In-Memory Cache ───────────────────────────────────
# Redis integration will replace this when Redis is connected.
_cache: dict[str, dict] = {}
_CACHE_MAX_SIZE = 500


def _get_cache_key(query: str) -> str:
    """Generate a deterministic cache key from the query text."""
    normalized = query.lower().strip()
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def _get_cached_result(key: str) -> dict | None:
    return _cache.get(key)


def _set_cached_result(key: str, result: dict) -> None:
    if len(_cache) >= _CACHE_MAX_SIZE:
        oldest_key = next(iter(_cache))
        del _cache[oldest_key]
    _cache[key] = result


async def _save_to_history(
    db: AsyncSession,
    user_id: str,
    query: str,
    response: SymptomResponse,
) -> None:
    """Persist a symptom analysis to the user's history."""
    record = SymptomQuery(
        user_id=user_id,
        symptoms_text=query,
        diagnosis=response.diagnosis,
        confidence=response.confidence,
        severity=response.severity.value,
        source=response.source.value,
    )
    db.add(record)
    # commit is handled by get_db dependency on request completion
    logger.info("History saved for user %s: %s", user_id, response.diagnosis)


# ── Endpoint ─────────────────────────────────────────────────

@router.post("/check", response_model=SymptomResponse)
async def check_symptoms(
    request: Request,
    body: SymptomRequest,
    kb: KnowledgeBaseService = Depends(get_kb_service),
    classifier: ClassifierService = Depends(get_classifier),
    current_user=Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
) -> SymptomResponse:
    """Analyze symptoms and return health information.

    Works for both anonymous and authenticated users.
    If authenticated, the result is saved to the user's history.

    The system uses a two-tier approach:
      1. **Knowledge Base** — fast keyword matching against 30 known conditions
      2. **AI Model** (fallback) — BART zero-shot classification for unmatched queries

    The response always includes a medical disclaimer.
    """
    query = body.symptoms
    logger.info("Symptom check received: '%s'", query[:80])

    # ── Step 1: Check cache ──────────────────────────────────
    cache_key = _get_cache_key(query)
    cached = _get_cached_result(cache_key)
    if cached:
        logger.info("Cache hit for query (key=%s)", cache_key)
        response = SymptomResponse(**cached)
        if current_user:
            await _save_to_history(db, current_user.id, query, response)
        return response

    # ── Step 2: Search knowledge base ────────────────────────
    kb_match = kb.search(query)

    if kb_match and kb_match.score >= 0.5:
        condition = kb_match.condition
        response = SymptomResponse(
            diagnosis=condition["name"],
            confidence=kb_match.confidence,
            severity=Severity(condition["severity"]),
            source=AnalysisSource.KNOWLEDGE_BASE,
            symptoms=condition.get("symptoms", []),
            recommendations=condition.get("recommendations", []),
            when_to_see_doctor=condition.get("when_to_see_doctor", ""),
            disclaimer=kb.disclaimer,
        )
        logger.info(
            "KB match: %s (confidence=%.4f, source=knowledge_base)",
            condition["name"],
            kb_match.confidence,
        )
        _set_cached_result(cache_key, response.model_dump(mode="json"))
        if current_user:
            await _save_to_history(db, current_user.id, query, response)
        return response

    # ── Step 3: Fall back to AI model ────────────────────────
    classification = await classifier.classify(query)

    if classification and classification.confidence > 0.3:
        kb_id = classifier.get_kb_id_for_label(classification.label)
        condition_data = None
        if kb_id:
            for c in kb._conditions if kb._loaded else []:
                if c["id"] == kb_id:
                    condition_data = c
                    break

        if condition_data:
            response = SymptomResponse(
                diagnosis=condition_data["name"],
                confidence=classification.confidence,
                severity=Severity(condition_data["severity"]),
                source=AnalysisSource.AI_MODEL,
                symptoms=condition_data.get("symptoms", []),
                recommendations=condition_data.get("recommendations", []),
                when_to_see_doctor=condition_data.get("when_to_see_doctor", ""),
                disclaimer=kb.disclaimer,
            )
        else:
            response = SymptomResponse(
                diagnosis=classification.label.title(),
                confidence=classification.confidence,
                severity=Severity.UNKNOWN,
                source=AnalysisSource.AI_MODEL,
                symptoms=[],
                recommendations=["Please consult a healthcare professional for proper evaluation"],
                when_to_see_doctor="If symptoms persist or worsen, see a doctor.",
                disclaimer=kb.disclaimer,
            )

        logger.info(
            "AI match: %s (confidence=%.4f, source=ai_model)",
            response.diagnosis,
            classification.confidence,
        )
        _set_cached_result(cache_key, response.model_dump(mode="json"))
        if current_user:
            await _save_to_history(db, current_user.id, query, response)
        return response

    # ── Step 4: Fallback — no confident match ────────────────
    fallback = kb.get_fallback()
    response = SymptomResponse(
        diagnosis=fallback.get("name", "General Health Inquiry"),
        confidence=0.35,
        severity=Severity.UNKNOWN,
        source=AnalysisSource.FALLBACK,
        symptoms=[],
        recommendations=fallback.get("recommendations", []),
        when_to_see_doctor=fallback.get("when_to_see_doctor", ""),
        disclaimer=kb.disclaimer,
    )
    logger.info("No confident match — returning fallback response")
    if current_user:
        await _save_to_history(db, current_user.id, query, response)
    return response


@router.get("/conditions")
async def list_conditions(
    kb: KnowledgeBaseService = Depends(get_kb_service),
) -> dict:
    """List all conditions available in the knowledge base."""
    return {
        "status": "success",
        "data": {
            "conditions": kb.list_conditions(),
            "total": kb.condition_count,
        },
    }
