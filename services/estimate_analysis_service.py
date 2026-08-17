"""
Civil Estimate Suite Pro v4.0
Estimate Analysis Service

Stores the detailed calculation trail behind a BOQ item.
The service is intentionally generic so the same structure can
be used by PCC, brickwork, plaster, excavation, RCC and steel.
"""
from __future__ import annotations

import json
from typing import Any


class EstimateAnalysisService:
    """Persist and retrieve detailed quantity/cost analysis."""

    TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS estimate_analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        boq_id INTEGER NOT NULL UNIQUE,
        calculator_type TEXT NOT NULL,
        analysis_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
        FOREIGN KEY(boq_id) REFERENCES boq(id) ON DELETE CASCADE
    );
    """

    def __init__(self, database):
        self.database = database
        self.initialize()

    def initialize(self) -> None:
        self.database.execute(self.TABLE_SQL)
        self.database.commit()

    def save(
        self,
        project_id: int,
        boq_id: int,
        calculator_type: str,
        analysis: dict[str, Any],
    ) -> int:
        project_id = int(project_id)
        boq_id = int(boq_id)
        if project_id <= 0 or boq_id <= 0:
            raise ValueError("Project ID and BOQ ID must be valid.")
        if not isinstance(analysis, dict):
            raise ValueError("Analysis must be a dictionary.")

        payload = json.dumps(analysis, ensure_ascii=False, sort_keys=True)

        existing = self.database.fetchone(
            "SELECT id FROM estimate_analyses WHERE boq_id=?",
            (boq_id,),
        )

        if existing:
            self.database.execute(
                """
                UPDATE estimate_analyses
                SET project_id=?, calculator_type=?, analysis_json=?,
                    updated_at=CURRENT_TIMESTAMP
                WHERE boq_id=?
                """,
                (project_id, calculator_type, payload, boq_id),
            )
            self.database.commit()
            return int(existing["id"])

        cursor = self.database.execute(
            """
            INSERT INTO estimate_analyses
            (project_id, boq_id, calculator_type, analysis_json)
            VALUES (?, ?, ?, ?)
            """,
            (project_id, boq_id, calculator_type, payload),
        )
        self.database.commit()
        return int(cursor.lastrowid)

    def get_by_boq(self, boq_id: int) -> dict[str, Any] | None:
        row = self.database.fetchone(
            "SELECT * FROM estimate_analyses WHERE boq_id=?",
            (int(boq_id),),
        )
        if row is None:
            return None

        try:
            data = json.loads(row["analysis_json"])
        except (TypeError, ValueError, json.JSONDecodeError):
            data = {}

        data["_id"] = row["id"]
        data["_project_id"] = row["project_id"]
        data["_boq_id"] = row["boq_id"]
        data["_calculator_type"] = row["calculator_type"]
        return data

    def get_by_project(self, project_id: int) -> list[dict[str, Any]]:
        rows = self.database.fetchall(
            """
            SELECT * FROM estimate_analyses
            WHERE project_id=?
            ORDER BY boq_id
            """,
            (int(project_id),),
        )
        results = []
        for row in rows:
            try:
                data = json.loads(row["analysis_json"])
            except (TypeError, ValueError, json.JSONDecodeError):
                data = {}
            data["_id"] = row["id"]
            data["_project_id"] = row["project_id"]
            data["_boq_id"] = row["boq_id"]
            data["_calculator_type"] = row["calculator_type"]
            results.append(data)
        return results

    def delete_by_boq(self, boq_id: int) -> bool:
        self.database.execute(
            "DELETE FROM estimate_analyses WHERE boq_id=?",
            (int(boq_id),),
        )
        self.database.commit()
        return True
