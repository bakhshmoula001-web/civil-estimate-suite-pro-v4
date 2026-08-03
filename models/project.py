from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Project:
    """
    Project Domain Model
    Civil Estimate Suite Pro v4.1
    """

    id: Optional[int] = None

    project_code: str = ""
    project_name: str = ""
    client_name: str = ""

    consultant: str = ""
    contractor: str = ""

    location: str = ""

    start_date: str = ""
    end_date: str = ""

    status: str = "Planning"

    remarks: str = ""

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    def validate(self) -> None:

        if not self.project_code.strip():
            raise ValueError("Project Code is required.")

        if not self.project_name.strip():
            raise ValueError("Project Name is required.")

        if not self.client_name.strip():
            raise ValueError("Client Name is required.")

    # --------------------------------------------------
    # Serialization
    # --------------------------------------------------

    def to_dict(self) -> dict:

        return {
            "id": self.id,
            "project_code": self.project_code,
            "project_name": self.project_name,
            "client_name": self.client_name,
            "consultant": self.consultant,
            "contractor": self.contractor,
            "location": self.location,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "status": self.status,
            "remarks": self.remarks,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    # --------------------------------------------------
    # Factory
    # --------------------------------------------------

    @classmethod
    def from_row(cls, row):

        if row is None:
            return None

        if hasattr(row, "keys"):

            return cls(
                id=row["id"],
                project_code=row["project_code"],
                project_name=row["project_name"],
                client_name=row["client_name"],
                consultant=row["consultant"],
                contractor=row["contractor"],
                location=row["location"],
                start_date=row["start_date"],
                end_date=row["end_date"],
                status=row["status"],
                remarks=row["remarks"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

        return cls(**row)

    # --------------------------------------------------
    # Display
    # --------------------------------------------------

    @property
    def display_name(self) -> str:
        return f"{self.project_code} - {self.project_name}"

    def __str__(self) -> str:
        return self.display_name