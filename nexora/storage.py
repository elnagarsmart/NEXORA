import sqlite3
from pathlib import Path

class LocalStore:
    def __init__(self):
        base = Path.home() / ".nexora"
        base.mkdir(parents=True, exist_ok=True)
        self.db = base / "local.db"
        with sqlite3.connect(self.db) as con:
            con.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, kind TEXT, value TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)")

    def add_item(self, kind, value):
        with sqlite3.connect(self.db) as con:
            con.execute("INSERT INTO items(kind, value) VALUES (?, ?)", (kind, value))

    def get_items(self, kind):
        with sqlite3.connect(self.db) as con:
            rows = con.execute("SELECT value FROM items WHERE kind=? ORDER BY id", (kind,)).fetchall()
        return [r[0] for r in rows]
