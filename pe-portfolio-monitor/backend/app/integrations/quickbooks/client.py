"""QuickBooks Online OAuth2 client scaffold.

This module provides a minimal OAuth2 authorization_code flow implementation
for QuickBooks Online API integration. All token exchange methods are stubs
that return mock data — no real Intuit API calls are made.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx
from pydantic import BaseModel, Field


class QBOAuthError(Exception):
    """Raised when a QuickBooks OAuth2 operation fails."""

    def __init__(self, message: str, *, code: str | None = None, status_code: int | None = None):
        self.message = message
        self.code = code or "qbo_auth_error"
        self.status_code = status_code
        super().__init__(message)


class QBOConnection(BaseModel):
    """Represents a QuickBooks Online OAuth2 connection.

    Attributes:
        company_id: The QBO Company ID (realm ID).
        company_name: Human-readable company name from QBO API.
        access_token: Current OAuth2 access token.
        refresh_token: OAuth2 refresh token for obtaining new access tokens.
        token_expires_at: UTC timestamp when the access token expires.
        environment: "sandbox" or "production".
    """

    company_id: str
    company_name: str
    access_token: str
    refresh_token: str
    token_expires_at: datetime
    environment: str = Field(pattern=r"^(sandbox|production)$")


class QBOOAuthClient:
    """Minimal QuickBooks Online OAuth2 client.

    Implements the authorization_code flow using Intuit's OAuth2 endpoints.
    All token-related methods return mock data until real credentials are
    provisioned.

    Args:
        client_id: OAuth2 client ID from Intuit Developer.
        client_secret: OAuth2 client secret from Intuit Developer.
        redirect_uri: Callback URL registered in Intuit Developer dashboard.
        environment: "sandbox" for testing or "production" for live data.
    """

    AUTHORIZATION_URL = "https://appcenter.intuit.com/connect/oauth2"
    TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    COMPANY_INFO_URL = "https://quickbooks.api.intuit.com/v3/company"

    SANDBOX_AUTH_URL = "https://appcenter.intuit.com/connect/oauth2"
    SANDBOX_API_URL = "https://sandbox-quickbooks.api.intuit.com/v3/company"

    SCOPE = "com.intuit.quickbooks.accounting"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        environment: str = "sandbox",
    ) -> None:
        if environment not in ("sandbox", "production"):
            raise QBOAuthError(
                f"Invalid environment: {environment}. Must be 'sandbox' or 'production'.",
                code="invalid_environment",
            )
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.environment = environment

    def _base_url(self) -> str:
        """Return the appropriate API base URL for the current environment."""
        if self.environment == "sandbox":
            return self.SANDBOX_API_URL
        return self.COMPANY_INFO_URL

    def _auth_url_base(self) -> str:
        """Return the appropriate authorization URL for the current environment."""
        if self.environment == "sandbox":
            return self.SANDBOX_AUTH_URL
        return self.AUTHORIZATION_URL

    def _build_auth_header(self, token: str) -> dict[str, str]:
        """Build the Authorization header for QBO API requests.

        Args:
            token: A valid OAuth2 access token.

        Returns:
            Dictionary with Authorization and Accept headers.
        """
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

    def authorize_url(self, state: str) -> str:
        """Build the Intuit OAuth2 authorization URL.

        Redirect the user to this URL to begin the authorization_code flow.
        After approval, Intuit redirects back to ``redirect_uri`` with a
        ``code`` query parameter.

        Args:
            state: An opaque string used to maintain state between the
                authorization request and callback. Typically a random
                token validated on callback to prevent CSRF attacks.

        Returns:
            The fully constructed authorization URL.
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.SCOPE,
            "response_type": "code",
            "state": state,
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self._auth_url_base()}?{query}"

    async def exchange_code(self, code: str) -> dict[str, Any]:
        """Exchange an authorization code for access/refresh tokens.

        This is a stub — it returns mock tokens without calling Intuit.

        Args:
            code: The authorization code received at the redirect URI.

        Returns:
            A dictionary containing ``access_token``, ``refresh_token``,
            and ``expires_in`` fields.
        """
        return {
            "access_token": "mock",
            "refresh_token": "mock",
            "expires_in": 3600,
            "token_type": "Bearer",
            "x_refresh_token_expires_in": 8726400,
        }

    async def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh an expired access token using a refresh token.

        This is a stub — it returns mock refreshed tokens without calling Intuit.

        Args:
            refresh_token: The refresh token from a previous token exchange.

        Returns:
            A dictionary containing a new ``access_token``,
            ``refresh_token``, and ``expires_in`` fields.
        """
        return {
            "access_token": "mock_refreshed",
            "refresh_token": "mock_refreshed",
            "expires_in": 3600,
            "token_type": "Bearer",
            "x_refresh_token_expires_in": 8726400,
        }

    async def get_company_info(self, access_token: str) -> dict[str, Any]:
        """Fetch the company information for the authenticated company.

        This is a stub — it returns static mock data without calling Intuit.

        Args:
            access_token: A valid OAuth2 access token.

        Returns:
            A dictionary with ``company_name``, ``company_id``,
            and ``fiscal_year_start_month`` fields.
        """
        return {
            "company_name": "Acme Portfolio Co",
            "company_id": "qb_company_001",
            "fiscal_year_start_month": 1,
        }

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self.aclose()

    async def aclose(self) -> None:
        """Alias for close(), for explicit async lifecycle management."""
        pass
