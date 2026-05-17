"""
Symptom History Router.

Endpoints:
  GET  /api/v1/history          — List authenticated user's query history (paginated)
  GET  /api/v1/history/{id}     — Get a single history entry
  DELETE /api/v1/history/{id}   — Delete a single history entry
  DELETE /api/v1/history        — Clear all history for the current user
"""

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError, NotFoundError
from app.core.security import get_current_user
from app.database import get_db
from app.models.symptom_query import SymptomQuery
from app.models.user import User

router = APIRouter(prefix="/api/v1/history", tags=["history"])
logger = logging.getLogger(__name__)


@router.get("")
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, le=50, description="Results per page"),
):
    """List the current user's symptom query history, newest first.

    Returns paginated results with total count for frontend pagination.
    """
    offset = (page - 1) * limit

    # Get total count
    count_result = await db.execute(
        select(SymptomQuery).where(SymptomQuery.user_id == current_user.id)
    )
    total = len(count_result.scalars().all())

    # Get paginated records
    result = await db.execute(
        select(SymptomQuery)
        .where(SymptomQuery.user_id == current_user.id)
        .order_by(SymptomQuery.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    queries = result.scalars().all()

    return {
        "status": "success",
        "data": {
            "history": [_serialize_query(q) for q in queries],
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit,
            },
        },
    }


@router.get("/{query_id}")
async def get_history_entry(
    query_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single symptom history entry by ID."""
    result = await db.execute(
        select(SymptomQuery).where(SymptomQuery.id == query_id)
    )
    query = result.scalar_one_or_none()

    if query is None:
        raise NotFoundError("SymptomQuery", query_id)

    # Only the owner can access their own records
    if query.user_id != current_user.id:
        raise AuthorizationError("You do not have access to this record")

    return {"status": "success", "data": _serialize_query(query)}


@router.delete("/{query_id}", status_code=204)
async def delete_history_entry(
    query_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a single symptom history entry by ID."""
    result = await db.execute(
        select(SymptomQuery).where(SymptomQuery.id == query_id)
    )
    query = result.scalar_one_or_none()

    if query is None:
        raise NotFoundError("SymptomQuery", query_id)

    if query.user_id != current_user.id:
        raise AuthorizationError("You do not have access to this record")

    await db.delete(query)
    logger.info("History entry %s deleted by user %s", query_id, current_user.id)


@router.delete("", status_code=204)
async def clear_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete ALL symptom history for the current user."""
    await db.execute(
        delete(SymptomQuery).where(SymptomQuery.user_id == current_user.id)
    )
    logger.info("All history cleared for user %s", current_user.id)


def _serialize_query(q: SymptomQuery) -> dict:
    """Convert a SymptomQuery ORM object to a serializable dict."""
    return {
        "id": q.id,
        "symptoms_text": q.symptoms_text,
        "diagnosis": q.diagnosis,
        "confidence": q.confidence,
        "severity": q.severity,
        "source": q.source,
        "created_at": q.created_at.isoformat(),
    }
