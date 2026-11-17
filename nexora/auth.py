import os
from supabase import create_client

class AuthService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        self.client = create_client(url, key) if url and key and "YOUR_PROJECT" not in url else None

    def sign_in(self, email, password):
        if not self.client:
            raise RuntimeError("Set SUPABASE_URL and SUPABASE_ANON_KEY in .env first.")
        return self.client.auth.sign_in_with_password({"email": email, "password": password})

    def sign_up(self, email, password):
        if not self.client:
            raise RuntimeError("Supabase is not configured.")
        return self.client.auth.sign_up({"email": email, "password": password})

    def google_sign_in(self):
        if not self.client:
            raise RuntimeError("Supabase is not configured.")
        result = self.client.auth.sign_in_with_oauth({"provider": "google"})
        return result.url
