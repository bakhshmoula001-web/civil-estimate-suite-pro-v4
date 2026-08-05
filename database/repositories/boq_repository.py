from __future__ import annotations

from models import boq
from models.boq import BOQ


class BOQRepository:
    """
    BOQ Repository

    Handles all database operations for BOQ items.
    """

    def __init__(self, database):
        self.db = database

    # =====================================================
    # CREATE
    # =====================================================

    def create(self, boq: BOQ):
        print("========== BOQ DEBUG ==========")
        print("project_id :", boq.project_id)
        print("item_no    :", boq.item_no)
        print("description:", boq.description)
        print("===============================")

        cursor = self.db.execute(
            """
            INSERT INTO boq
            (
                project_id,
                item_no,
                description,
                unit,
                quantity,
                rate,
                amount,
                remarks
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                boq.project_id,
                boq.item_no,
                boq.description,
                boq.unit,
                boq.quantity,
                boq.rate,
                boq.amount,
                boq.remarks,
            ),
        )

        self.db.commit()

        return cursor.lastrowid

    # =====================================================
    # READ
    # =====================================================

    def get(self, boq_id: int):

        row = self.db.fetchone(
            "SELECT * FROM boq WHERE id=?",
            (boq_id,),
        )

        return BOQ.from_row(row)

    def get_all(self):

        rows = self.db.fetchall(
            """
            SELECT *
            FROM boq
            ORDER BY item_no
            """
        )

        return [BOQ.from_row(r) for r in rows]

    def get_by_project(self, project_id: int):

        rows = self.db.fetchall(
            """
            SELECT *
            FROM boq
            WHERE project_id=?
            ORDER BY item_no
            """,
            (project_id,),
        )

        return [BOQ.from_row(r) for r in rows]

    # =====================================================
    # UPDATE
    # =====================================================

    def update(self, boq_id: int, boq: BOQ):

        self.db.execute(
            """
            UPDATE boq
            SET
                item_no=?,
                description=?,
                unit=?,
                quantity=?,
                rate=?,
                amount=?,
                remarks=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (
                boq.item_no,
                boq.description,
                boq.unit,
                boq.quantity,
                boq.rate,
                boq.amount,
                boq.remarks,
                boq_id,
            ),
        )

        self.db.commit()

        return True

    # =====================================================
    # DELETE
    # =====================================================

    def delete(self, boq_id: int):

        self.db.execute(
            "DELETE FROM boq WHERE id=?",
            (boq_id,),
        )

        self.db.commit()

        return True

    # =====================================================
    # SEARCH
    # =====================================================

    def search(self, keyword: str):

        keyword = f"%{keyword}%"

        rows = self.db.fetchall(
            """
            SELECT *
            FROM boq
            WHERE
                item_no LIKE ?
                OR description LIKE ?
                OR unit LIKE ?
            ORDER BY item_no
            """,
            (
                keyword,
                keyword,
                keyword,
            ),
        )

        return [BOQ.from_row(r) for r in rows]

    # =====================================================
    # HELPERS
    # =====================================================

    def count(self):

        row = self.db.fetchone(
            "SELECT COUNT(*) AS total FROM boq"
        )

        if row is None:
            return 0

        return row["total"]

    def exists(self, project_id: int, item_no: str):

        row = self.db.fetchone(
            """
            SELECT id
            FROM boq
            WHERE project_id=? AND item_no=?
            """,
            (
                project_id,
                item_no,
            ),
        )

        return row is not None