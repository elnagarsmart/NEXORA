import os
import sqlite3
import tempfile
from pathlib import Path


class LocalStore:
    """Small local SQLite store with a writable-path fallback for Android."""

    def __init__(self):
        configured = os.getenv("FLET_APP_STORAGE_DATA")
        candidates = []
        if configured:
            candidates.append(Path(configured) / "nexora")
        try:
            candidates.append(Path.home() / ".nexora")
        except Exception:
            pass
        candidates.append(Path(tempfile.gettempdir()) / "nexora")

        self.db = None
        self._memory = None

        for base in candidates:
            try:
                base.mkdir(parents=True, exist_ok=True)
                db_path = base / "local.db"
                with sqlite3.connect(db_path) as con:
                    con.execute(
                        "CREATE TABLE IF NOT EXISTS items ("
                        "id INTEGER PRIMARY KEY, "
                        "kind TEXT NOT NULL, "
                        "value TEXT NOT NULL, "
                        "created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
                    )
                self.db = db_path
                break
            except (OSError, sqlite3.Error):
                continue

        if self.db is None:
            self._memory = sqlite3.connect(":memory:", check_same_thread=False)
            self._memory.execute(
                "CREATE TABLE IF NOT EXISTS items ("
                "id INTEGER PRIMARY KEY, "
                "kind TEXT NOT NULL, "
                "value TEXT NOT NULL, "
                "created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
            )

    def _connection(self):
        return sqlite3.connect(self.db) if self.db is not None else self._memory

    def add_item(self, kind, value):
        with self._connection() as con:
            con.execute(
                "INSERT INTO items(kind, value) VALUES (?, ?)",
                (kind, value),
            )

    def get_items(self, kind):
        with self._connection() as con:
            rows = con.execute(
                "SELECT value FROM items WHERE kind=? ORDER BY id",
                (kind,),
            ).fetchall()
        return [row[0] for row in rows]
