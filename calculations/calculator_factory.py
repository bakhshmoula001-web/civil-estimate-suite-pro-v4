"""
Civil Estimate Suite Pro v4.0
Calculator Factory
Central registry for all engineering calculators.
"""

from __future__ import annotations

from typing import Any

from calculations.pcc_calculator import PCCCalculator
from calculations.rcc_calculator import RCCCalculator
from calculations.brickwork_calculator import BrickworkCalculator
from calculations.excavation_calculator import ExcavationCalculator
from calculations.plaster_calculator import PlasterCalculator
from calculations.steel_calculator import SteelCalculator
from calculations.slab_steel_calculator import SlabSteelCalculator
from calculations.column_steel_calculator import ColumnSteelCalculator
from calculations.beam_steel_calculator import BeamSteelCalculator
from calculations.footing_calculator import FootingCalculator
from calculations.staircase_calculator import StaircaseCalculator


class CalculatorFactory:
    """Central factory for every calculator exposed by the application."""

    _calculators = {
        "PCC": PCCCalculator,
        "RCC": RCCCalculator,
        "BRICKWORK": BrickworkCalculator,
        "EXCAVATION": ExcavationCalculator,
        "PLASTER": PlasterCalculator,
        "STEEL": SteelCalculator,
        "SLAB_STEEL": SlabSteelCalculator,
        "COLUMN_STEEL": ColumnSteelCalculator,
        "BEAM_STEEL": BeamSteelCalculator,
        "FOOTING": FootingCalculator,
        "STAIRCASE": StaircaseCalculator,
    }

    _display_names = {
        "PCC": "PCC",
        "RCC": "RCC",
        "BRICKWORK": "Brickwork",
        "EXCAVATION": "Excavation",
        "PLASTER": "Plaster",
        "STEEL": "Steel Weight",
        "SLAB_STEEL": "Slab Steel",
        "COLUMN_STEEL": "Column Steel",
        "BEAM_STEEL": "Beam Steel",
        "FOOTING": "Footing / Foundation",
        "STAIRCASE": "Staircase",
    }

    _aliases = {
        "PCC": "PCC",
        "PCC_CALCULATOR": "PCC",
        "RCC": "RCC",
        "RCC_CALCULATOR": "RCC",
        "BRICKWORK": "BRICKWORK",
        "BRICK_WORK": "BRICKWORK",
        "BRICKWORK_CALCULATOR": "BRICKWORK",
        "EXCAVATION": "EXCAVATION",
        "EXCAVATION_CALCULATOR": "EXCAVATION",
        "EARTHWORK": "EXCAVATION",
        "PLASTER": "PLASTER",
        "PLASTER_CALCULATOR": "PLASTER",
        "STEEL": "STEEL",
        "STEEL_WEIGHT": "STEEL",
        "STEEL_CALCULATOR": "STEEL",
        "SLAB_STEEL": "SLAB_STEEL",
        "SLAB_REBAR": "SLAB_STEEL",
        "SLAB_STEEL_CALCULATOR": "SLAB_STEEL",
        "COLUMN_STEEL": "COLUMN_STEEL",
        "COLUMN_REBAR": "COLUMN_STEEL",
        "COLUMN_STEEL_CALCULATOR": "COLUMN_STEEL",
        "BEAM_STEEL": "BEAM_STEEL",
        "BEAM_REBAR": "BEAM_STEEL",
        "BEAM_STEEL_CALCULATOR": "BEAM_STEEL",
        "FOOTING": "FOOTING",
        "FOUNDATION": "FOOTING",
        "FOOTING_FOUNDATION": "FOOTING",
        "FOOTING_CALCULATOR": "FOOTING",
        "STAIRCASE": "STAIRCASE",
        "STAIRCASE_CALCULATOR": "STAIRCASE",
        "STAIR": "STAIRCASE",
    }

    @classmethod
    def _normalize(cls, calculator_type: str) -> str:
        if calculator_type is None:
            raise ValueError("Calculator type is required.")

        value = str(calculator_type).strip().upper()
        if value.endswith(" CALCULATOR"):
            value = value[:-len(" CALCULATOR")].strip()

        value = value.replace("-", "_").replace(" ", "_")
        return cls._aliases.get(value, value)

    @classmethod
    def create(cls, calculator_type: str, **kwargs: Any):
        key = cls._normalize(calculator_type)
        calculator_class = cls._calculators.get(key)

        if calculator_class is None:
            available = ", ".join(cls.display_names())
            raise ValueError(
                f"Calculator '{calculator_type}' not found. "
                f"Available: {available}"
            )

        return calculator_class(**kwargs)

    @classmethod
    def available(cls) -> list[str]:
        return list(cls._calculators.keys())

    @classmethod
    def display_names(cls) -> list[str]:
        return [cls._display_names[key] for key in cls._calculators]

    @classmethod
    def exists(cls, calculator_type: str) -> bool:
        try:
            return cls._normalize(calculator_type) in cls._calculators
        except ValueError:
            return False

    @classmethod
    def register(cls, name: str, calculator_class) -> None:
        key = cls._normalize(name)
        cls._calculators[key] = calculator_class

    @classmethod
    def unregister(cls, name: str) -> None:
        cls._calculators.pop(cls._normalize(name), None)


__all__ = ["CalculatorFactory"]
