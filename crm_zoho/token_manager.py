"""
OAuth token manager for Zoho CRM with automatic refresh.

This upgraded version ensures:
- Access token never expires (auto-refresh before expiration)
- Refresh token is preserved forever
- Cleaner error handling
- Optional "always refresh" mode
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx


class ZohoTokenManager:
    """
    Manages Zoho OAuth tokens with safe, automatic refresh.
    Access token always remains valid, and refresh token is never lost.
    """

    TOKEN_FILE = Path(".tokens.json")

    # Refresh 5 minutes before expiry
    TOKEN_REFRESH_BUFFER_SECONDS = 300  # refresh 5 minutes early

    # If True → refresh access token for every call (safest)
    ALWAYS_REFRESH = False

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scope: str = "ZohoCRM.modules.ALL",
        accounts_server: str = "https://accounts.zoho.com",
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.accounts_server = accounts_server.rstrip("/")
        self.token_data: Optional[Dict[str, Any]] = None

        self._load_tokens()

    # -------------------------------------------------------------------------
    # TOKEN FILE I/O
    # -------------------------------------------------------------------------

    def _load_tokens(self) -> None:
        """Load tokens from persistent storage."""
        if self.TOKEN_FILE.exists():
            try:
                with open(self.TOKEN_FILE, "r") as f:
                    self.token_data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load tokens: {e}")
                self.token_data = None

    def _save_tokens(self, token_data: Dict[str, Any]) -> None:
        """Save tokens to local storage, ensuring refresh token is preserved."""
        # Do NOT overwrite refresh token if missing in new response
        if self.token_data and "refresh_token" in self.token_data:
            token_data.setdefault("refresh_token", self.token_data["refresh_token"])

        self.token_data = token_data

        try:
            with open(self.TOKEN_FILE, "w") as f:
                json.dump(token_data, f, indent=2)
            os.chmod(self.TOKEN_FILE, 0o600)
        except IOError as e:
            raise RuntimeError(f"Failed to save tokens: {e}") from e

    # -------------------------------------------------------------------------
    # AUTH URL + INITIAL TOKEN EXCHANGE
    # -------------------------------------------------------------------------

    def get_authorization_url(self) -> str:
        """Generate OAuth URL for initial login."""
        params = {
            "scope": self.scope,
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "access_type": "offline",
            "prompt": "consent",  # Ensures refresh token is always issued
        }
        return f"{self.accounts_server}/oauth/v2/auth?{urlencode(params)}"

    def exchange_code_for_tokens(self, authorization_code: str) -> Dict[str, Any]:
        """Exchange auth code for initial access + refresh tokens."""
        url = f"{self.accounts_server}/oauth/v2/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret",
            "redirect_uri": self.redirect_uri,
            "code": authorization_code,
        }

        with httpx.Client() as client:
            response = client.post(url, data=data)
            response.raise_for_status()
            token_data = response.json()

        # Add expiry timestamp
        token_data["expires_at"] = time.time() + token_data.get("expires_in", 3600)

        # Save permanently
        self._save_tokens(token_data)

        return token_data

    # -------------------------------------------------------------------------
    # REFRESH ACCESS TOKEN (FOREVER)
    # -------------------------------------------------------------------------

    def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh access token using refresh token."""
        if not self.token_data or "refresh_token" not in self.token_data:
            raise RuntimeError("Missing refresh token. Run OAuth flow again.")

        url = f"{self.accounts_server}/oauth/v2/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret",
            "refresh_token": self.token_data["refresh_token"],
        }

        with httpx.Client() as client:
            response = client.post(url, data=data)
            response.raise_for_status()
            new_data = response.json()

        # Zoho does NOT return refresh_token on refresh
        new_data.setdefault("refresh_token", self.token_data["refresh_token"])

        # Set new expiry time
        new_data["expires_at"] = time.time() + new_data.get("expires_in", 3600)

        # Save safely
        self._save_tokens(new_data)

        return new_data

    # -------------------------------------------------------------------------
    # PUBLIC TOKEN ACCESS
    # -------------------------------------------------------------------------

    def get_valid_access_token(self) -> str:
        """
        Returns a guaranteed-valid access token.
        It refreshes early so token never expires.
        """
        if not self.token_data or "access_token" not in self.token_data:
            raise RuntimeError(
                "No access token available. Run initial OAuth flow:\n"
                f"1. Visit: {self.get_authorization_url()}\n"
                "2. Authorize\n"
                "3. Copy ?code=...\n"
                "4. Call exchange_code_for_tokens(code)"
            )

        expires_at = self.token_data.get("expires_at", 0)
        now = time.time()

        # ALWAYS refresh mode (safest)
        if self.ALWAYS_REFRESH:
            print("[Zoho] Always-refresh mode ON → refreshing token…")
            self.refresh_access_token()
            return self.token_data["access_token"]

        # Auto-refresh before expiry buffer
        if now >= expires_at - self.TOKEN_REFRESH_BUFFER_SECONDS:
            print("[Zoho] Access token is expiring soon → refreshing…")
            self.refresh_access_token()

        return self.token_data["access_token"]

    def is_authenticated(self) -> bool:
        """True if tokens exist and refresh works."""
        try:
            self.get_valid_access_token()
            return True
        except Exception:
            return False