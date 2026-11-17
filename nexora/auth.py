import os


class AuthService:
    """Load the optional Supabase SDK only when authentication is used.

    Keeping this import lazy prevents an optional native dependency from
    stopping the Android app before its first screen is displayed.
    """

    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")
        self.client = None

    def _get_client(self):
        if self.client is not None:
            return self.client

        if not self.url or not self.key or "YOUR_PROJECT" in self.url:
            raise RuntimeError(
                "تسجيل الدخول السحابي غير مُعدّ بعد. يلزم إعداد Supabase أولاً."
            )

        try:
            from supabase import create_client
            self.client = create_client(self.url, self.key)
            return self.client
        except Exception as exc:
            raise RuntimeError(
                f"تعذر تحميل خدمة تسجيل الدخول: {type(exc).__name__}: {exc}"
            ) from exc

    def sign_in(self, email, password):
        if not email or not password:
            raise ValueError("أدخل البريد الإلكتروني وكلمة المرور.")
        return self._get_client().auth.sign_in_with_password(
            {"email": email, "password": password}
        )

    def sign_up(self, email, password):
        if not email or not password:
            raise ValueError("أدخل البريد الإلكتروني وكلمة المرور.")
        return self._get_client().auth.sign_up(
            {"email": email, "password": password}
        )

    def google_sign_in(self):
        result = self._get_client().auth.sign_in_with_oauth(
            {"provider": "google"}
        )
        return result.url
