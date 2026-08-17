"""
Civil Estimate Suite Pro v4.0
Steel / Rebar Calculator
"""
from __future__ import annotations

from calculations.base_calculator import BaseCalculator
from calculations.calculation_result import CalculationResult


class SteelCalculator(BaseCalculator):
    """Bar-wise reinforcement steel quantity and weight calculator."""

    DIAMETER_MM = (8, 10, 12, 16, 20, 25, 32, 40)
    STEEL_DENSITY_KG_M3 = 7850.0
    CFT_TO_M3 = 0.028316846592

    def __init__(
        self,
        diameter_mm: float,
        number_of_bars: int = 0,
        bar_length: float = 0.0,
        spacing_mm: float = 0.0,
        distribution_length: float = 0.0,
        cutting_allowance_percent: float = 0.0,
        lap_length: float = 0.0,
        laps_per_bar: int = 0,
        binding_wire_percent: float = 2.0,
        length_unit: str = "m",
        steel_rate: float = 0.0,
    ):
        super().__init__()

        self.diameter_mm = self.positive(
            diameter_mm, "Bar diameter"
        )

        self.number_of_bars = self.non_negative_int(
            number_of_bars, "Number of bars"
        )
        self.bar_length = self.non_negative(
            bar_length, "Bar length"
        )
        self.spacing_mm = self.non_negative(
            spacing_mm, "Spacing"
        )
        self.distribution_length = self.non_negative(
            distribution_length, "Distribution length"
        )
        self.cutting_allowance_percent = self.non_negative(
            cutting_allowance_percent,
            "Cutting allowance",
        )
        self.lap_length = self.non_negative(
            lap_length,
            "Lap length",
        )
        self.laps_per_bar = self.non_negative_int(
            laps_per_bar,
            "Laps per bar",
        )
        self.binding_wire_percent = self.non_negative(
            binding_wire_percent,
            "Binding wire percentage",
        )
        self.length_unit = self.normalize_unit(length_unit)
        self.steel_rate = self.non_negative(
            steel_rate,
            "Steel rate",
        )

        if self.length_unit not in {"m", "ft"}:
            raise ValueError("Length unit must be m or ft.")

        if self.number_of_bars == 0 and self.spacing_mm <= 0:
            raise ValueError(
                "Enter either Number of Bars or Spacing."
            )

        if self.number_of_bars == 0 and self.distribution_length <= 0:
            raise ValueError(
                "Distribution length is required when using spacing."
            )

        if self.number_of_bars > 0 and self.bar_length <= 0:
            raise ValueError(
                "Bar length is required when Number of Bars is used."
            )

    @staticmethod
    def normalize_unit(unit: str) -> str:
        value = str(unit or "m").strip().lower()
        return {
            "m": "m",
            "meter": "m",
            "metre": "m",
            "ft": "ft",
            "feet": "ft",
        }.get(value, str(unit).strip())

    @staticmethod
    def non_negative_int(value, label):
        try:
            number = int(float(value))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{label} must be a whole number."
            ) from exc
        if number < 0:
            raise ValueError(f"{label} cannot be negative.")
        return number

    def _length_m(self, value: float) -> float:
        return value if self.length_unit == "m" else value * 0.3048

    def _bars_from_spacing(self) -> int:
        if self.spacing_mm <= 0:
            return 0
        if self.distribution_length <= 0:
            raise ValueError(
                "Distribution length is required for spacing calculation."
            )
        length_m = self._length_m(self.distribution_length)
        return max(
            1,
            int((length_m * 1000) / self.spacing_mm) + 1,
        )

    def calculate(self) -> CalculationResult:
        spacing_bars = self._bars_from_spacing()

        if self.number_of_bars > 0:
            main_bars = self.number_of_bars
            base_length = self._length_m(self.bar_length)
        else:
            main_bars = spacing_bars
            base_length = self._length_m(self.distribution_length)

        lap_total_m = self.lap_length * self.laps_per_bar
        total_base_length_m = (
            main_bars * base_length
            + main_bars * self._length_m(lap_total_m)
        )

        cutting_extra_m = (
            total_base_length_m
            * self.cutting_allowance_percent
            / 100.0
        )
        total_length_m = total_base_length_m + cutting_extra_m

        diameter_m = self.diameter_mm / 1000.0
        weight_per_m = (
            3.141592653589793
            * diameter_m ** 2
            / 4.0
            * self.STEEL_DENSITY_KG_M3
        )
        steel_kg = total_length_m * weight_per_m
        binding_wire_kg = (
            steel_kg * self.binding_wire_percent / 100.0
        )
        amount = steel_kg * self.steel_rate

        r = self.result
        r.calculator = "Steel"
        r.description = (
            f"Reinforcement Steel Ø{self.diameter_mm:g} mm"
        )
        r.unit = "kg"
        r.quantity = steel_kg

        values = {
            "diameter_mm": self.diameter_mm,
            "bar_count": main_bars,
            "bars_from_spacing": spacing_bars,
            "bar_length": self.bar_length,
            "spacing_mm": self.spacing_mm,
            "distribution_length": self.distribution_length,
            "lap_length": self.lap_length,
            "laps_per_bar": self.laps_per_bar,
            "cutting_allowance_percent": self.cutting_allowance_percent,
            "base_length_m": base_length,
            "lap_total_m": lap_total_m,
            "cutting_extra_m": cutting_extra_m,
            "total_length_m": total_length_m,
            "weight_per_m": weight_per_m,
            "steel_kg": steel_kg,
            "binding_wire_percent": self.binding_wire_percent,
            "binding_wire_kg": binding_wire_kg,
            "steel_rate": self.steel_rate,
            "steel_amount": amount,
            "length_unit": self.length_unit,
        }
        for key, value in values.items():
            r.add_value(key, value)

        return r


__all__ = ["SteelCalculator"]
