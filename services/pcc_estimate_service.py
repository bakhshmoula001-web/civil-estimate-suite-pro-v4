"""
Civil Estimate Suite Pro v4.0
PCC Cost Build-up Service
"""
from __future__ import annotations

from typing import Any


class PCCEstimateService:
    """Build a transparent PCC material/labour cost analysis."""

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
            raise ValueError("PCC calculation result is required.")

        skilled_days = float(skilled_days)
        skilled_rate = float(skilled_rate)
        unskilled_days = float(unskilled_days)
        unskilled_rate = float(unskilled_rate)

        for name, value in {
            "Skilled labour days": skilled_days,
            "Skilled labour rate": skilled_rate,
            "Unskilled labour days": unskilled_days,
            "Unskilled labour rate": unskilled_rate,
        }.items():
            if value < 0:
                raise ValueError(f"{name} cannot be negative.")

        def rate(name: str) -> float:
            try:
                value = float(material_rates.get(name, 0.0))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid rate for {name}.") from exc
            if value < 0:
                raise ValueError(f"Rate for {name} cannot be negative.")
            return value

        volume_unit = str(result.get_value("volume_unit", result.unit or "m³"))
        material_volume_unit = volume_unit

        materials = [
            {
                "name": "Cement",
                "unit": "Bags",
                "quantity": round(float(result.cement_bags), 3),
                "rate": round(rate("cement_bag"), 2),
            },
            {
                "name": "Sand",
                "unit": material_volume_unit,
                "quantity": round(float(result.sand_volume), 3),
                "rate": round(rate("sand"), 2),
            },
            {
                "name": "Coarse Aggregate",
                "unit": material_volume_unit,
                "quantity": round(float(result.aggregate_volume), 3),
                "rate": round(rate("aggregate"), 2),
            },
        ]
        for item in materials:
            item["amount"] = round(item["quantity"] * item["rate"], 2)

        material_total = round(sum(item["amount"] for item in materials), 2)

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
            item["amount"] = round(item["quantity"] * item["rate"], 2)

        labour_total = round(sum(item["amount"] for item in labour), 2)
        total_cost = round(material_total + labour_total, 2)
        quantity = float(result.quantity)
        unit_rate = round(total_cost / quantity, 2) if quantity > 0 else 0.0

        dimension_unit = result.get_value(
            "dimension_unit",
            "m" if volume_unit == "m³" else "ft",
        )

        return {
            "version": 2,
            "calculator": "PCC",
            "description": result.description,
            "unit": volume_unit,
            "dimensions": {
                "length": float(result.get_value("length", 0.0)),
                "width": float(result.get_value("width", 0.0)),
                "height": float(result.get_value("height", 0.0)),
                "dimension_unit": dimension_unit,
            },
            "mix_ratio": result.get_value("mix_ratio", ""),
            "quantity": round(quantity, 3),
            "wet_volume": round(float(result.wet_volume), 3),
            "dry_volume": round(float(result.dry_volume), 3),
            "metric_quantity_m3": round(float(result.get_value("metric_quantity_m3", 0.0)), 6),
            "materials": materials,
            "material_total": material_total,
            "labour": labour,
            "labour_total": labour_total,
            "total_cost": total_cost,
            "unit_rate": unit_rate,
        }
