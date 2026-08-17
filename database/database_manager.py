from __future__ import annotations

import sqlite3
from pathlib import Path


class DatabaseManager:
    """SQLite Database Manager"""

    def __init__(self, database_path: str):
        self.database_path = Path(database_path)
        self.connection = None

    # =====================================================
    # Connection
    # =====================================================

    def connect(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.database_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    # =====================================================
    # Core SQL Methods
    # =====================================================

    def execute(self, sql: str, params=()):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor

    def commit(self):
        self.connect().commit()

    def rollback(self):
        self.connect().rollback()

    # =====================================================
    # Fetch Methods
    # =====================================================

    def fetchone(self, sql: str, params=()):
        cursor = self.execute(sql, params)
        return cursor.fetchone()

    def fetchall(self, sql: str, params=()):
        cursor = self.execute(sql, params)
        return cursor.fetchall()

    # Compatibility (old method names)

    def fetch_one(self, sql: str, params=()):
        return self.fetchone(sql, params)

    def fetch_all(self, sql: str, params=()):
        return self.fetchall(sql, params)

    # =====================================================
    # Project CRUD
    # =====================================================

    def insert_project(self, project):

        cursor = self.execute(
            """
            INSERT INTO projects
            (
                project_code,
                project_name,
                client_name,
                consultant,
                contractor
                location,
                start_date,
                end_date,
                status,
                remarks

            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                project.project_code,
                project.project_name,
                project.client_name,
                project.consultant,
                project.contractor,
                project.location,
                project.start_date,
                project.end_date,
                project.status,
                project.remarks,
            ),
        )

        self.commit()

        return cursor.lastrowid

    def update_project(self, project_id, project):

        self.execute(
            """
            UPDATE projects
            SET
                project_code=?,
                project_name=?,
                client_name=?,
                location=?,
                description=?
            WHERE id=?
            """,
            (
                project.project_code,
                project.project_name,
                project.client_name,
                project.location,
                project.description,
                project_id,
            ),
        )

        self.commit()

        return True

    def delete_project(self, project_id):

        self.execute(
            "DELETE FROM projects WHERE id=?",
            (project_id,),
        )

        self.commit()

        return True

    def get_project(self, project_id):

        return self.fetchone(
            "SELECT * FROM projects WHERE id=?",
            (project_id,),
        )

    def get_projects(self):

        return self.fetchall(
            "SELECT * FROM projects ORDER BY id DESC"
        )