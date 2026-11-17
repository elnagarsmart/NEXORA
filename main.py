import flet as ft
from dotenv import load_dotenv
from pathlib import Path

from nexora.app import main

load_dotenv(Path(__file__).parent / ".env")

if __name__ == "__main__":
    ft.app(target=main)
