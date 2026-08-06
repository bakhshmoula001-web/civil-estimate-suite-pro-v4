"""
=========================================
Civil Estimate Suite Pro v4.0
Material Model
=========================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Material:
    """
    Material Record
    """

    id: Optional[int] = None

    project_id: int = 0

    material_name: str = ""

    unit: str = "Nos"

    quantity: float = 0.0

    rate: float = 0.0

    amount: float = 0.0

    remarks: str = ""

    created_at: Optional[str] = None

    updated_at: Optional[str] = None

    @property
    def total_amount(self) -> float:
        """
        Auto calculate amount.

        Returns
        -------
        float
        """
        return round(self.quantity * self.rate, 2)

    def calculate_amount(self) -> float:
        """
        Update amount field.
        """
        self.amount = round(
            self.quantity * self.rate,
            2,
        )
        return self.amount

    def to_dict(self) -> dict:
        """
        Convert model into dictionary.
        """

        return {
            "id": self.id,
            "project_id": self.project_id,
            "material_name": self.material_name,
            "unit": self.unit,
            "quantity": self.quantity,
            "rate": self.rate,
            "amount": self.amount,
            "remarks": self.remarks,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Material":
        """
        Create Material object from dictionary.
        """

        return cls(
            id=data.get("id"),
            project_id=data.get("project_id", 0),
            material_name=data.get("material_name", ""),
            unit=data.get("unit", "Nos"),
            quantity=float(data.get("quantity", 0)),
            rate=float(data.get("rate", 0)),
            amount=float(data.get("amount", 0)),
            remarks=data.get("remarks", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
    def validate(self):

        if self.project_id <= 0:
            raise ValueError("Invalid project.")

        if self.material_name.strip() == "":
            raise ValueError("Material name is required.")

        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative.")

        if self.rate < 0:
            raise ValueError("Rate cannot be negative.")

        if self.unit.strip() == "":
            raise ValueError("Unit is required.")
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
    @classmethod
    def from_row(cls, row):

        if row is None:
            return None

        return cls(
            id=row["id"],
            project_id=row["project_id"],
            material_name=row["material_name"],
            unit=row["unit"],
            quantity=float(row["quantity"] or 0),
            rate=float(row["rate"] or 0),
            amount=float(row["amount"] or 0),
            remarks=row["remarks"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
    )