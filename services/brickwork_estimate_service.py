"""
Civil Estimate Suite Pro v4.0
Brickwork Estimate Service

Builds the detailed, auditable analysis used by:
    Calculator -> BOQ -> Material -> Reports
"""
from __future__ import annotations

from typing import Any


class BrickworkEstimateService:
    """Build transparent brickwork material and labour analysis."""

    @staticmethod
    def build_analysis(
        result: Any,
        material_rates: dict[str, float],
        skilled_days: float,
        skilled_rate: float,
        unskilled_days: float,
        unskilled_rate: float,
    ) -> dict:
        if result is None:
            raise ValueError("Brickwork calculation result is required.")

        def non_negative(value, label):
            try:
                number = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{label} must be numeric.") from exc
            if number < 0:
                raise ValueError(f"{label} cannot be negative.")
            return number

        def positive(value, label):
            number = non_negative(value, label)
            if number <= 0:
                raise ValueError(f"{label} must be greater than zero.")
            return number

        def rate(name):
            return non_negative(material_rates.get(name, 0), f"{name} rate")

        skilled_days = non_negative(skilled_days, "Skilled labour days")
        skilled_rate = non_negative(skilled_rate, "Skilled labour rate")
        unskilled_days = non_negative(unskilled_days, "Unskilled labour days")
        unskilled_rate = non_negative(unskilled_rate, "Unskilled labour rate")

        volume_unit = str(
            result.get_value("volume_unit", result.unit or "m³")
        )
        dimension_unit = str(
            result.get_value(
                "dimension_unit",
                "m" if volume_unit == "m³" else "ft",
            )
        )

        quantity = positive(result.quantity, "Brickwork quantity")

        materials = [
            {
                "name": "Bricks",
                "unit": "Nos",
                "quantity": round(
                    float(result.get_value("brick_quantity", 0)),
                    2,
                ),
                "rate": round(rate("brick"), 2),
            },
            {
                "name": "Cement",
                "unit": "Bags",
                "quantity": round(float(result.cement_bags), 3),
                "rate": round(rate("cement_bag"), 2),
            },
            {
                "name": "Sand",
                "unit": volume_unit,
                "quantity": round(float(result.sand_volume), 3),
                "rate": round(rate("sand"), 2),
            },
        ]

        for item in materials:
            item["amount"] = round(
                item["quantity"] * item["rate"],
                2,
            )

        material_total = round(
            sum(item["amount"] for item in materials),
            2,
        )

        labour = [
            {
                "name": "Skilled Labour",
                "unit": "day",
                "quantity": round(skilled_days, 2),
                "rate": round(skilled_rate, 2),
            },
            {
                "name": "Unskilled Labour",
                "unit": "day",
                "quantity": round(unskilled_days, 2),
                "rate": round(unskilled_rate, 2),
            },
        ]

        for item in labour:
            item["amount"] = round(
                item["quantity"] * item["rate"],
                2,
            )

        labour_total = round(
            sum(item["amount"] for item in labour),
            2,
        )

        total_cost = round(material_total + labour_total, 2)
        unit_rate = round(total_cost / quantity, 2)

        return {
            "version": 1,
            "calculator": "Brickwork",
            "description": result.description,
            "unit": volume_unit,
            "dimensions": {
                "length": float(result.get_value("length", 0)),
                "height": float(result.get_value("height", 0)),
                "thickness": float(result.get_value("thickness", 0)),
                "dimension_unit": dimension_unit,
            },
            "brick_size": result.get_value("brick_size", "Standard"),
            "brick_dimensions_m": {
                "length": float(result.get_value("brick_length", 0)),
                "width": float(result.get_value("brick_width", 0)),
                "height": float(result.get_value("brick_height", 0)),
            },
            "mortar_ratio": result.get_value("mortar_ratio", ""),
            "waste_percent": float(result.get_value("waste_percent", 0)),
            "quantity": round(quantity, 3),
            "wall_volume": round(
                float(result.get_value("wall_volume", quantity)),
                3,
            ),
            "mortar_volume": round(
                float(result.get_value("mortar_volume", 0)),
                3,
            ),
            "dry_mortar_volume": round(
                float(result.get_value("dry_mortar_volume", 0)),
                3,
            ),
            "materials": materials,
            "material_total": material_total,
            "labour": labour,
            "labour_total": labour_total,
            "total_cost": total_cost,
            "unit_rate": unit_rate,
        }


__all__ = ["BrickworkEstimateService"]
