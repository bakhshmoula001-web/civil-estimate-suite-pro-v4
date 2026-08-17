"""
Civil Estimate Suite Pro v4.0
Plaster Calculator

Supports:
    m² with dimensions in metres
    Sft with dimensions in feet

The plaster thickness is entered in millimetres.
Material analysis:
    Cement (bags)
    Sand (m³ / Cft)
"""
from __future__ import annotations

from calculations.base_calculator import BaseCalculator
from calculations.calculation_result import CalculationResult


class PlasterCalculator(BaseCalculator):
    MIX_RATIOS = {
        "1:4": (1.0, 4.0),
        "1:5": (1.0, 5.0),
        "1:6": (1.0, 6.0),
    }

    DRY_MORTAR_FACTOR = 1.33
    CFT_TO_M3 = 0.028316846592

    def __init__(
        self,
        length: float,
        height: float,
        thickness_mm: float = 12.0,
        mortar_ratio: str = "1:4",
        surfaces: int = 1,
        area_unit: str = "m²",
    ):
        super().__init__()

        self.length = self.positive(length, "Length")
        self.height = self.positive(height, "Height")
        self.thickness_mm = self.positive(
            thickness_mm,
            "Plaster thickness",
        )

        self.surfaces = int(surfaces)
        if self.surfaces not in (1, 2):
            raise ValueError("Surfaces must be 1 or 2.")

        self.mortar_ratio = str(mortar_ratio)
        if self.mortar_ratio not in self.MIX_RATIOS:
            raise ValueError(
                f"Unsupported mortar ratio: {mortar_ratio}."
            )

        self.area_unit = self.normalize_unit(area_unit)
        if self.area_unit not in {"m²", "Sft"}:
            raise ValueError("Area unit must be m² or Sft.")

    @staticmethod
    def normalize_unit(unit: str) -> str:
        value = str(unit or "m²").strip().lower()
        aliases = {
            "m2": "m²",
            "m^2": "m²",
            "m²": "m²",
            "sqm": "m²",
            "sq.m": "m²",
            "sft": "Sft",
            "ft2": "Sft",
            "ft²": "Sft",
            "sqft": "Sft",
            "sq ft": "Sft",
        }
        return aliases.get(value, str(unit).strip())

    def _dimensions_m(self):
        if self.area_unit == "m²":
            return self.length, self.height
        return self.length * 0.3048, self.height * 0.3048

    def calculate_area_m2(self):
        length_m, height_m = self._dimensions_m()
        return length_m * height_m * self.surfaces

    def calculate(self) -> CalculationResult:
        area_m2 = self.calculate_area_m2()
        thickness_m = self.thickness_mm / 1000.0

        wet_mortar_m3 = area_m2 * thickness_m
        dry_mortar_m3 = wet_mortar_m3 * self.DRY_MORTAR_FACTOR

        cement_part, sand_part = self.MIX_RATIOS[self.mortar_ratio]
        total_parts = cement_part + sand_part

        cement_m3 = dry_mortar_m3 * cement_part / total_parts
        sand_m3 = dry_mortar_m3 * sand_part / total_parts
        cement_bags = self.cement_bags(cement_m3)

        factor = 1.0 if self.area_unit == "m²" else 1 / 0.09290304
        quantity = area_m2 * factor
        sand_quantity = (
            sand_m3
            if self.area_unit == "m²"
            else sand_m3 / self.CFT_TO_M3
        )

        self.result.calculator = "Plaster"
        self.result.description = f"Plaster ({self.mortar_ratio})"
        self.result.unit = self.area_unit
        self.result.quantity = quantity
        self.result.wet_volume = wet_mortar_m3
        self.result.dry_volume = dry_mortar_m3
        self.result.cement_volume = cement_m3
        self.result.cement_bags = cement_bags
        self.result.sand_volume = sand_quantity

        values = {
            "length": self.length,
            "height": self.height,
            "dimension_unit": "m" if self.area_unit == "m²" else "ft",
            "area_unit": self.area_unit,
            "surfaces": self.surfaces,
            "thickness_mm": self.thickness_mm,
            "mortar_ratio": self.mortar_ratio,
            "area_m2": area_m2,
            "wet_mortar_m3": wet_mortar_m3,
            "dry_mortar_m3": dry_mortar_m3,
            "cement_m3": cement_m3,
            "cement_bags": cement_bags,
            "sand_m3": sand_m3,
            "sand_quantity": sand_quantity,
        }
        for key, value in values.items():
            self.result.add_value(key, value)

        return self.result


__all__ = ["PlasterCalculator"]
