"""
Civil Estimate Suite Pro v4.0
Steel / Rebar Estimate Service
"""
from __future__ import annotations


class SteelEstimateService:
    """Convert a steel calculation into detailed BOQ/cost analysis."""

    @staticmethod
    def build_analysis(result, steel_rate=0.0):
        def nn(value, label):
            try:
                value = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"{label} must be numeric."
                ) from exc
            if value < 0:
                raise ValueError(
                    f"{label} cannot be negative."
                )
            return value

        steel_rate = nn(steel_rate, "Steel rate")
        steel_kg = nn(
            result.get_value("steel_kg", result.quantity),
            "Steel quantity",
        )
        binding_kg = nn(
            result.get_value("binding_wire_kg", 0),
            "Binding wire quantity",
        )
        binding_rate = 0.0

        steel = {
            "name": "Reinforcement Steel",
            "unit": "kg",
            "quantity": round(steel_kg, 3),
            "rate": round(steel_rate, 2),
        }
        steel["amount"] = round(
            steel["quantity"] * steel["rate"],
            2,
        )

        binding = {
            "name": "Binding Wire",
            "unit": "kg",
            "quantity": round(binding_kg, 3),
            "rate": round(binding_rate, 2),
        }
        binding["amount"] = 0.0

        return {
            "version": 1,
            "calculator": "Steel",
            "description": result.description,
            "unit": "kg",
            "quantity": round(steel_kg, 3),
            "diameter_mm": float(
                result.get_value("diameter_mm", 0)
            ),
            "bar_count": int(
                result.get_value("bar_count", 0)
            ),
            "spacing_mm": float(
                result.get_value("spacing_mm", 0)
            ),
            "distribution_length": float(
                result.get_value("distribution_length", 0)
            ),
            "bar_length": float(
                result.get_value("bar_length", 0)
            ),
            "lap_length": float(
                result.get_value("lap_length", 0)
            ),
            "laps_per_bar": int(
                result.get_value("laps_per_bar", 0)
            ),
            "cutting_allowance_percent": float(
                result.get_value(
                    "cutting_allowance_percent", 0
                )
            ),
            "total_length_m": round(
                float(result.get_value("total_length_m", 0)),
                3,
            ),
            "weight_per_m": round(
                float(result.get_value("weight_per_m", 0)),
                4,
            ),
            "materials": [steel, binding],
            "material_total": steel["amount"],
            "labour": [],
            "labour_total": 0.0,
            "total_cost": steel["amount"],
            "unit_rate": round(steel_rate, 2),
        }


__all__ = ["SteelEstimateService"]
