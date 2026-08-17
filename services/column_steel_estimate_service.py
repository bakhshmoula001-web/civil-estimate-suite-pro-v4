"""
Civil Estimate Suite Pro v4.0
Column Steel Estimate Service
"""
from __future__ import annotations


class ColumnSteelEstimateService:
    @staticmethod
    def build_analysis(result, steel_rate=0.0):
        rate = float(steel_rate)
        total = float(result.quantity)
        vertical = float(result.get_value("vertical_kg", 0))
        stirrup = float(result.get_value("stirrup_kg", 0))
        return {
            "version": 1,
            "calculator": "Column Steel",
            "description": result.description,
            "unit": "kg",
            "quantity": round(total, 3),
            "dimensions": {
                "length": float(result.get_value("column_length", 0)),
                "width": float(result.get_value("column_width", 0)),
                "height": float(result.get_value("column_height", 0)),
                "count": int(result.get_value("column_count", 1)),
                "unit": result.get_value("length_unit", "m"),
                "cover_mm": float(result.get_value("cover_mm", 0)),
            },
            "vertical": {
                "diameter_mm": float(result.get_value("vertical_dia_mm", 0)),
                "bars": int(result.get_value("vertical_bars", 0)),
                "length_each_m": float(result.get_value("vertical_length_each_m", 0)),
                "total_length_m": float(result.get_value("vertical_total_length_m", 0)),
                "weight_kg": round(vertical, 3),
            },
            "stirrups": {
                "diameter_mm": float(result.get_value("stirrup_dia_mm", 0)),
                "spacing_mm": float(result.get_value("stirrup_spacing_mm", 0)),
                "count_one": int(result.get_value("stirrup_count_one", 0)),
                "total_count": int(result.get_value("stirrup_total_count", 0)),
                "cutting_length_m": float(result.get_value("stirrup_cutting_length_m", 0)),
                "total_length_m": float(result.get_value("stirrup_total_length_m", 0)),
                "weight_kg": round(stirrup, 3),
            },
            "base_steel_kg": round(float(result.get_value("base_steel_kg", 0)), 3),
            "cutting_kg": round(float(result.get_value("cutting_kg", 0)), 3),
            "binding_wire_kg": round(float(result.get_value("binding_wire_kg", 0)), 3),
            "materials": [
                {
                    "name": "Vertical Reinforcement",
                    "unit": "kg",
                    "quantity": round(vertical, 3),
                    "rate": rate,
                    "amount": round(vertical * rate, 2),
                },
                {
                    "name": "Stirrups / Ties",
                    "unit": "kg",
                    "quantity": round(stirrup, 3),
                    "rate": rate,
                    "amount": round(stirrup * rate, 2),
                },
            ],
            "material_total": round(total * rate, 2),
            "labour": [],
            "labour_total": 0.0,
            "total_cost": round(total * rate, 2),
            "unit_rate": round(rate, 2),
        }


__all__ = ["ColumnSteelEstimateService"]
