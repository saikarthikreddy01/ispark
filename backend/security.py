"""Small authentication helpers for the AcadGraph prototype.

The browser stores no identity or role. Password verification happens only on
the server and the authenticated identity is carried by a signed, HTTP-only
session cookie.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
from pathlib import Path
from typing import Any, Dict, Optional


PASSWORD_SCHEME = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 260_000
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def hash_password(password: str) -> str:
    """Create a salted PBKDF2 hash using Python's standard library."""
    if not password:
        raise ValueError("Password cannot be empty")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    return f"{PASSWORD_SCHEME}${PASSWORD_ITERATIONS}${_encode(salt)}${_encode(digest)}"


def verify_password(password: str, encoded: str) -> bool:
    """Verify a password without leaking timing information."""
    try:
        scheme, rounds, salt, expected = encoded.split("$", 3)
        if scheme != PASSWORD_SCHEME:
            return False
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), _decode(salt), int(rounds)
        )
        return hmac.compare_digest(actual, _decode(expected))
    except (AttributeError, TypeError, ValueError):
        return False


def get_session_secret() -> str:
    """Read the signing key from the environment, with a development fallback.

    Render should define SESSION_SECRET. The random fallback keeps local setup
    simple, but intentionally expires sessions whenever the process restarts.
    """
    configured = os.getenv("SESSION_SECRET", "").strip()
    if configured:
        return configured
    return secrets.token_urlsafe(48)


def load_faculty_account(username: str) -> Optional[Dict[str, Any]]:
    """Load a faculty account from data, optionally overridden by environment.

    FACULTY_USERNAME and FACULTY_PASSWORD_HASH provide a simple deployment
    override without placing a plaintext password in source control.
    """
    normalized = username.strip().lower()
    env_username = os.getenv("FACULTY_USERNAME", "").strip().lower()
    env_hash = os.getenv("FACULTY_PASSWORD_HASH", "").strip()
    if env_username and env_hash and hmac.compare_digest(normalized, env_username):
        return {
            "username": env_username,
            "password_hash": env_hash,
            "role": "FACULTY",
            "title": os.getenv("FACULTY_TITLE", "Academic Faculty Advisor"),
            "department": os.getenv("FACULTY_DEPARTMENT", "Computer Science & Engineering"),
            "institution": os.getenv("FACULTY_INSTITUTION", "VFSTR (Deemed to be University)"),
        }

    path = DATA_DIR / "faculty_accounts.json"
    try:
        accounts = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    for account in accounts:
        if hmac.compare_digest(str(account.get("username", "")).lower(), normalized):
            return account
    return None


def public_faculty(account: Dict[str, Any]) -> Dict[str, Any]:
    """Return faculty identity metadata without credential material."""
    return {
        key: account.get(key)
        for key in ("username", "role", "title", "department", "institution")
    }
