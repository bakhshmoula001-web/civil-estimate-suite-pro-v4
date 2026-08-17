"""
=========================================================
Civil Estimate Suite Pro v4.0
Calculation Result
---------------------------------------------------------
Common result object returned by all calculators.
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CalculationResult:
    """
    Generic calculation result.

    Every calculator (PCC, Brickwork, RCC, Road, etc.)
    should return this object.
    """

    # ---------------------------------------------
    # Basic Information
    # ---------------------------------------------

    calculator: str = ""

    description: str = ""

    unit: str = ""

    quantity: float = 0.0

    # ---------------------------------------------
    # Volumes
    # ---------------------------------------------

    wet_volume: float = 0.0

    dry_volume: float = 0.0

    # ---------------------------------------------
    # Material Quantities
    # ---------------------------------------------

    cement_volume: float = 0.0

    cement_bags: float = 0.0

    sand_volume: float = 0.0

    aggregate_volume: float = 0.0

    steel_weight: float = 0.0

    # ---------------------------------------------
    # Cost
    # ---------------------------------------------

    material_cost: float = 0.0

    labour_cost: float = 0.0

    total_cost: float = 0.0

    # ---------------------------------------------
    # Extra Values
    # ---------------------------------------------

    extras: dict[str, Any] = field(default_factory=dict)

    # =====================================================
    # Helpers
    # =====================================================

    def add_value(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store any additional calculation value.
        """

        self.extras[key] = value

    def get_value(
        self,
        key: str,
        default=None,
    ):
        """
        Read additional value.
        """

        return self.extras.get(key, default)

    # =====================================================
    # Cost
    # =====================================================

    def calculate_total_cost(self) -> float:

        self.total_cost = round(
            self.material_cost +
            self.labour_cost,
            2,
        )

        return self.total_cost

    # =====================================================
    # Dictionary
    # =====================================================

    def to_dict(self) -> dict:

        return {
            "calculator": self.calculator,
            "description": self.description,
            "unit": self.unit,
            "quantity": self.quantity,
            "wet_volume": self.wet_volume,
            "dry_volume": self.dry_volume,
            "cement_volume": self.cement_volume,
            "cement_bags": self.cement_bags,
            "sand_volume": self.sand_volume,
            "aggregate_volume": self.aggregate_volume,
            "steel_weight": self.steel_weight,
            "material_cost": self.material_cost,
            "labour_cost": self.labour_cost,
            "total_cost": self.total_cost,
            "extras": self.extras,
        }