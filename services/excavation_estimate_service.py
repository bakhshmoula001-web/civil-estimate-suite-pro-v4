"""
Civil Estimate Suite Pro v4.0
Excavation Estimate Service
"""
from __future__ import annotations


class ExcavationEstimateService:
    """Build detailed excavation material/labour/cost analysis."""

    @staticmethod
    def build_analysis(
        result,
        skilled_days: float,
        skilled_rate: float,
        unskilled_days: float,
        unskilled_rate: float,
        disposal_distance_m: float = 0.0,
        disposal_rate_per_m3: float = 0.0,
    ) -> dict:
        def non_negative(value, label):
            try:
                number = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"{label} must be numeric."
                ) from exc
            if number < 0:
                raise ValueError(
                    f"{label} cannot be negative."
                )
            return number

        quantity = float(result.quantity)
        if quantity <= 0:
            raise ValueError(
                "Excavation quantity must be greater than zero."
            )

        skilled_days = non_negative(
            skilled_days,
            "Skilled labour days",
        )
        skilled_rate = non_negative(
            skilled_rate,
            "Skilled labour rate",
        )
        unskilled_days = non_negative(
            unskilled_days,
            "Unskilled labour days",
        )
        unskilled_rate = non_negative(
            unskilled_rate,
            "Unskilled labour rate",
        )

        disposal_distance_m = non_negative(
            disposal_distance_m,
            "Disposal distance",
        )
        disposal_rate_per_m3 = non_negative(
            disposal_rate_per_m3,
            "Disposal rate",
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

        spoil_quantity = float(
            result.get_value(
                "spoil_quantity",
                quantity,
            )
        )

        disposal_amount = round(
            (spoil_quantity if disposal_distance_m > 0 else 0.0)
            * disposal_rate_per_m3,
            2,
        )

        total_cost = round(
            labour_total + disposal_amount,
            2,
        )
        unit_rate = round(
            total_cost / quantity,
            2,
        )

        return {
            "version": 1,
            "calculator": "Excavation",
            "description": result.description,
            "unit": result.unit,
            "dimensions": {
                "length": float(
                    result.get_value("length", 0)
                ),
                "width": float(
                    result.get_value("width", 0)
                ),
                "depth": float(
                    result.get_value("depth", 0)
                ),
                "dimension_unit": result.get_value(
                    "dimension_unit",
                    "m",
                ),
            },
            "number_of_excavations": int(
                result.get_value(
                    "number_of_excavations",
                    1,
                )
            ),
            "quantity": round(quantity, 3),
            "spoil_factor_percent": float(
                result.get_value(
                    "spoil_factor_percent",
                    0,
                )
            ),
            "spoil_quantity": round(
                spoil_quantity,
                3,
            ),
            "materials": [],
            "material_total": 0.0,
            "labour": labour,
            "labour_total": labour_total,
            "disposal_distance_m": disposal_distance_m,
            "disposal_rate_per_m3": disposal_rate_per_m3,
            "disposal_amount": disposal_amount,
            "total_cost": total_cost,
            "unit_rate": unit_rate,
        }


__all__ = ["ExcavationEstimateService"]
