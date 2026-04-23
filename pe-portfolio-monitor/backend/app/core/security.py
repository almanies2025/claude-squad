"""Security utilities: password hashing, TOTP, and JWT."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

import pyotp
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def generate_totp_secret() -> str:
    """Generate a random 32-character base32 TOTP secret."""
    return pyotp.random_base32(length=32)


def verify_totp(secret: str, code: str) -> bool:
    """Verify a 6-digit TOTP code against the stored secret."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


def totp_provisioning_uri(secret: str, email: str) -> str:
    """Generate an otpauth:// provisioning URI for authenticator apps."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=settings.TOTP_ISSUER)


def create_access_token(user_id: str, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Decode and validate a JWT access token. Returns payload or None if invalid."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
