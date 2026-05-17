"""
Pydantic Schemas for Request/Response Validation.

Defines the data contracts for the API. FastAPI uses these for:
  - Automatic request body validation
  - Response serialization
  - OpenAPI documentation generation
  - Type safety across the application
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


# ── Enums ────────────────────────────────────────────────────

class Severity(str, Enum):
    """Condition severity levels."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    UNKNOWN = "unknown"


class AnalysisSource(str, Enum):
    """Indicates how the result was determined."""
    KNOWLEDGE_BASE = "knowledge_base"
    AI_MODEL = "ai_model"
    FALLBACK = "fallback"


# ── Symptom Schemas ──────────────────────────────────────────

class SymptomRequest(BaseModel):
    """Request body for symptom analysis."""

    symptoms: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description="Description of symptoms in natural language",
        examples=["I have a headache and feel dizzy"],
    )

    @field_validator("symptoms")
    @classmethod
    def sanitize_symptoms(cls, v: str) -> str:
        """Strip HTML tags and normalize whitespace."""
        import re
        # Remove HTML tags
        cleaned = re.sub(r"<[^>]+>", "", v)
        # Normalize whitespace
        cleaned = " ".join(cleaned.split())
        return cleaned.strip()


class SymptomResponse(BaseModel):
    """Response body for symptom analysis."""

    diagnosis: str = Field(
        ...,
        description="Matched condition name",
        examples=["Tension Headache / Migraine"],
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0-1) from the analysis",
        examples=[0.87],
    )
    severity: Severity = Field(
        ...,
        description="Condition severity level",
    )
    source: AnalysisSource = Field(
        ...,
        description="Whether the result came from knowledge base or AI model",
    )
    symptoms: list[str] = Field(
        default_factory=list,
        description="Common symptoms for the matched condition",
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Actionable health recommendations",
    )
    when_to_see_doctor: str = Field(
        default="",
        description="Guidance on when to seek professional medical help",
    )
    disclaimer: str = Field(
        default="This is educational health information, not medical advice. Consult a healthcare professional.",
        description="Medical disclaimer",
    )


# ── Common Response Wrappers ─────────────────────────────────

class MetaInfo(BaseModel):
    """Metadata included in every API response."""
    request_id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(BaseModel):
    """Standard success response wrapper."""
    status: str = "success"
    data: dict | list | None = None
    meta: MetaInfo = Field(default_factory=MetaInfo)


class ErrorDetail(BaseModel):
    """Error information in error responses."""
    code: str
    message: str
    details: dict | list | None = None


class ErrorResponse(BaseModel):
    """Standard error response wrapper."""
    status: str = "error"
    error: ErrorDetail
    meta: MetaInfo = Field(default_factory=MetaInfo)
