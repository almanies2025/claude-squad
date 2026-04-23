"""Auth API: register, login, TOTP setup and verify."""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Firm, User
from app.dependencies import get_current_user
from app.domain.entities import (
    FirmCreate,
    Token,
    UserCreate,
    UserLogin,
)
from app.core.security import (
    create_access_token,
    generate_totp_secret,
    hash_password,
    totp_provisioning_uri,
    verify_password,
    verify_totp,
)

# In-memory rate limiter: per-IP attempt counter with 15-minute window.
# For production, replace with Redis-backed rate limiting.
_RATE_LIMIT: dict[str, list[float]] = {}
_RATE_WINDOW = 900  # 15 minutes
_RATE_MAX = 10  # max attempts per window


def _check_rate_limit(client_ip: str) -> None:
    """Raise 429 if IP has exceeded login rate limit."""
    now = time.time()
    if client_ip not in _RATE_LIMIT:
        _RATE_LIMIT[client_ip] = []
    # Remove old entries outside the window
    _RATE_LIMIT[client_ip] = [t for t in _RATE_LIMIT[client_ip] if now - t < _RATE_WINDOW]
    if len(_RATE_LIMIT[client_ip]) >= _RATE_MAX:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again in 15 minutes.",
        )
    _RATE_LIMIT[client_ip].append(now)


router = APIRouter()


# ── POST /auth/register ─────────────────────────────────────────────────────────


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    firm_data: FirmCreate,
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db),
):
    """
    Register a new firm and its first user.

    Creates the Firm, then the User (hashed password). If totp_enabled is True
    on the user, a TOTP secret is generated but must be verified separately via
    POST /auth/totp/verify before it is activated.
    """
    # Check email uniqueness
    existing = await session.execute(select(User).where(User.email == user_data.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    # Create firm
    firm = Firm(
        id=uuid.uuid4(),
        name=firm_data.name,
        timezone=firm_data.timezone,
        subscription_status="trial",
    )
    session.add(firm)

    # Create user
    hashed_pw = hash_password(user_data.password)

    user = User(
        id=uuid.uuid4(),
        firm_id=firm.id,
        email=user_data.email,
        hashed_password=hashed_pw,
        name=user_data.name,
        role=user_data.role,
        totp_secret=None,
        totp_enabled=False,
        is_active=True,
    )
    session.add(user)
    await session.flush()
    await session.commit()

    token = create_access_token(str(user.id))
    return Token(access_token=token, token_type="bearer")


# ── POST /auth/login ─────────────────────────────────────────────────────────────


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    """
    Authenticate with email + password. If the user has TOTP enabled, the
    response indicates that a TOTP code is required — the client must then call
    POST /auth/totp/verify to obtain the final JWT.

    Rate-limited to 10 attempts per IP per 15 minutes.
    """
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)
    result = await session.execute(select(User).where(User.email == credentials.email))
    user: User | None = result.scalar_one_or_none()

    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # If TOTP is enabled, require second factor
    if user.totp_enabled and user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="TOTP required",
            headers={"X-TOTP-Required": "true", "X-User-Id": str(user.id)},
        )

    token = create_access_token(str(user.id))
    return Token(access_token=token, token_type="bearer")


# ── POST /auth/totp/setup ────────────────────────────────────────────────────────


@router.post("/totp/setup", response_model=dict)
async def totp_setup(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Generate a new TOTP secret for the authenticated user.

    Returns the provisioning URI (otpauth://) for use with an authenticator app.
    The secret is NOT yet active — the user must verify a code via POST /auth/totp/verify.
    """
    new_secret = generate_totp_secret()
    user.totp_secret = new_secret
    await session.flush()

    uri = totp_provisioning_uri(new_secret, user.email)
    # Mask secret: return only first 4 and last 4 chars
    masked = f"{new_secret[:4]}...{new_secret[-4:]}"
    return {
        "totp_secret_masked": masked,
        "provisioning_uri": uri,
        "message": "Verify a code to activate TOTP. Store the full secret securely — it is not stored server-side.",
    }


# ── Local request model for TOTP verify ───────────────────────────────────────


class TOTPVerifyRequest(BaseModel):
    """Request body for POST /auth/totp/verify — code + user_id from 403 response."""

    code: str
    user_id: str


# ── POST /auth/totp/verify ───────────────────────────────────────────────────────


@router.post("/totp/verify", response_model=Token)
async def totp_verify(
    payload: TOTPVerifyRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    """
    Verify a TOTP code for a user whose account has TOTP enabled.

    After a 403 from /auth/login, the client receives X-User-Id. It should
    present that ID here along with the 6-digit code from the authenticator app.
    Returns a fresh JWT on success.

    Rate-limited to 20 attempts per IP per 15 minutes.
    """
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)
    try:
        user_id = uuid.UUID(payload.user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id format"
        )

    result = await session.execute(select(User).where(User.id == user_id))
    user: User | None = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user.totp_enabled or not user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TOTP is not enabled for this user",
        )

    if not verify_totp(user.totp_secret, payload.code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code",
        )

    token = create_access_token(str(user.id))
    return Token(access_token=token, token_type="bearer")
