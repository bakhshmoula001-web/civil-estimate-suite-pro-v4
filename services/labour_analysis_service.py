"""
Civil Estimate Suite Pro v4.0
Labour Analysis Service

Centralizes skilled/unskilled labour analysis for all calculators.
The calculator remains the source of labour quantity/rates; this service
normalizes the data, calculates amounts, and provides project summaries.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable


class LabourAnalysisService:
    SKILLED = "Skilled Labour"
    UNSKILLED = "Unskilled Labour"

    @staticmethod
    def _num(value: Any, default: float = 0.0) -> float:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return default

    @classmethod
    def normalize(cls, labour: Iterable[dict] | None) -> list[dict]:
        """Return clean labour rows with calculated amount."""
        rows = []

        for raw in labour or []:
            if not isinstance(raw, dict):
                continue

            name = str(
                raw.get("name")
                or raw.get("NAME")
                or raw.get("labour")
                or raw.get("LABOUR")
                or "Labour"
            ).strip()

            unit = str(
                raw.get("unit")
                or raw.get("UNIT")
                or "day"
            ).strip()

            quantity = cls._num(
                raw.get("quantity", raw.get("QUANTITY", raw.get("days", 0)))
            )
            rate = cls._num(
                raw.get("rate", raw.get("RATE", 0))
            )

            if quantity < 0:
                raise ValueError(f"{name}: labour quantity cannot be negative.")
            if rate < 0:
                raise ValueError(f"{name}: labour rate cannot be negative.")

            amount = round(quantity * rate, 2)

            rows.append({
                "name": name,
                "unit": unit,
                "quantity": round(quantity, 3),
                "rate": round(rate, 2),
                "amount": amount,
            })

        return rows

    @classmethod
    def analyze(cls, labour: Iterable[dict] | None) -> dict:
        """Build a complete skilled/unskilled labour cost build-up."""
        rows = cls.normalize(labour)

        # Check UNskilled first because the word "unskilled"
        # contains the substring "skilled".
        unskilled = [
            x for x in rows
            if "unskilled" in x["name"].lower()
        ]
        skilled = [
            x for x in rows
            if "skilled" in x["name"].lower()
            and "unskilled" not in x["name"].lower()
        ]
        other = [
            x for x in rows
            if x not in skilled and x not in unskilled
        ]

        def total(items):
            return round(sum(x["amount"] for x in items), 2)

        return {
            "rows": rows,
            "skilled": skilled,
            "unskilled": unskilled,
            "other": other,
            "skilled_days": round(
                sum(x["quantity"] for x in skilled), 3
            ),
            "unskilled_days": round(
                sum(x["quantity"] for x in unskilled), 3
            ),
            "skilled_cost": total(skilled),
            "unskilled_cost": total(unskilled),
            "other_cost": total(other),
            "labour_total": total(rows),
        }

    @classmethod
    def attach(cls, analysis: dict) -> dict:
        """
        Normalize and enrich an existing calculator analysis without
        changing its original calculation fields.
        """
        if not isinstance(analysis, dict):
            raise ValueError("Analysis must be a dictionary.")

        result = dict(analysis)
        labour = cls.analyze(result.get("labour", []))

        result["labour"] = labour["rows"]
        result["labour_analysis"] = labour
        result["labour_total"] = labour["labour_total"]

        # Keep total cost mathematically consistent with material + labour.
        material_total = cls._num(result.get("material_total"))
        result["total_cost"] = round(
            material_total + labour["labour_total"], 2
        )

        material_qty = cls._num(result.get("quantity"))
        if material_qty > 0:
            result["unit_rate"] = round(
                result["total_cost"] / material_qty, 2
            )

        return result

    @classmethod
    def project_summary(
        cls,
        analyses: Iterable[dict],
    ) -> dict:
        """Consolidate labour across all BOQ calculator analyses."""
        by_type = defaultdict(
            lambda: {
                "quantity": 0.0,
                "amount": 0.0,
                "unit": "day",
            }
        )

        skilled_days = 0.0
        unskilled_days = 0.0
        skilled_cost = 0.0
        unskilled_cost = 0.0
        total = 0.0

        for analysis in analyses or []:
            data = cls.analyze(
                analysis.get("labour", [])
                if isinstance(analysis, dict)
                else []
            )

            for row in data["rows"]:
                key = (row["name"], row["unit"])
                by_type[key]["quantity"] += row["quantity"]
                by_type[key]["amount"] += row["amount"]
                by_type[key]["unit"] = row["unit"]

            skilled_days += data["skilled_days"]
            unskilled_days += data["unskilled_days"]
            skilled_cost += data["skilled_cost"]
            unskilled_cost += data["unskilled_cost"]
            total += data["labour_total"]

        rows = []
        for (name, unit), value in sorted(by_type.items()):
            qty = round(value["quantity"], 3)
            amount = round(value["amount"], 2)
            rate = round(amount / qty, 2) if qty else 0.0
            rows.append({
                "name": name,
                "unit": unit,
                "quantity": qty,
                "rate": rate,
                "amount": amount,
            })

        return {
            "rows": rows,
            "skilled_days": round(skilled_days, 3),
            "unskilled_days": round(unskilled_days, 3),
            "skilled_cost": round(skilled_cost, 2),
            "unskilled_cost": round(unskilled_cost, 2),
            "labour_total": round(total, 2),
        }


__all__ = ["LabourAnalysisService"]
