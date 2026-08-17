from __future__ import annotations

from services.unit_conversion_service import (
    UnitConversionError,
    UnitConversionService,
)


class UnitQuantityService:
    """Unit-safe quantity/rate conversion for civil-estimation workflows."""

    @staticmethod
    def _num(value):
        try:
            return float(value or 0)
        except (TypeError, ValueError) as exc:
            raise ValueError("Quantity/rate must be numeric.") from exc

    @classmethod
    def convert_quantity(cls, quantity, from_unit, to_unit):
        return UnitConversionService.convert(
            cls._num(quantity), from_unit, to_unit
        )

    @classmethod
    def quantity_record(cls, quantity, unit, target_unit=None, decimals=6):
        qty = cls._num(quantity)
        target = target_unit or unit
        converted = qty if target == unit else cls.convert_quantity(
            qty, unit, target
        )
        return {
            "quantity": round(converted, decimals),
            "unit": target,
            "source_quantity": qty,
            "source_unit": unit,
        }

    @classmethod
    def rate_for_quantity_unit(cls, rate, rate_unit, quantity_unit):
        """Convert a rate denominator to the BOQ quantity unit."""
        value = cls._num(rate)
        if rate_unit == quantity_unit:
            return value
        factor = UnitConversionService.convert(
            1.0, quantity_unit, rate_unit
        )
        return value * factor

    @classmethod
    def cost(cls, quantity, quantity_unit, rate, rate_unit=None):
        normalized_rate = cls.rate_for_quantity_unit(
            rate, rate_unit or quantity_unit, quantity_unit
        )
        return cls._num(quantity) * normalized_rate

    @classmethod
    def format(cls, quantity, unit, decimals=3):
        return f"{cls._num(quantity):,.{int(decimals)}f} {unit}"


__all__ = ["UnitQuantityService", "UnitConversionError"]
