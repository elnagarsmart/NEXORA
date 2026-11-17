# NEXORA — Smart Digital World

A bilingual (Arabic/English) cross-platform starter built with Python + Flet, FastAPI and Supabase.

## Included in this first build
- Responsive Flet app shell for Android, Windows and Web
- Arabic/English interface toggle and light/dark mode
- Email/password and Google sign-in entry points through Supabase Auth
- Dashboard sections: AI assistant (provider-ready placeholder), files, notes, community, messaging, tasks, learning, search and settings
- FastAPI health endpoint and starter API
- Supabase SQL schema with Row Level Security, profiles, notes, tasks, posts, conversations, messages, reports and role scaffolding
- Local SQLite cache for offline notes/tasks starter data
- Windows run script and build guidance

## Requirements
- Python 3.11+
- Supabase project (free tier availability and limits can change)
- Android build: Flutter + Android SDK are required by Flet's packaging toolchain
- Windows build: Windows machine and Flet packaging dependencies

## Run locally (Windows)
1. Install Python 3.11+.
2. Copy `.env.example` to `.env` and fill the Supabase URL and publishable/anon key.
3. Open a terminal in this folder:
   ```bash
   python -m venv .venv
   .venv\\Scripts\\activate
   pip install -r requirements.txt
   python -m flet run
   ```
4. API (optional, separate terminal):
   ```bash
   uvicorn backend.main:app --reload
   ```

## Build
- Web: `flet build web`
- Android APK: `flet build apk`
- Windows: `flet build windows`

The exact Flet build prerequisites depend on the OS and installed SDKs. Build commands are included as a starting point, not a claim that binaries have already been produced.

## Supabase setup
1. Create a Supabase project.
2. Run `supabase/schema.sql` in the SQL Editor.
3. Configure Authentication > Providers > Google if Google sign-in is required.
4. Set the app's redirect URL(s) in Supabase Auth URL Configuration.
5. Put the project URL and publishable/anon key in `.env`.

Never put a Supabase service-role key in the client app. The schema enables RLS and restricts user-owned records. Public community posts are readable only when published; report/block/moderation workflows should be enabled before opening community features to the public.

## Important launch checklist
- Configure Google OAuth credentials and redirect URLs.
- Configure email provider and email confirmation templates.
- Add server-side moderation and rate limits before public launch.
- Add account deletion, privacy policy, terms, reporting and blocking.
- Configure backups and test RLS policies with multiple test accounts.
- Do not expose private messages or private files in public search.
