"""
Civil Estimate Suite Pro v4.0
Labour Norm Service

Central catalogue for productivity-based labour calculation.

Important:
- Existing calculator productivity defaults are preserved.
- Norms are editable data, not hard-coded calculation logic.
- Steel/rebar calculators are intentionally marked manual until the
  engineer defines project/company-specific productivity norms.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class LabourNorm:
    calculator: str
    work_item: str
    quantity_unit: str
    skilled_productivity: float | None
    unskilled_productivity: float | None
    productivity_unit: str
    source: str = "Application default; engineer may override"


class LabourNormService:
    """
    Provides the default productivity norms used by calculators.

    Productivity means:
        quantity completed per labour day

    Labour days:
        quantity / productivity
    """

    DEFAULTS = {
        "pcc": LabourNorm(
            "PCC", "PCC concrete", "m³", 1.0, 2.0, "m³/day"
        ),
        "rcc": LabourNorm(
            "RCC", "RCC concrete", "m³", 1.0, 2.0, "m³/day"
        ),
        "brickwork": LabourNorm(
            "Brickwork", "Brick masonry", "m³", 10.0, 15.0, "m³/day"
        ),
        "plaster": LabourNorm(
            "Plaster", "Plaster work", "m²", 10.0, 15.0, "m²/day"
        ),
        "excavation": LabourNorm(
            "Excavation", "Excavation", "m³", 8.0, 6.0, "m³/day"
        ),
        "footing": LabourNorm(
            "Footing", "Footing concrete", "m³", None, None, "m³/day",
            source="Use engineer-entered footing productivity"
        ),
        "staircase": LabourNorm(
            "Staircase", "Staircase concrete", "m³", None, None, "m³/day",
            source="Use engineer-entered staircase productivity"
        ),
        "steel": LabourNorm(
            "Steel", "General reinforcement", "kg", None, None, "kg/day",
            source="Use engineer/company-specific steel productivity"
        ),
        "slab_steel": LabourNorm(
            "Slab Steel", "Slab reinforcement", "kg", None, None, "kg/day",
            source="Use engineer/company-specific steel productivity"
        ),
        "column_steel": LabourNorm(
            "Column Steel", "Column reinforcement", "kg", None, None, "kg/day",
            source="Use engineer/company-specific steel productivity"
        ),
        "beam_steel": LabourNorm(
            "Beam Steel", "Beam reinforcement", "kg", None, None, "kg/day",
            source="Use engineer/company-specific steel productivity"
        ),
    }

    def __init__(self, overrides: dict[str, dict[str, Any]] | None = None):
        self._norms = dict(self.DEFAULTS)
        for key, values in (overrides or {}).items():
            self.set_norm(key, **values)

    @classmethod
    def normalize_key(cls, calculator: str) -> str:
        key = str(calculator or "").strip().lower()
        aliases = {
            "pcc calculator": "pcc",
            "rcc calculator": "rcc",
            "brick": "brickwork",
            "brickwork calculator": "brickwork",
            "plaster calculator": "plaster",
            "excavation calculator": "excavation",
            "footing / foundation": "footing",
            "footing / foundation calculator": "footing",
            "staircase calculator": "staircase",
            "steel / rebar": "steel",
            "steel/rebar": "steel",
            "slab steel / rebar": "slab_steel",
            "column steel / rebar": "column_steel",
            "beam steel / rebar": "beam_steel",
        }
        return aliases.get(key, key)

    def get(self, calculator: str) -> LabourNorm:
        key = self.normalize_key(calculator)
        if key not in self._norms:
            raise KeyError(f"No labour norm registered for '{calculator}'.")
        return self._norms[key]

    def set_norm(
        self,
        calculator: str,
        *,
        work_item: str | None = None,
        quantity_unit: str | None = None,
        skilled_productivity: float | None = None,
        unskilled_productivity: float | None = None,
        productivity_unit: str | None = None,
        source: str | None = None,
    ) -> LabourNorm:
        key = self.normalize_key(calculator)
        current = self._norms.get(key)

        norm = LabourNorm(
            calculator=(
                current.calculator if current else str(calculator).strip()
            ),
            work_item=(
                work_item if work_item is not None
                else (current.work_item if current else "")
            ),
            quantity_unit=(
                quantity_unit if quantity_unit is not None
                else (current.quantity_unit if current else "")
            ),
            skilled_productivity=(
                skilled_productivity
                if skilled_productivity is not None
                else (current.skilled_productivity if current else None)
            ),
            unskilled_productivity=(
                unskilled_productivity
                if unskilled_productivity is not None
                else (current.unskilled_productivity if current else None)
            ),
            productivity_unit=(
                productivity_unit
                if productivity_unit is not None
                else (current.productivity_unit if current else "")
            ),
            source=(
                source if source is not None
                else (current.source if current else "Engineer defined")
            ),
        )

        for value, label in (
            (norm.skilled_productivity, "skilled productivity"),
            (norm.unskilled_productivity, "unskilled productivity"),
        ):
            if value is not None and float(value) <= 0:
                raise ValueError(f"{label} must be greater than zero.")

        self._norms[key] = norm
        return norm

    def calculate_days(
        self,
        calculator: str,
        quantity: float,
        skilled_productivity: float | None = None,
        unskilled_productivity: float | None = None,
    ) -> dict[str, float | None]:
        quantity = float(quantity)
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")

        norm = self.get(calculator)

        skilled = (
            skilled_productivity
            if skilled_productivity is not None
            else norm.skilled_productivity
        )
        unskilled = (
            unskilled_productivity
            if unskilled_productivity is not None
            else norm.unskilled_productivity
        )

        def days(qty, productivity):
            if productivity is None:
                return None
            productivity = float(productivity)
            if productivity <= 0:
                raise ValueError("Productivity must be greater than zero.")
            return round(qty / productivity, 3)

        return {
            "skilled_days": days(quantity, skilled),
            "unskilled_days": days(quantity, unskilled),
            "skilled_productivity": skilled,
            "unskilled_productivity": unskilled,
            "productivity_unit": norm.productivity_unit,
        }

    def all_norms(self) -> list[dict[str, Any]]:
        return [asdict(norm) for norm in self._norms.values()]


__all__ = ["LabourNorm", "LabourNormService"]
