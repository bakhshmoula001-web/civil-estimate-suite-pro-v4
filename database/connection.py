# connection.py
from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import Lock


class DatabaseConnection:
    """Central SQLite connection manager."""

    def __init__(self, database_path: str):
        self.database_path = Path(database_path)
        self._connection = None
        self._lock = Lock()

    def connect(self) -> sqlite3.Connection:
        with self._lock:
            if self._connection is None:
                self.database_path.parent.mkdir(parents=True, exist_ok=True)

                self._connection = sqlite3.connect(
                    self.database_path,
                    check_same_thread=False
                )

                self._connection.row_factory = sqlite3.Row

                self._connection.execute("PRAGMA foreign_keys = ON;")
                self._connection.execute("PRAGMA journal_mode = WAL;")

            return self._connection

    def cursor(self):
        return self.connect().cursor()

    def commit(self):
        if self._connection:
            self._connection.commit()

    def rollback(self):
        if self._connection:
            self._connection.rollback()

    def close(self):
        with self._lock:
            if self._connection:
                self._connection.close()
                self._connection = None

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        return False
