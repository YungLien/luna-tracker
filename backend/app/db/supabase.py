from supabase import create_client, Client
from dotenv import load_dotenv

from app.config import _env

load_dotenv()

_client: Client | None = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        url = _env("SUPABASE_URL")
        key = _env("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        _client = create_client(url, key)
    return _client


def check_supabase_connection() -> dict:
    """Safe probe for /health — no secrets in response."""
    url = _env("SUPABASE_URL")
    key = _env("SUPABASE_SERVICE_KEY")
    info = {
        "supabase_url_set": bool(url),
        "supabase_service_key_set": bool(key),
        "supabase_service_key_length": len(key),
        "supabase_service_key_prefix_ok": key.startswith("sb_secret_") or key.startswith("eyJ"),
    }
    if not url or not key:
        info["supabase_ok"] = False
        info["supabase_hint"] = "Set SUPABASE_URL and SUPABASE_SERVICE_KEY on Railway."
        return info
    try:
        get_supabase().table("users").select("id").limit(1).execute()
        info["supabase_ok"] = True
        info["supabase_hint"] = "Database reachable."
    except Exception as exc:
        info["supabase_ok"] = False
        info["supabase_hint"] = str(exc)[:240]
    return info
