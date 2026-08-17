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
            consultant,
            contractor,
            location,
            start_date,
            end_date,
            status,
            remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor = self.db.execute(
            sql,
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
            consultant=?,
            contractor=?,
            location=?,
            start_date=?,
            end_date=?,
            status=?,
            remarks=?,
            updated_at=CURRENT_TIMESTAMP
        WHERE id=?
        """

        self.db.execute(
            sql,
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
            OR consultant LIKE ?
            OR contractor LIKE ?
            OR location LIKE ?
            OR start_date LIKE ?
            OR end_date LIKE ?
            OR status LIKE ?
            OR remarks LIKE ?
            OR created_at LIKE ?
            OR updated_at LIKE ?
        ORDER BY id DESC
        """

        rows = self.db.fetchall(
            sql,
            (
                keyword,
                keyword,
                keyword,
                keyword,
                keyword,
                keyword,
                keyword,
                keyword,
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
        limit = max(1, int(limit))

        sql = """
        SELECT *
        FROM projects
        ORDER BY id DESC
        LIMIT ?
        """

        rows = self.db.fetchall(sql, (limit,))
        return [Project.from_row(r) for r in rows]

    def count(self):
        """
        Return the actual number of project records.

        The database wrapper may return a dictionary-like row,
        sqlite Row, tuple/list, or a scalar depending on the
        configured database adapter. Handle all supported forms.
        """

        sql = """
        SELECT COUNT(*) AS project_count
        FROM projects
        """

        row = self.db.fetchone(sql)

        if row is None:
            return 0

        if isinstance(row, dict):
            value = row.get("project_count")

            if value is None:
                value = next(iter(row.values()), 0)

            try:
                return int(value or 0)
            except (TypeError, ValueError):
                return 0

        try:
            value = row["project_count"]
            return int(value or 0)
        except (KeyError, IndexError, TypeError):
            pass

        if isinstance(row, (tuple, list)):
            if not row:
                return 0

            try:
                return int(row[0] or 0)
            except (TypeError, ValueError):
                return 0

        try:
            return int(row)
        except (TypeError, ValueError):
            return 0
