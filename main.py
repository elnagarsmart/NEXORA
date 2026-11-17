from pathlib import Path

import flet as ft

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except Exception:
    # The Android package can run without a local .env file.
    pass

try:
    from nexora.app import main
except Exception as import_error:
    # Keep import-time failures visible on screen instead of showing a blank app.
    def main(page: ft.Page):
        page.title = "NEXORA — Startup error"
        page.bgcolor = "#0B1020"
        page.padding = 24
        page.add(
            ft.Column(
                [
                    ft.Text("NEXORA", size=28, weight=ft.FontWeight.BOLD),
                    ft.Text("تعذر تحميل التطبيق." , size=18, color="white"),
                    ft.Text(
                        f"{type(import_error).__name__}: {import_error}",
                        color="#F5C66A",
                        selectable=True,
                    ),
                ],
                spacing=16,
            )
        )

if __name__ == "__main__":
    ft.app(target=main)
