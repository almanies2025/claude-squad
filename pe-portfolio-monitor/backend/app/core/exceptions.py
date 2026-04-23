"""Domain exceptions for the API layer."""

from __future__ import annotations


class AppException(Exception):
    """Base exception for application-level errors."""

    def __init__(self, message: str, *, code: str | None = None):
        self.message = message
        self.code = code or "app_error"
        super().__init__(message)


class NotFoundException(AppException):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, code="not_found")


class ForbiddenException(AppException):
    """Action forbidden — typically tenant or permission violation."""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, code="forbidden")


class ConflictException(AppException):
    """Resource already exists (e.g., duplicate email)."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, code="conflict")


class ValidationException(AppException):
    """Request validation failed."""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, code="validation_error")
