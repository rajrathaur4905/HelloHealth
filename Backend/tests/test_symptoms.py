"""
Symptom Check Endpoint Tests.

Verifies the POST /api/v1/symptoms/check endpoint for:
  1. Valid input returns 200 with analysis results
  2. Empty/missing input returns 422 validation error
  3. Response contains all required fields (diagnosis, confidence, severity, source)
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_symptom_check_valid_input(client: AsyncClient):
    """POST /api/v1/symptoms/check with a valid symptom string should return 200.

    Uses a well-known symptom ('headache') that the knowledge base
    can match without needing the AI model.
    """
    response = await client.post(
        "/api/v1/symptoms/check",
        json={"symptoms": "I have a bad headache and feel dizzy"},
    )
    assert response.status_code == 200

    data = response.json()
    assert "diagnosis" in data
    assert "confidence" in data


@pytest.mark.asyncio
async def test_symptom_check_empty_input_returns_422(client: AsyncClient):
    """POST /api/v1/symptoms/check with empty symptoms should return 422.

    The SymptomRequest schema requires min_length=2, so an empty
    string violates validation and FastAPI returns 422 Unprocessable Entity.
    """
    response = await client.post(
        "/api/v1/symptoms/check",
        json={"symptoms": ""},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_symptom_check_response_has_required_fields(client: AsyncClient):
    """The symptom check response must include all required fields.

    Required fields (from SymptomResponse schema):
      - diagnosis: str
      - confidence: float (0-1)
      - severity: one of mild/moderate/severe/unknown
      - source: one of knowledge_base/ai_model/fallback
      - disclaimer: str (medical disclaimer)
    """
    response = await client.post(
        "/api/v1/symptoms/check",
        json={"symptoms": "I have a sore throat and cough"},
    )
    assert response.status_code == 200

    data = response.json()

    # All required fields must be present
    required_fields = ["diagnosis", "confidence", "severity", "source", "disclaimer"]
    for field in required_fields:
        assert field in data, f"Missing required field: '{field}'"

    # Confidence must be between 0 and 1
    assert 0.0 <= data["confidence"] <= 1.0, (
        f"Confidence {data['confidence']} is out of range [0, 1]"
    )

    # Severity must be a valid enum value
    valid_severities = ["mild", "moderate", "severe", "unknown"]
    assert data["severity"] in valid_severities, (
        f"Invalid severity: '{data['severity']}'"
    )

    # Source must be a valid enum value
    valid_sources = ["knowledge_base", "ai_model", "fallback"]
    assert data["source"] in valid_sources, (
        f"Invalid source: '{data['source']}'"
    )

    # Disclaimer must be non-empty
    assert len(data["disclaimer"]) > 0, "Disclaimer should not be empty"
