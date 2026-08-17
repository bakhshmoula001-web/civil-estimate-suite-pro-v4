"""
Civil Estimate Suite Pro v4.0
Final Estimate Summary Service
"""

from __future__ import annotations


class EstimateSummaryService:
    """Consolidate all saved BOQ calculator analyses for one project."""

    @staticmethod
    def _num(value):
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    @classmethod
    def build(cls, items, analyses):
        material_cost = 0.0
        skilled_cost = 0.0
        unskilled_cost = 0.0
        other_labour_cost = 0.0
        total_cost = 0.0
        analysed_items = 0

        material_breakdown = {}
        labour_breakdown = {}

        for item in items or []:
            item_id = getattr(item, "id", None)
            analysis = (analyses or {}).get(item_id)
            if not isinstance(analysis, dict):
                continue

            analysed_items += 1

            material_cost += cls._num(
                analysis.get("material_cost", analysis.get("material_total", 0))
            )
            skilled_cost += cls._num(analysis.get("skilled_labour_cost", 0))
            unskilled_cost += cls._num(analysis.get("unskilled_labour_cost", 0))
            other_labour_cost += cls._num(analysis.get("other_labour_cost", 0))

            labour_value = analysis.get(
                "labour_cost",
                analysis.get(
                    "labour_total",
                    cls._num(analysis.get("skilled_labour_cost", 0))
                    + cls._num(analysis.get("unskilled_labour_cost", 0))
                    + cls._num(analysis.get("other_labour_cost", 0)),
                ),
            )
            total_cost += cls._num(
                analysis.get(
                    "total_cost",
                    cls._num(analysis.get("material_cost", analysis.get("material_total", 0)))
                    + cls._num(labour_value),
                )
            )

            for row in analysis.get("materials", []) or []:
                name = str(
                    row.get("name")
                    or row.get("material_name")
                    or "Material"
                ).strip()
                amount = cls._num(
                    row.get("amount", row.get("cost", 0))
                )
                material_breakdown[name] = (
                    material_breakdown.get(name, 0.0) + amount
                )

            for row in analysis.get("labour", []) or []:
                name = str(
                    row.get("name")
                    or row.get("labour")
                    or "Labour"
                ).strip()
                amount = cls._num(row.get("amount", row.get("cost", 0)))
                labour_breakdown[name] = (
                    labour_breakdown.get(name, 0.0) + amount
                )

        labour_cost = skilled_cost + unskilled_cost + other_labour_cost
        if total_cost == 0:
            total_cost = material_cost + labour_cost

        return {
            "boq_items": len(items or []),
            "analysed_items": analysed_items,
            "pending_analysis": max(0, len(items or []) - analysed_items),
            "material_cost": round(material_cost, 2),
            "skilled_labour_cost": round(skilled_cost, 2),
            "unskilled_labour_cost": round(unskilled_cost, 2),
            "other_labour_cost": round(other_labour_cost, 2),
            "labour_cost": round(labour_cost, 2),
            "total_cost": round(total_cost, 2),
            "material_breakdown": {
                k: round(v, 2) for k, v in sorted(material_breakdown.items())
            },
            "labour_breakdown": {
                k: round(v, 2) for k, v in sorted(labour_breakdown.items())
            },
        }


__all__ = ["EstimateSummaryService"]
