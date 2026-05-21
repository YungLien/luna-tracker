-- Luna Tracker: lock down public API access (Supabase Security Advisor)
--
-- Run once in Supabase Dashboard → SQL Editor → New query → Run
--
-- Architecture: only the FastAPI backend uses SUPABASE_SERVICE_KEY (bypasses RLS).
-- The browser never talks to Supabase directly. With RLS on and no permissive
-- policies, anon/authenticated roles cannot read or write any rows via PostgREST.

-- ── users (contains Strava OAuth tokens — highest sensitivity) ─────────────
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- ── meals ───────────────────────────────────────────────────────────────────
ALTER TABLE public.meals ENABLE ROW LEVEL SECURITY;

-- ── activities ──────────────────────────────────────────────────────────────
ALTER TABLE public.activities ENABLE ROW LEVEL SECURITY;

-- ── daily_summaries ─────────────────────────────────────────────────────────
ALTER TABLE public.daily_summaries ENABLE ROW LEVEL SECURITY;

-- Optional hardening: remove direct table grants from client-facing roles.
-- Safe for this project because the app uses the service role only via backend.
REVOKE ALL ON TABLE public.users FROM anon, authenticated;
REVOKE ALL ON TABLE public.meals FROM anon, authenticated;
REVOKE ALL ON TABLE public.activities FROM anon, authenticated;
REVOKE ALL ON TABLE public.daily_summaries FROM anon, authenticated;
