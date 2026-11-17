# NEXORA — Android App

NEXORA is being prepared as an installable **Android application (APK)**. It is not intended to be installed as a website or PWA.

## Android APK

The repository includes a GitHub Actions workflow that builds an APK whenever code is pushed to `main`, and can also be started manually from the Actions tab.

The build artifact is named `NEXORA-Android-APK` and contains the APK file. Download the artifact ZIP, extract it, then tap the `.apk` file on your Android phone to install it. Android may ask you to allow installation for the app used to open the file.

Build command used by the workflow:

```bash
flet build apk --product NEXORA --org com.elnagarsmart --bundle-id com.elnagarsmart.nexora
```

The APK is a native Android install package built with Flet/Flutter. The build workflow is configured, but an APK is only available after the GitHub Actions build finishes successfully.

## Run the source locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Backend (optional, separate from the Android app)

Install backend dependencies separately:

```bash
pip install -r requirements-backend.txt
uvicorn backend.main:app --reload
```

## Supabase setup

1. Create a Supabase project.
2. Run `supabase/schema.sql` in the SQL Editor.
3. Copy `.env.example` to `.env` and fill in the Supabase project URL and publishable/anon key.
4. Configure Google OAuth and the allowed redirect URLs in Supabase Auth if Google sign-in is needed.

Never put a Supabase service-role key inside the Android app. The current repository is a starter build: several modules are UI placeholders, and authentication, messaging, community moderation, role management, and cloud sync still need implementation and device testing before public release.

## Android signing

The automated APK is suitable for initial device testing. Before distributing production updates or publishing to Google Play, configure a private release keystore and keep it outside the public repository. Always preserve the same signing key for future updates.
