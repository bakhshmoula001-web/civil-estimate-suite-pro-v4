"""
Civil Estimate Suite Pro v4.0
Column Steel / Reinforcement Calculator
"""
from __future__ import annotations
from calculations.base_calculator import BaseCalculator


class ColumnSteelCalculator(BaseCalculator):
    STEEL_DENSITY_KG_M3 = 7850.0

    def __init__(
        self,
        column_length,
        column_width,
        column_height,
        cover_mm,
        vertical_dia_mm,
        vertical_bars,
        vertical_lap_length_m=0.0,
        vertical_laps=0,
        stirrup_dia_mm=8.0,
        stirrup_spacing_mm=150.0,
        stirrup_hook_extra_mm=200.0,
        cutting_allowance_percent=2.0,
        binding_wire_percent=2.0,
        steel_rate=0.0,
        column_count=1,
        length_unit="m",
    ):
        super().__init__()
        self.unit = self._unit(length_unit)
        if self.unit not in {"m", "ft"}:
            raise ValueError("Length unit must be m or ft.")

        self.L = self.positive(column_length, "Column length")
        self.W = self.positive(column_width, "Column width")
        self.H = self.positive(column_height, "Column height")
        self.cover = self.non_negative(cover_mm, "Clear cover")
        self.vdia = self.positive(vertical_dia_mm, "Vertical bar diameter")
        self.vbars = self.non_negative_int(vertical_bars, "Vertical bars")
        if self.vbars < 4:
            raise ValueError("Column requires at least 4 vertical bars.")
        self.vlap = self.non_negative(vertical_lap_length_m, "Vertical lap length")
        self.vlaps = self.non_negative_int(vertical_laps, "Vertical laps")
        self.sdia = self.positive(stirrup_dia_mm, "Stirrup diameter")
        self.spacing = self.positive(stirrup_spacing_mm, "Stirrup spacing")
        self.hook = self.non_negative(stirrup_hook_extra_mm, "Stirrup hook allowance")
        self.cutting = self.non_negative(cutting_allowance_percent, "Cutting allowance")
        self.binding = self.non_negative(binding_wire_percent, "Binding wire")
        self.rate = self.non_negative(steel_rate, "Steel rate")
        self.count = self.non_negative_int(column_count, "Column count")
        if self.count < 1:
            raise ValueError("Column count must be at least 1.")

    @staticmethod
    def _unit(unit):
        v = str(unit or "m").strip().lower()
        return {"m": "m", "meter": "m", "metre": "m",
                "ft": "ft", "feet": "ft"}.get(v, str(unit).strip())

    @staticmethod
    def non_negative_int(value, label):
        try:
            n = int(float(value))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{label} must be a whole number.") from exc
        if n < 0:
            raise ValueError(f"{label} cannot be negative.")
        return n

    def _m(self, value):
        return value if self.unit == "m" else value * 0.3048

    @staticmethod
    def _kg_per_m(dia):
        d = dia / 1000.0
        return 3.141592653589793 * d * d / 4.0 * 7850.0

    def calculate(self):
        L = self._m(self.L)
        W = self._m(self.W)
        H = self._m(self.H)
        cover_m = self.cover / 1000.0

        # Vertical bars include the specified lap/splice allowance.
        vertical_length_each = H + self.vlap * self.vlaps
        vertical_base_length = vertical_length_each * self.vbars * self.count
        vertical_kg = vertical_base_length * self._kg_per_m(self.vdia)

        # Centerline stirrup dimensions after cover.
        center_L = max(0.0, L - 2 * cover_m)
        center_W = max(0.0, W - 2 * cover_m)
        stirrup_cut_m = (
            2 * center_L + 2 * center_W
            + (self.hook / 1000.0)
        )
        stirrup_count_one = max(1, int((H * 1000.0) / self.spacing) + 1)
        stirrup_total_count = stirrup_count_one * self.count
        stirrup_length = stirrup_cut_m * stirrup_total_count
        stirrup_kg = stirrup_length * self._kg_per_m(self.sdia)

        base_kg = vertical_kg + stirrup_kg
        cutting_kg = base_kg * self.cutting / 100.0
        total_kg = base_kg + cutting_kg
        binding_kg = total_kg * self.binding / 100.0
        amount = total_kg * self.rate

        r = self.result
        r.calculator = "Column Steel"
        r.description = "Column Reinforcement Steel"
        r.unit = "kg"
        r.quantity = total_kg

        values = {
            "column_length": self.L,
            "column_width": self.W,
            "column_height": self.H,
            "column_count": self.count,
            "length_unit": self.unit,
            "cover_mm": self.cover,
            "vertical_dia_mm": self.vdia,
            "vertical_bars": self.vbars,
            "vertical_length_each_m": vertical_length_each,
            "vertical_total_length_m": vertical_base_length,
            "vertical_kg": vertical_kg,
            "vertical_lap_length_m": self.vlap,
            "vertical_laps": self.vlaps,
            "stirrup_dia_mm": self.sdia,
            "stirrup_spacing_mm": self.spacing,
            "stirrup_count_one": stirrup_count_one,
            "stirrup_total_count": stirrup_total_count,
            "stirrup_cutting_length_m": stirrup_cut_m,
            "stirrup_total_length_m": stirrup_length,
            "stirrup_kg": stirrup_kg,
            "base_steel_kg": base_kg,
            "cutting_allowance_percent": self.cutting,
            "cutting_kg": cutting_kg,
            "steel_kg": total_kg,
            "binding_wire_percent": self.binding,
            "binding_wire_kg": binding_kg,
            "steel_rate": self.rate,
            "steel_amount": amount,
        }
        for k, v in values.items():
            r.add_value(k, v)
        return r


__all__ = ["ColumnSteelCalculator"]
