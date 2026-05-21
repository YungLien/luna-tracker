# Supabase migrations

## Fix Security Advisor alerts (RLS)

If Supabase reports **"Table publicly accessible"** or **"Sensitive data publicly accessible"**:

1. Open [Supabase Dashboard](https://supabase.com/dashboard) → your **luna_tracker** project.
2. Go to **SQL Editor** → **New query**.
3. Paste and run the contents of [`migrations/001_enable_rls.sql`](./migrations/001_enable_rls.sql).
4. Open **Database** → **Security Advisor** and confirm the critical issues are resolved.

Your FastAPI backend uses `SUPABASE_SERVICE_KEY`, which **bypasses RLS** — the app keeps working. Public `anon` / `authenticated` keys can no longer read `users`, `meals`, `activities`, or `daily_summaries` through the auto-generated API.

**Never** put `SUPABASE_SERVICE_KEY` in the frontend or commit it to git.
