
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Project:
    """Project domain model for Civil Estimate Suite Pro."""

    id: Optional[int] = None
    project_code: str = ""
    project_name: str = ""
    client_name: str = ""
    location: str = ""
    description: str = ""

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    is_active: bool = True
    version: int = 1

    def validate(self) -> None:
        if not self.project_name.strip():
            raise ValueError("Project name is required.")

        if not self.project_code.strip():
            raise ValueError("Project code is required.")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_code": self.project_code,
            "project_name": self.project_name,
            "client_name": self.client_name,
            "location": self.location,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": self.is_active,
            "version": self.version,
        }

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
                location=row["location"],
                description=row["description"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

        return cls(**row)

    @property
    def display_name(self) -> str:
        return f"{self.project_code} - {self.project_name}"

    def __str__(self) -> str:
        return self.display_name
