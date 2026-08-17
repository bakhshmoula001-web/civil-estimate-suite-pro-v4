"""
Civil Estimate Suite Pro v4.0
Project Cost Control Service
"""

from __future__ import annotations


class CostControlService:
    """Build a project-level cost control summary from BOQ analyses."""

    @staticmethod
    def _num(value):
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    @classmethod
    def build(cls, items, analyses):
        material = skilled = unskilled = other = 0.0
        analysed = 0

        for item in items or []:
            analysis = (analyses or {}).get(getattr(item, "id", None))
            if not isinstance(analysis, dict):
                continue

            analysed += 1
            material += cls._num(
                analysis.get("material_cost", analysis.get("material_total", 0))
            )
            skilled += cls._num(
                analysis.get("skilled_labour_cost", analysis.get("skilled_cost", 0))
            )
            unskilled += cls._num(
                analysis.get(
                    "unskilled_labour_cost",
                    analysis.get("unskilled_cost", 0),
                )
            )
            other += cls._num(
                analysis.get("other_labour_cost", analysis.get("other_labour", 0))
            )

        labour = skilled + unskilled + other
        grand = material + labour
        boq_count = len(items or [])
        pending = max(0, boq_count - analysed)

        def pct(value):
            return round((value / grand) * 100, 2) if grand else 0.0

        return {
            "boq_items": boq_count,
            "analysed_items": analysed,
            "pending_items": pending,
            "material_cost": round(material, 2),
            "skilled_labour_cost": round(skilled, 2),
            "unskilled_labour_cost": round(unskilled, 2),
            "other_labour_cost": round(other, 2),
            "labour_cost": round(labour, 2),
            "grand_total": round(grand, 2),
            "material_percent": pct(material),
            "labour_percent": pct(labour),
            "skilled_percent": pct(skilled),
            "unskilled_percent": pct(unskilled),
        }


__all__ = ["CostControlService"]
