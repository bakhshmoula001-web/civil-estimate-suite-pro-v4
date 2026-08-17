"""
Civil Estimate Suite Pro v4.0
PCC Calculator

Supports engineer-friendly quantity units:
    - m³ with dimensions entered in metres
    - Cft with dimensions entered in feet

Calculations are performed internally in metric units for consistency and
then converted back to the selected quantity/material volume unit.
"""
from __future__ import annotations

from calculations.base_calculator import BaseCalculator
from calculations.calculation_result import CalculationResult


class PCCCalculator(BaseCalculator):
    MIX_RATIOS = {
        "1:2:4": (1.0, 2.0, 4.0),
        "1:3:6": (1.0, 3.0, 6.0),
        "1:1.5:3": (1.0, 1.5, 3.0),
        "1:4:8": (1.0, 4.0, 8.0),
    }

    UNIT_FACTORS_TO_M3 = {
        "m³": 1.0,
        "Cft": 0.028316846592,
    }

    def __init__(
        self,
        length: float,
        width: float,
        height: float,
        mix_ratio: str = "1:2:4",
        volume_unit: str = "m³",
    ):
        super().__init__()

        self.length = self.positive(length, "Length")
        self.width = self.positive(width, "Width")
        self.height = self.positive(height, "Height")

        if mix_ratio not in self.MIX_RATIOS:
            raise ValueError(f"Unsupported mix ratio: {mix_ratio}")

        normalized_unit = self.normalize_unit(volume_unit)
        if normalized_unit not in self.UNIT_FACTORS_TO_M3:
            raise ValueError("Volume unit must be either m³ or Cft.")

        self.mix_ratio = mix_ratio
        self.volume_unit = normalized_unit
        self.factor_to_m3 = self.UNIT_FACTORS_TO_M3[normalized_unit]

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

    def calculate(self) -> CalculationResult:
        cement_part, sand_part, aggregate_part = self.MIX_RATIOS[self.mix_ratio]
        total_parts = cement_part + sand_part + aggregate_part

        # Convert entered dimensions to metres so the internal calculation
        # remains consistent regardless of the engineer's selected unit.
        if self.volume_unit == "m³":
            length_m = self.length
            width_m = self.width
            height_m = self.height
        else:
            length_m = self.length * 0.3048
            width_m = self.width * 0.3048
            height_m = self.height * 0.3048

        wet_volume_m3 = length_m * width_m * height_m
        dry_volume_m3 = self.dry_volume(wet_volume_m3)

        cement_volume_m3 = self.ratio_part(
            dry_volume_m3, cement_part, total_parts
        )
        cement_bags = self.cement_bags(cement_volume_m3)

        sand_volume_m3 = self.ratio_part(
            dry_volume_m3, sand_part, total_parts
        )
        aggregate_volume_m3 = self.ratio_part(
            dry_volume_m3, aggregate_part, total_parts
        )

        factor = self.factor_to_m3
        wet_volume = wet_volume_m3 / factor
        dry_volume = dry_volume_m3 / factor
        sand_volume = sand_volume_m3 / factor
        aggregate_volume = aggregate_volume_m3 / factor
        cement_volume = cement_volume_m3 / factor

        self.result.calculator = "PCC"
        self.result.description = f"PCC ({self.mix_ratio})"
        self.result.unit = self.volume_unit
        self.result.quantity = wet_volume
        self.result.wet_volume = wet_volume
        self.result.dry_volume = dry_volume
        self.result.cement_volume = cement_volume
        self.result.cement_bags = cement_bags
        self.result.sand_volume = sand_volume
        self.result.aggregate_volume = aggregate_volume

        self.result.add_value("mix_ratio", self.mix_ratio)
        self.result.add_value("length", self.length)
        self.result.add_value("width", self.width)
        self.result.add_value("height", self.height)
        self.result.add_value("dimension_unit", "m" if self.volume_unit == "m³" else "ft")
        self.result.add_value("volume_unit", self.volume_unit)
        self.result.add_value("metric_quantity_m3", wet_volume_m3)
        self.result.add_value("metric_dry_volume_m3", dry_volume_m3)
        self.result.add_value("metric_sand_volume_m3", sand_volume_m3)
        self.result.add_value("metric_aggregate_volume_m3", aggregate_volume_m3)

        return self.result
