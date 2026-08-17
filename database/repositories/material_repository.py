from __future__ import annotations

from models.material import Material


class MaterialRepository:
    """Database access for project material records."""

    def __init__(self, database):
        self.db = database

    def create(self, material: Material):
        cursor = self.db.execute(
            """
            INSERT INTO materials
            (project_id, material_name, unit, quantity, rate, amount, remarks)
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

    def get(self, material_id: int):
        row = self.db.fetchone(
            "SELECT * FROM materials WHERE id = ?",
            (material_id,),
        )
        return Material.from_row(row)

    def get_all(self):
        rows = self.db.fetchall(
            "SELECT * FROM materials ORDER BY material_name, unit"
        )
        return [Material.from_row(row) for row in rows]

    def get_by_project(self, project_id: int):
        rows = self.db.fetchall(
            """
            SELECT * FROM materials
            WHERE project_id = ?
            ORDER BY material_name, unit
            """,
            (project_id,),
        )
        return [Material.from_row(row) for row in rows]

    def find_by_project_name_unit(
        self,
        project_id: int,
        material_name: str,
        unit: str,
    ):
        row = self.db.fetchone(
            """
            SELECT *
            FROM materials
            WHERE project_id = ?
              AND LOWER(TRIM(material_name)) = LOWER(TRIM(?))
              AND LOWER(TRIM(unit)) = LOWER(TRIM(?))
            LIMIT 1
            """,
            (project_id, material_name, unit),
        )
        return Material.from_row(row)

    def exists(self, project_id: int, material_name: str, unit: str | None = None):
        if unit is None:
            row = self.db.fetchone(
                """
                SELECT id FROM materials
                WHERE project_id = ?
                  AND LOWER(TRIM(material_name)) = LOWER(TRIM(?))
                LIMIT 1
                """,
                (project_id, material_name),
            )
        else:
            row = self.db.fetchone(
                """
                SELECT id FROM materials
                WHERE project_id = ?
                  AND LOWER(TRIM(material_name)) = LOWER(TRIM(?))
                  AND LOWER(TRIM(unit)) = LOWER(TRIM(?))
                LIMIT 1
                """,
                (project_id, material_name, unit),
            )
        return row is not None

    def update(self, material_id: int, material: Material):
        self.db.execute(
            """
            UPDATE materials
            SET material_name=?,
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

    def delete(self, material_id: int):
        self.db.execute(
            "DELETE FROM materials WHERE id=?",
            (material_id,),
        )
        self.db.commit()
        return True

    def search(self, keyword: str):
        keyword = f"%{keyword}%"
        rows = self.db.fetchall(
            """
            SELECT * FROM materials
            WHERE material_name LIKE ?
               OR unit LIKE ?
               OR remarks LIKE ?
            ORDER BY material_name, unit
            """,
            (keyword, keyword, keyword),
        )
        return [Material.from_row(row) for row in rows]

    def count(self):
        row = self.db.fetchone("SELECT COUNT(*) AS total FROM materials")
        return 0 if row is None else row["total"]
