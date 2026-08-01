"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : BOQ Item Model
Purpose   : BOQ Entity
Author    : OpenAI + Moula Bakhsh
Version   : 4.0.0
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class BOQItem:
    """
    BOQ Item Entity
    """

    id: Optional[int] = None

    project_id: int = 0

    item_no: str = ""

    description: str = ""

    unit: str = ""

    quantity: float = 0.0

    rate: float = 0.0

    amount: float = 0.0

    remarks: str = ""

    created_at: str = ""

    updated_at: str = ""

    @property
    def total(self) -> float:
        """
        Auto calculate amount.
        """
        return round(self.quantity * self.rate, 2)

    def is_new(self) -> bool:
        return self.id is None

    def to_dict(self) -> dict:

        return {
            "id": self.id,
            "project_id": self.project_id,
            "item_no": self.item_no,
            "description": self.description,
            "unit": self.unit,
            "quantity": self.quantity,
            "rate": self.rate,
            "amount": self.amount,
            "remarks": self.remarks,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_row(cls, row):

        if row is None:
            return None

        return cls(
            id=row["id"],
            project_id=row["project_id"],
            item_no=row["item_no"],
            description=row["description"],
            unit=row["unit"],
            quantity=row["quantity"],
            rate=row["rate"],
            amount=row["amount"],
            remarks=row["remarks"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )