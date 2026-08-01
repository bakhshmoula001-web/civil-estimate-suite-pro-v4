from __future__ import annotations

from database.schema import DATABASE_SCHEMA


class DatabaseInitializer:
    """
    Creates and updates the application database.

    Safe to call every application startup.
    """

    def __init__(self, database):
        self.database = database

    def initialize(self):

        conn = self.database.connect()

        conn.executescript(DATABASE_SCHEMA)

        conn.commit()