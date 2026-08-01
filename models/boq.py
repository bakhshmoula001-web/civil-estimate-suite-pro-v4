from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class BOQ:
    """
    BOQ Model

    Represents a single Bill of Quantities item.
    """

    id: Optional[int] = None
    project_id: Optional[int] = None

    item_no: str = ""
    description: str = ""

    unit: str = ""
    quantity: float = 0.0
    rate: float = 0.0
    amount: float = 0.0

    remarks: str = ""

    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    # ---------------------------------------------------------
    # Business Logic
    # ---------------------------------------------------------

    def calculate_amount(self) -> float:
        """Calculate total amount."""
        self.amount = round(
            float(self.quantity) * float(self.rate),
            2
        )
        return self.amount

    # ---------------------------------------------------------

    def validate(self):

        if not self.project_id:
            raise ValueError("Project is required.")

        if not self.item_no.strip():
            raise ValueError("Item No is required.")

        if not self.description.strip():
            raise ValueError("Description is required.")

        if not self.unit.strip():
            raise ValueError("Unit is required.")

        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        if self.rate < 0:
            raise ValueError("Rate cannot be negative.")

        self.calculate_amount()

    # ---------------------------------------------------------

    def to_dict(self):

        self.calculate_amount()

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

    # ---------------------------------------------------------

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

    # ---------------------------------------------------------

    @property
    def display_name(self):

        return f"{self.item_no} - {self.description}"