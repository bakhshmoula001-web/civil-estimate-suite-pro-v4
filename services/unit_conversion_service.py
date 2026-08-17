"""
Civil Estimate Suite Pro v4.0
Engineering Unit Conversion Service

Purpose:
    Keep CFT and m³ (and other common civil-engineering units)
    interchangeable without changing the original calculated quantity.

Design:
    - User-selected display unit remains optional.
    - Calculators may store a native quantity/unit.
    - Reports can display the selected unit.
    - Conversion is deterministic and reversible.
"""

from __future__ import annotations


class UnitConversionError(ValueError):
    """Raised when an unsupported or incompatible unit is requested."""


class UnitConversionService:
    # Conversion factors to a canonical unit for each measurement family.
    # Volume canonical = m3
    # Area canonical   = m2
    # Length canonical = m
    # Weight canonical = kg
    # Time canonical   = day
    _FACTORS = {
        "volume": {
            "m3": 1.0,
            "m³": 1.0,
            "cum": 1.0,
            "cubic meter": 1.0,
            "cubic metre": 1.0,
            "cft": 0.028316846592,
            "ft3": 0.028316846592,
            "ft³": 0.028316846592,
            "cuft": 0.028316846592,
            "cubic feet": 0.028316846592,
            "cubic foot": 0.028316846592,
            "liter": 0.001,
            "litre": 0.001,
            "l": 0.001,
        },
        "area": {
            "m2": 1.0,
            "m²": 1.0,
            "sqm": 1.0,
            "sqft": 0.09290304,
            "ft2": 0.09290304,
            "ft²": 0.09290304,
            "sq ft": 0.09290304,
        },
        "length": {
            "m": 1.0,
            "meter": 1.0,
            "metre": 1.0,
            "ft": 0.3048,
            "feet": 0.3048,
            "inch": 0.0254,
            "in": 0.0254,
            "mm": 0.001,
            "cm": 0.01,
        },
        "weight": {
            "kg": 1.0,
            "kilogram": 1.0,
            "ton": 1000.0,
            "tonne": 1000.0,
            "mt": 1000.0,
            "lb": 0.45359237,
        },
        "time": {
            "day": 1.0,
            "days": 1.0,
            "hr": 1.0 / 8.0,
            "hour": 1.0 / 8.0,
            "hours": 1.0 / 8.0,
        },
    }

    _DISPLAY = {
        "volume": ("Cft", "m³"),
        "area": ("Sqft", "m²"),
        "length": ("ft", "m"),
        "weight": ("kg", "ton"),
        "time": ("day", "hr"),
    }

    @classmethod
    def _normalise(cls, unit):
        return str(unit or "").strip().lower().replace(" ", " ")

    @classmethod
    def family_for(cls, unit):
        key = cls._normalise(unit)
        for family, units in cls._FACTORS.items():
            if key in units:
                return family
        raise UnitConversionError(f"Unsupported unit: {unit}")

    @classmethod
    def convert(cls, value, from_unit, to_unit):
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise UnitConversionError("Quantity must be numeric.") from exc

        from_key = cls._normalise(from_unit)
        to_key = cls._normalise(to_unit)

        from_family = cls.family_for(from_key)
        to_family = cls.family_for(to_key)

        if from_family != to_family:
            raise UnitConversionError(
                f"Incompatible units: {from_unit} → {to_unit}"
            )

        canonical = number * cls._FACTORS[from_family][from_key]
        result = canonical / cls._FACTORS[to_family][to_key]
        return result

    @classmethod
    def convert_volume(cls, value, from_unit, to_unit):
        if cls.family_for(from_unit) != "volume":
            raise UnitConversionError(f"{from_unit} is not a volume unit.")
        if cls.family_for(to_unit) != "volume":
            raise UnitConversionError(f"{to_unit} is not a volume unit.")
        return cls.convert(value, from_unit, to_unit)

    @classmethod
    def available_units(cls, family):
        family_key = str(family or "").strip().lower()
        if family_key not in cls._FACTORS:
            raise UnitConversionError(f"Unsupported unit family: {family}")
        return tuple(cls._DISPLAY.get(family_key, cls._FACTORS[family_key].keys()))

    @classmethod
    def preferred_units(cls, family):
        return cls.available_units(family)

    @classmethod
    def unit_options(cls):
        return {
            family: cls.available_units(family)
            for family in cls._FACTORS
        }

    @classmethod
    def format_quantity(cls, value, unit, decimals=3):
        converted = float(value)
        return f"{converted:,.{int(decimals)}f} {unit}"

    @classmethod
    def convert_with_label(cls, value, from_unit, to_unit, decimals=3):
        result = cls.convert(value, from_unit, to_unit)
        return cls.format_quantity(result, to_unit, decimals)


__all__ = ["UnitConversionService", "UnitConversionError"]
