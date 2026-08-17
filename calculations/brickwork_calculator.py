"""
Civil Estimate Suite Pro v4.0
Brickwork Calculator

Supports:
    m³ with dimensions in metres
    Cft with dimensions in feet

Brick size presets remain stored in metres internally.
"""
from __future__ import annotations

from calculations.base_calculator import BaseCalculator
from calculations.calculation_result import CalculationResult


class BrickworkCalculator(BaseCalculator):
    BRICK_SIZES = {
        "Standard": {
            "length": 0.230,
            "width": 0.115,
            "height": 0.075,
        },
        "9x4.5x3 inch": {
            "length": 0.2286,
            "width": 0.1143,
            "height": 0.0762,
        },
        "9x4x3 inch": {
            "length": 0.2286,
            "width": 0.1016,
            "height": 0.0762,
        },
        "Custom": None,
    }

    MORTAR_RATIOS = {
        "1:4": (1.0, 4.0),
        "1:5": (1.0, 5.0),
        "1:6": (1.0, 6.0),
    }

    MORTAR_JOINT = 0.010
    DRY_MORTAR_FACTOR = 1.33
    CFT_TO_M3 = 0.028316846592

    def __init__(
        self,
        length: float,
        height: float,
        thickness: float,
        mortar_ratio: str = "1:6",
        brick_size: str = "Standard",
        waste_percent: float = 5.0,
        volume_unit: str = "m³",
        custom_brick_length: float | None = None,
        custom_brick_width: float | None = None,
        custom_brick_height: float | None = None,
    ):
        super().__init__()

        self.length = self.positive(length, "Length")
        self.height = self.positive(height, "Height")
        self.thickness = self.positive(thickness, "Wall thickness")

        if mortar_ratio not in self.MORTAR_RATIOS:
            raise ValueError(
                f"Unsupported mortar ratio: {mortar_ratio}. "
                f"Available: {', '.join(self.MORTAR_RATIOS)}"
            )

        if brick_size not in self.BRICK_SIZES:
            raise ValueError(
                f"Unsupported brick size: {brick_size}."
            )

        self.volume_unit = self.normalize_unit(volume_unit)
        if self.volume_unit not in {"m³", "Cft"}:
            raise ValueError("Volume unit must be either m³ or Cft.")

        self.mortar_ratio = mortar_ratio
        self.brick_size = brick_size
        self.waste_percent = self.non_negative(
            waste_percent,
            "Waste percentage",
        )

        self.custom_brick_length = custom_brick_length
        self.custom_brick_width = custom_brick_width
        self.custom_brick_height = custom_brick_height

        if self.brick_size == "Custom":
            self._validate_custom_brick_size()

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

    def _validate_custom_brick_size(self):
        self.custom_brick_length = self.positive(
            self.custom_brick_length,
            "Custom brick length",
        )
        self.custom_brick_width = self.positive(
            self.custom_brick_width,
            "Custom brick width",
        )
        self.custom_brick_height = self.positive(
            self.custom_brick_height,
            "Custom brick height",
        )

    def get_brick_dimensions(self):
        if self.brick_size == "Custom":
            return (
                self.custom_brick_length,
                self.custom_brick_width,
                self.custom_brick_height,
            )
        d = self.BRICK_SIZES[self.brick_size]
        return d["length"], d["width"], d["height"]

    def get_mortar_parts(self):
        return self.MORTAR_RATIOS[self.mortar_ratio]

    def _dimensions_in_metres(self):
        if self.volume_unit == "m³":
            return self.length, self.thickness, self.height
        return (
            self.length * 0.3048,
            self.thickness * 0.3048,
            self.height * 0.3048,
        )

    def calculate_wall_volume(self):
        length_m, thickness_m, height_m = self._dimensions_in_metres()
        return length_m * thickness_m * height_m

    def calculate_brick_volume(self):
        l, w, h = self.get_brick_dimensions()
        return l * w * h

    def calculate_nominal_brick_volume(self):
        l, w, h = self.get_brick_dimensions()
        j = self.MORTAR_JOINT
        return (l + j) * (w + j) * (h + j)

    def calculate_brick_quantity(self, wall_volume):
        nominal = self.calculate_nominal_brick_volume()
        base = wall_volume / nominal
        final = base * (1.0 + self.waste_percent / 100.0)
        return base, final

    def calculate_mortar_volume(self, wall_volume, base_brick_quantity):
        mortar = wall_volume - (
            base_brick_quantity * self.calculate_brick_volume()
        )
        return max(mortar, 0.0)

    def calculate_mortar_materials(self, mortar_volume):
        dry = mortar_volume * self.DRY_MORTAR_FACTOR
        cement_part, sand_part = self.get_mortar_parts()
        total_parts = cement_part + sand_part
        cement_volume = dry * cement_part / total_parts
        sand_volume = dry * sand_part / total_parts
        cement_bags = self.cement_bags(cement_volume)
        return dry, cement_volume, cement_bags, sand_volume

    def calculate(self) -> CalculationResult:
        wall_volume_m3 = self.calculate_wall_volume()

        base_bricks, bricks = self.calculate_brick_quantity(wall_volume_m3)
        mortar_m3 = self.calculate_mortar_volume(
            wall_volume_m3,
            base_bricks,
        )
        dry_mortar_m3, cement_m3, cement_bags, sand_m3 = (
            self.calculate_mortar_materials(mortar_m3)
        )

        factor = 1.0 if self.volume_unit == "m³" else self.CFT_TO_M3

        quantity = wall_volume_m3 / factor
        mortar_volume = mortar_m3 / factor
        dry_mortar_volume = dry_mortar_m3 / factor
        sand_volume = sand_m3 / factor
        cement_volume = cement_m3 / factor

        self.result.calculator = "Brickwork"
        self.result.description = f"Brickwork ({self.mortar_ratio})"
        self.result.unit = self.volume_unit
        self.result.quantity = quantity
        self.result.wet_volume = quantity
        self.result.cement_volume = cement_volume
        self.result.cement_bags = cement_bags
        self.result.sand_volume = sand_volume

        brick_l, brick_w, brick_h = self.get_brick_dimensions()

        values = {
            "length": self.length,
            "height": self.height,
            "thickness": self.thickness,
            "dimension_unit": "m" if self.volume_unit == "m³" else "ft",
            "volume_unit": self.volume_unit,
            "wall_volume": quantity,
            "metric_wall_volume_m3": wall_volume_m3,
            "brick_size": self.brick_size,
            "brick_length": brick_l,
            "brick_width": brick_w,
            "brick_height": brick_h,
            "brick_volume": self.calculate_brick_volume(),
            "nominal_brick_volume": self.calculate_nominal_brick_volume(),
            "base_brick_quantity": base_bricks,
            "brick_quantity": bricks,
            "waste_percent": self.waste_percent,
            "mortar_ratio": self.mortar_ratio,
            "mortar_joint": self.MORTAR_JOINT,
            "mortar_volume": mortar_volume,
            "dry_mortar_volume": dry_mortar_volume,
            "cement_volume": cement_volume,
            "cement_bags": cement_bags,
            "sand_volume": sand_volume,
        }
        for key, value in values.items():
            self.result.add_value(key, value)

        return self.result


__all__ = ["BrickworkCalculator"]
