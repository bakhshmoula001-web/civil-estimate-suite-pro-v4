"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Base Repository
Purpose   : Base CRUD Repository
Author    : OpenAI + Moula Bakhsh
Version   : 4.0.0
=========================================================
"""

from __future__ import annotations

from typing import Any

from database.database_manager import DatabaseManager


class BaseRepository:
    """
    Base Repository

    Every repository inherits from this class.

    Features
    --------
    ✔ Execute SQL
    ✔ Fetch One
    ✔ Fetch All
    ✔ Insert
    ✔ Update
    ✔ Delete
    ✔ Count
    """

class BaseRepository:

    def __init__(self, database):

        self.db = database

    # --------------------------------------------------
    # Execute
    # --------------------------------------------------

    def execute(
        self,
        query: str,
        parameters: tuple = ()
    ):

        return self.db.execute(
            query,
            parameters
        )

    # --------------------------------------------------
    # Fetch
    # --------------------------------------------------

    def fetch_one(
        self,
        query: str,
        parameters: tuple = ()
    ):

        return self.db.fetch_one(
            query,
            parameters
        )

    def fetch_all(
        self,
        query: str,
        parameters: tuple = ()
    ):

        return self.db.fetch_all(
            query,
            parameters
        )

    # --------------------------------------------------
    # Insert
    # --------------------------------------------------

    def insert(
        self,
        query: str,
        parameters: tuple
    ) -> int:

        return self.db.insert(
            query,
            parameters
        )

    # --------------------------------------------------
    # Update
    # --------------------------------------------------

    def update(
        self,
        query: str,
        parameters: tuple
    ) -> int:

        return self.db.update(
            query,
            parameters
        )

    # --------------------------------------------------
    # Delete
    # --------------------------------------------------

    def delete(
        self,
        query: str,
        parameters: tuple
    ) -> int:

        return self.db.update(
            query,
            parameters
        )

    # --------------------------------------------------
    # Scalar
    # --------------------------------------------------

    def scalar(
        self,
        query: str,
        parameters: tuple = ()
    ) -> Any:

        return self.db.get_scalar(
            query,
            parameters
        )

    # --------------------------------------------------
    # Count
    # --------------------------------------------------

    def count(
        self,
        table_name: str
    ) -> int:

        query = f"SELECT COUNT(*) FROM {table_name}"

        result = self.scalar(query)

        return int(result or 0)

    # --------------------------------------------------
    # Exists
    # --------------------------------------------------

    def exists(
        self,
        table_name: str,
        field_name: str,
        value: Any
    ) -> bool:

        query = (
            f"SELECT COUNT(*) "
            f"FROM {table_name} "
            f"WHERE {field_name}=?"
        )

        result = self.scalar(
            query,
            (value,)
        )

        return int(result or 0) > 0