"""
Civil Estimate Suite Pro v4.0
Excavation Calculator

Supports:
    m³ with dimensions in metres
    Cft with dimensions in feet

Calculates:
    excavation quantity
    swell/waste-adjusted spoil quantity
    skilled and unskilled labour are handled by the estimate service
"""
from __future__ import annotations

from calculations.base_calculator import BaseCalculator
from calculations.calculation_result import CalculationResult


class ExcavationCalculator(BaseCalculator):
    CFT_TO_M3 = 0.028316846592

    def __init__(
        self,
        length: float,
        width: float,
        depth: float,
        quantity_unit: str = "m³",
        number_of_excavations: int = 1,
        spoil_factor_percent: float = 0.0,
    ):
        super().__init__()

        self.length = self.positive(length, "Length")
        self.width = self.positive(width, "Width")
        self.depth = self.positive(depth, "Depth")

        self.quantity_unit = self.normalize_unit(quantity_unit)
        if self.quantity_unit not in {"m³", "Cft"}:
            raise ValueError("Quantity unit must be m³ or Cft.")

        try:
            self.number_of_excavations = int(number_of_excavations)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Number of excavations must be a whole number."
            ) from exc

        if self.number_of_excavations <= 0:
            raise ValueError(
                "Number of excavations must be greater than zero."
            )

        self.spoil_factor_percent = self.non_negative(
            spoil_factor_percent,
            "Spoil factor",
        )

    @staticmethod
    def normalize_unit(unit: str) -> str:
        value = str(unit or "m³").strip().lower()
        aliases = {
            "m3": "m³",
            "m^3": "m³",
            "m³": "m³",
            "cft": "Cft",
            "ft3": "Cft",
            "ft³": "Cft",
            "cubic feet": "Cft",
            "cubic foot": "Cft",
        }
        return aliases.get(value, str(unit).strip())

    def _dimensions_m(self):
        if self.quantity_unit == "m³":
            return self.length, self.width, self.depth
        return (
            self.length * 0.3048,
            self.width * 0.3048,
            self.depth * 0.3048,
        )

    def calculate_excavation_m3(self):
        l, w, d = self._dimensions_m()
        return l * w * d * self.number_of_excavations

    def calculate(self) -> CalculationResult:
        excavation_m3 = self.calculate_excavation_m3()

        factor = (
            1.0
            if self.quantity_unit == "m³"
            else 1.0 / self.CFT_TO_M3
        )

        quantity = excavation_m3 * factor
        spoil_quantity = quantity * (
            1.0 + self.spoil_factor_percent / 100.0
        )

        self.result.calculator = "Excavation"
        self.result.description = "Earthwork Excavation"
        self.result.unit = self.quantity_unit
        self.result.quantity = quantity

        values = {
            "length": self.length,
            "width": self.width,
            "depth": self.depth,
            "dimension_unit": (
                "m" if self.quantity_unit == "m³" else "ft"
            ),
            "quantity_unit": self.quantity_unit,
            "number_of_excavations": self.number_of_excavations,
            "excavation_volume_m3": excavation_m3,
            "spoil_factor_percent": self.spoil_factor_percent,
            "spoil_quantity": spoil_quantity,
        }

        for key, value in values.items():
            self.result.add_value(key, value)

        return self.result


__all__ = ["ExcavationCalculator"]
