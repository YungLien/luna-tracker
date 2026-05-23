import os


def _env(name: str) -> str:
    """Read env var; strip whitespace and optional surrounding quotes (Railway raw editor)."""
    val = (os.getenv(name) or "").strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
        val = val[1:-1].strip()
    return val


def frontend_base_url() -> str:
    """Where to send the browser after Strava OAuth (no trailing slash)."""
    explicit = _env("FRONTEND_URL").rstrip("/")
    if explicit:
        return explicit

    # If FRONTEND_URL missing in Railway, use first https origin from CORS list.
    for origin in _env("ALLOWED_ORIGINS").split(","):
        origin = origin.strip().rstrip("/")
        if origin.startswith("https://"):
            return origin

    return "http://localhost:5173"


def public_config_status() -> dict:
    """Safe snapshot for /health — verify production env without exposing secrets."""
    redirect = _env("STRAVA_REDIRECT_URI")
    return {
        "frontend_url_env_set": bool(_env("FRONTEND_URL")),
        "frontend_redirect_base": frontend_base_url(),
        "strava_redirect_uri": redirect,
        "strava_redirect_uses_localhost": "localhost" in redirect,
        "allowed_origins": _env("ALLOWED_ORIGINS"),
    }
