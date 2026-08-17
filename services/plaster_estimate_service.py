"""
Civil Estimate Suite Pro v4.0
Plaster Estimate Service
"""
from __future__ import annotations


class PlasterEstimateService:
    """Build an auditable plaster material/labour cost analysis."""

    @staticmethod
    def build_analysis(
        result,
        material_rates: dict[str, float],
        skilled_days: float,
        skilled_rate: float,
        unskilled_days: float,
        unskilled_rate: float,
    ) -> dict:
        def non_negative(value, label):
            try:
                number = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{label} must be numeric.") from exc
            if number < 0:
                raise ValueError(f"{label} cannot be negative.")
            return number

        quantity = float(result.quantity)
        if quantity <= 0:
            raise ValueError("Plaster quantity must be greater than zero.")

        def rate(key, label):
            return non_negative(material_rates.get(key, 0), label)

        materials = [
            {
                "name": "Cement",
                "unit": "Bags",
                "quantity": round(float(result.cement_bags), 3),
                "rate": round(rate("cement_bag", "Cement rate"), 2),
            },
            {
                "name": "Sand",
                "unit": result.unit.replace("Sft", "Cft") if result.unit == "Sft" else "m³",
                "quantity": round(float(result.get_value("sand_quantity", 0)), 3),
                "rate": round(rate("sand", "Sand rate"), 2),
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

        skilled_days = non_negative(skilled_days, "Skilled labour days")
        skilled_rate = non_negative(skilled_rate, "Skilled labour rate")
        unskilled_days = non_negative(
            unskilled_days,
            "Unskilled labour days",
        )
        unskilled_rate = non_negative(
            unskilled_rate,
            "Unskilled labour rate",
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
            "calculator": "Plaster",
            "description": result.description,
            "unit": result.unit,
            "dimensions": {
                "length": float(result.get_value("length", 0)),
                "height": float(result.get_value("height", 0)),
                "dimension_unit": result.get_value(
                    "dimension_unit",
                    "m",
                ),
            },
            "thickness_mm": float(
                result.get_value("thickness_mm", 0)
            ),
            "surfaces": int(
                result.get_value("surfaces", 1)
            ),
            "mortar_ratio": result.get_value(
                "mortar_ratio",
                "",
            ),
            "quantity": round(quantity, 3),
            "wet_mortar_m3": round(
                float(result.get_value("wet_mortar_m3", 0)),
                3,
            ),
            "dry_mortar_m3": round(
                float(result.get_value("dry_mortar_m3", 0)),
                3,
            ),
            "materials": materials,
            "material_total": material_total,
            "labour": labour,
            "labour_total": labour_total,
            "total_cost": total_cost,
            "unit_rate": unit_rate,
        }


__all__ = ["PlasterEstimateService"]
