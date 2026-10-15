"""Public profile URL checks with conservative request handling."""

from __future__ import annotations

import re
import time
from typing import Any
from urllib.parse import quote

import requests

# Keep this list small and easy to review. Sites may block automated requests
# or change their routing; a response is not definitive proof of account status.
DEFAULT_PLATFORMS: dict[str, str] = {
    "github": "https://github.com/{username}",
    "gitlab": "https://gitlab.com/{username}",
    "reddit": "https://www.reddit.com/user/{username}/",
    "medium": "https://medium.com/@{username}",
    "keybase": "https://keybase.io/{username}",
    "instagram": "https://www.instagram.com/{username}/"
}

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{1,39}$")


def validate_username(username: str) -> str:
    """Validate a username-like string to prevent malformed input and URL injection."""
    value = username.strip()
    if not USERNAME_RE.fullmatch(value):
        raise ValueError(
            "Username must be 1–39 characters and contain only letters, numbers, dots, underscores, or hyphens."
        )
    return value


def check_profile(
    username: str,
    platform: str,
    session: requests.Session,
    timeout: float = 8.0,
) -> dict[str, Any]:
    """Request one curated public profile URL and classify the HTTP response cautiously."""
    if platform not in DEFAULT_PLATFORMS:
        raise ValueError(f"Unknown platform: {platform}")

    safe_username = quote(validate_username(username), safe="._-")
    url = DEFAULT_PLATFORMS[platform].format(username=safe_username)
    result: dict[str, Any] = {
        "platform": platform,
        "url": url,
        "status": "unknown",
        "http_status": None,
        "final_url": None,
        "error": None,
    }

    try:
        # GET is used because some sites respond differently to HEAD requests.
        # Do not follow arbitrary user-provided URLs; targets come from our allowlist.
        response = session.get(url, timeout=timeout, allow_redirects=True)
        result["http_status"] = response.status_code
        result["final_url"] = response.url

        if response.status_code == 200:
            result["status"] = "http_200_review_needed"
        elif response.status_code == 404:
            result["status"] = "http_404_not_found"
        elif response.status_code in (401, 403, 429):
            result["status"] = "blocked_or_rate_limited"
        elif 300 <= response.status_code < 400:
            result["status"] = "redirect"
        else:
            result["status"] = "http_response"
        response.close()
    except requests.Timeout:
        result["status"] = "error"
        result["error"] = "timeout"
    except requests.RequestException as exc:
        # Keep reports concise; do not include request internals or local paths.
        result["status"] = "error"
        result["error"] = type(exc).__name__

    return result
