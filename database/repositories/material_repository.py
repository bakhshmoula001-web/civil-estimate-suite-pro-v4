from __future__ import annotations

from models.material import Material


class MaterialRepository:
    """
    Material Repository

    Handles all database operations for Material records.
    """

    def __init__(self, database):
        self.db = database

    # =====================================================
    # CREATE
    # =====================================================

    def create(self, material: Material):

        cursor = self.db.execute(
            """
            INSERT INTO materials
            (
                project_id,
                material_name,
                unit,
                quantity,
                rate,
                amount,
                remarks
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                material.project_id,
                material.material_name,
                material.unit,
                material.quantity,
                material.rate,
                material.amount,
                material.remarks,
            ),
        )

        self.db.commit()

        return cursor.lastrowid

    # =====================================================
    # READ
    # =====================================================

    def get(self, material_id: int):

        row = self.db.fetchone(
            """
            SELECT *
            FROM materials
            WHERE id = ?
            """,
            (material_id,),
        )

        return Material.from_row(row)

    def get_all(self):

        rows = self.db.fetchall(
            """
            SELECT *
            FROM materials
            ORDER BY material_name
            """
        )

        return [Material.from_row(row) for row in rows]

    def get_by_project(self, project_id: int):

        rows = self.db.fetchall(
            """
            SELECT *
            FROM materials
            WHERE project_id = ?
            ORDER BY material_name
            """,
            (project_id,),
        )

        return [Material.from_row(row) for row in rows]

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        material_id: int,
        material: Material,
    ):

        self.db.execute(
            """
            UPDATE materials
            SET
                material_name=?,
                unit=?,
                quantity=?,
                rate=?,
                amount=?,
                remarks=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (
                material.material_name,
                material.unit,
                material.quantity,
                material.rate,
                material.amount,
                material.remarks,
                material_id,
            ),
        )

        self.db.commit()

        return True

    # =====================================================
    # DELETE
    # =====================================================

    def delete(self, material_id: int):

        self.db.execute(
            """
            DELETE FROM materials
            WHERE id=?
            """,
            (material_id,),
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
            FROM materials
            WHERE
                material_name LIKE ?
                OR unit LIKE ?
                OR remarks LIKE ?
            ORDER BY material_name
            """,
            (
                keyword,
                keyword,
                keyword,
            ),
        )

        return [Material.from_row(row) for row in rows]

    # =====================================================
    # HELPERS
    # =====================================================

    def count(self):

        row = self.db.fetchone(
            """
            SELECT COUNT(*) AS total
            FROM materials
            """
        )

        if row is None:
            return 0

        return row["total"]

    def exists(
        self,
        project_id: int,
        material_name: str,
    ):

        row = self.db.fetchone(
            """
            SELECT id
            FROM materials
            WHERE
                project_id = ?
                AND material_name = ?
            """,
            (
                project_id,
                material_name,
            ),
        )

        return row is not None