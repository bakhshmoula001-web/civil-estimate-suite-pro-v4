from __future__ import annotations

from models.project import Project


class ProjectRepository:
    """
    Data Access Layer

    Service
        │
        ▼
    Repository
        │
        ▼
    SQLite Database
    """

    def __init__(self, db):
        self.db = db

    # =====================================================
    # CREATE
    # =====================================================

    def create(self, project: Project):

        sql = """
        INSERT INTO projects
        (
            project_code,
            project_name,
            client_name,
            location,
            description
        )
        VALUES (?, ?, ?, ?, ?)
        """

        cursor = self.db.execute(
            sql,
            (
                project.project_code,
                project.project_name,
                project.client_name,
                project.location,
                project.description,
            ),
        )

        self.db.commit()

        return cursor.lastrowid

    # =====================================================
    # READ
    # =====================================================

    def get(self, project_id: int):

        sql = """
        SELECT *
        FROM projects
        WHERE id = ?
        """

        row = self.db.fetchone(sql, (project_id,))

        if row is None:
            return None

        return Project.from_row(row)

    def get_all(self):

        sql = """
        SELECT *
        FROM projects
        ORDER BY id DESC
        """

        rows = self.db.fetchall(sql)

        return [Project.from_row(r) for r in rows]

    # =====================================================
    # UPDATE
    # =====================================================

    def update(self, project_id: int, project: Project):

        sql = """
        UPDATE projects
        SET

            project_code=?,
            project_name=?,
            client_name=?,
            location=?,
            description=?,
            updated_at=CURRENT_TIMESTAMP

        WHERE id=?
        """

        self.db.execute(
            sql,
            (
                project.project_code,
                project.project_name,
                project.client_name,
                project.location,
                project.description,
                project_id,
            ),
        )

        self.db.commit()

        return True

    # =====================================================
    # DELETE
    # =====================================================

    def delete(self, project_id: int):

        sql = """
        DELETE FROM projects
        WHERE id=?
        """

        self.db.execute(sql, (project_id,))

        self.db.commit()

        return True

    # =====================================================
    # SEARCH
    # =====================================================

    def search(self, keyword: str):

        keyword = f"%{keyword}%"

        sql = """
        SELECT *
        FROM projects

        WHERE

            project_code LIKE ?

            OR project_name LIKE ?

            OR client_name LIKE ?

            OR location LIKE ?

        ORDER BY id DESC
        """

        rows = self.db.fetchall(
            sql,
            (
                keyword,
                keyword,
                keyword,
                keyword,
            ),
        )

        return [Project.from_row(r) for r in rows]

    # =====================================================
    # HELPERS
    # =====================================================

    def find_by_code(self, project_code: str):

        sql = """
        SELECT *
        FROM projects
        WHERE project_code=?
        """

        row = self.db.fetchone(sql, (project_code,))

        if row is None:
            return None

        return Project.from_row(row)

    def get_recent(self, limit: int = 10):

        sql = f"""
        SELECT *
        FROM projects

        ORDER BY id DESC

        LIMIT {limit}
        """

        rows = self.db.fetchall(sql)

        return [Project.from_row(r) for r in rows]

    def count(self):

        sql = """
        SELECT COUNT(*)
        FROM projects
        """

        row = self.db.fetchone(sql)

        if isinstance(row, dict):
            return list(row.values())[0]

        if isinstance(row, (tuple, list)):
            return row[0]

        return 0