from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass(slots=True)
class RateItem:
    id: Optional[int] = None
    project_id: int = 0
    category: str = "Material"
    item_name: str = ""
    unit: str = "Nos"
    rate: float = 0.0
    source: str = "Project"
    remarks: str = ""

    def validate(self):
        if self.project_id <= 0: raise ValueError("Invalid project.")
        if not self.item_name.strip(): raise ValueError("Rate item name is required.")
        if not self.unit.strip(): raise ValueError("Unit is required.")
        if self.rate < 0: raise ValueError("Rate cannot be negative.")

    @classmethod
    def from_row(cls, row):
        if row is None: return None
        return cls(
            id=row["id"], project_id=row["project_id"],
            category=row["category"], item_name=row["item_name"],
            unit=row["unit"], rate=float(row["rate"] or 0),
            source=row["source"] or "Project",
            remarks=row["remarks"] or "",
        )
