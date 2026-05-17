"""
Authentication Router.

Endpoints:
  POST /api/v1/auth/register  — Create a new user account
  POST /api/v1/auth/login     — Authenticate and receive JWT tokens
  GET  /api/v1/auth/me        — Get current authenticated user profile
"""

import logging
import re

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ValidationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.models.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
logger = logging.getLogger(__name__)


# ── Request / Response Schemas ───────────────────────────────

class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=255, examples=["user@example.com"])
    username: str = Field(..., min_length=3, max_length=50, examples=["johndoe"])
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower().strip()

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return v.strip()

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginRequest(BaseModel):
    email: str = Field(..., examples=["user@example.com"])
    password: str = Field(...)


class AuthResponse(BaseModel):
    status: str = "success"
    data: dict


class UserProfile(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    created_at: str


# ── Endpoints ────────────────────────────────────────────────

@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user account.

    Returns access and refresh tokens on successful registration.
    """
    # Check for existing email
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none():
        raise ConflictError(f"Email '{body.email}' is already registered")

    # Check for existing username
    result = await db.execute(select(User).where(User.username == body.username))
    if result.scalar_one_or_none():
        raise ConflictError(f"Username '{body.username}' is already taken")

    # Create user
    user = User(
        email=body.email,
        username=body.username,
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    await db.flush()  # Generate the user ID

    logger.info("User registered: %s (%s)", user.username, user.email)

    return AuthResponse(
        data={
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
            },
            "access_token": create_access_token(user.id),
            "refresh_token": create_refresh_token(user.id),
            "token_type": "bearer",
        }
    )


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate with email and password.

    Returns access and refresh tokens on successful login.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == body.email.lower().strip()))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(body.password, user.hashed_password):
        # Intentionally vague — don't reveal whether email exists
        raise ValidationError("Invalid email or password")

    if not user.is_active:
        raise ValidationError("Account has been deactivated")

    logger.info("User logged in: %s", user.email)

    return AuthResponse(
        data={
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
            },
            "access_token": create_access_token(user.id),
            "refresh_token": create_refresh_token(user.id),
            "token_type": "bearer",
        }
    )


@router.get("/me")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return {
        "status": "success",
        "data": {
            "id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at.isoformat(),
        },
    }
