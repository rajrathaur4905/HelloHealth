"""
Security Utilities — JWT Tokens and Password Hashing.

Provides core authentication primitives used by the auth router:
  - Password hashing/verification via bcrypt
  - JWT access/refresh token creation and decoding
  - FastAPI dependency for extracting the current user from a request
"""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import AuthenticationError
from app.database import get_db

logger = logging.getLogger(__name__)

# ── Password Hashing ────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain-text password with bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT Token Management ────────────────────────────────────

def create_access_token(user_id: str) -> str:
    """Create a short-lived access token (default: 30 minutes)."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Create a long-lived refresh token (default: 7 days)."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token. Raises AuthenticationError on failure."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("sub") is None:
            raise AuthenticationError("Token missing subject claim")
        return payload
    except JWTError as e:
        logger.warning("JWT decode failed: %s", e)
        raise AuthenticationError("Invalid or expired token")


# ── FastAPI Dependencies ─────────────────────────────────────

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Extract and validate the current user from the JWT in the Authorization header.

    Usage in routes:
        @router.get("/me")
        async def me(user: User = Depends(get_current_user)):
            return user
    """
    if credentials is None:
        raise AuthenticationError("Authorization header required")

    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")

    # Import here to avoid circular imports
    from app.models.user import User

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise AuthenticationError("User not found")
    if not user.is_active:
        raise AuthenticationError("User account is deactivated")

    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Like get_current_user but returns None instead of raising for unauthenticated requests.

    Useful for endpoints that work for both anonymous and authenticated users
    (e.g., symptom check saves history only for logged-in users).
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials, db)
    except AuthenticationError:
        return None
