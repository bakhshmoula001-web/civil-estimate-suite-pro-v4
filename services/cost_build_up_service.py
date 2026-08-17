"""
Civil Estimate Suite Pro v4.0
Cost Build-Up Service

Central cost engine:
    Material quantity x material rate
    + Skilled labour quantity x skilled rate
    + Unskilled labour quantity x unskilled rate
    = Total cost

The service accepts calculator analysis dictionaries or normalized
material/labour rows and does not change engineering quantities.
"""

from __future__ import annotations

from typing import Any, Iterable


class CostBuildUpService:
    @staticmethod
    def _num(value: Any, default: float = 0.0) -> float:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return default

    @classmethod
    def material_rows(cls, materials: Iterable[dict] | None) -> list[dict]:
        rows = []
        for raw in materials or []:
            if not isinstance(raw, dict):
                continue

            name = str(
                raw.get("material_name")
                or raw.get("name")
                or raw.get("MATERIAL")
                or "Material"
            ).strip()
            unit = str(raw.get("unit") or raw.get("UNIT") or "Nos").strip()

            qty = cls._num(
                raw.get("quantity", raw.get("QUANTITY", raw.get("QTY")))
            )
            rate = cls._num(raw.get("rate", raw.get("RATE")))

            if qty < 0:
                raise ValueError(f"{name}: material quantity cannot be negative.")
            if rate < 0:
                raise ValueError(f"{name}: material rate cannot be negative.")

            rows.append({
                "name": name,
                "unit": unit,
                "quantity": round(qty, 3),
                "rate": round(rate, 2),
                "amount": round(qty * rate, 2),
            })
        return rows

    @classmethod
    def labour_rows(cls, labour: Iterable[dict] | None) -> list[dict]:
        rows = []
        for raw in labour or []:
            if not isinstance(raw, dict):
                continue

            name = str(
                raw.get("name")
                or raw.get("labour")
                or raw.get("LABOUR")
                or "Labour"
            ).strip()
            unit = str(raw.get("unit") or raw.get("UNIT") or "day").strip()
            qty = cls._num(
                raw.get("quantity", raw.get("days", raw.get("QUANTITY")))
            )
            rate = cls._num(raw.get("rate", raw.get("RATE")))

            if qty < 0:
                raise ValueError(f"{name}: labour quantity cannot be negative.")
            if rate < 0:
                raise ValueError(f"{name}: labour rate cannot be negative.")

            rows.append({
                "name": name,
                "unit": unit,
                "quantity": round(qty, 3),
                "rate": round(rate, 2),
                "amount": round(qty * rate, 2),
            })
        return rows

    @classmethod
    def build(
        cls,
        materials: Iterable[dict] | None = None,
        labour: Iterable[dict] | None = None,
        quantity: float = 0.0,
        quantity_unit: str = "",
        description: str = "",
    ) -> dict:
        material = cls.material_rows(materials)
        labour_rows = cls.labour_rows(labour)

        material_cost = round(sum(x["amount"] for x in material), 2)

        skilled = [
            x for x in labour_rows
            if "unskilled" not in x["name"].lower()
            and "skilled" in x["name"].lower()
        ]
        unskilled = [
            x for x in labour_rows
            if "unskilled" in x["name"].lower()
        ]
        other_labour = [
            x for x in labour_rows
            if x not in skilled and x not in unskilled
        ]

        skilled_cost = round(sum(x["amount"] for x in skilled), 2)
        unskilled_cost = round(sum(x["amount"] for x in unskilled), 2)
        other_labour_cost = round(sum(x["amount"] for x in other_labour), 2)
        labour_cost = round(
            skilled_cost + unskilled_cost + other_labour_cost, 2
        )

        total_cost = round(material_cost + labour_cost, 2)

        qty = cls._num(quantity)
        unit_rate = round(total_cost / qty, 2) if qty > 0 else 0.0

        return {
            "description": description,
            "quantity": round(qty, 3),
            "quantity_unit": quantity_unit,
            "materials": material,
            "labour": labour_rows,
            "material_cost": material_cost,
            "skilled_labour_cost": skilled_cost,
            "unskilled_labour_cost": unskilled_cost,
            "other_labour_cost": other_labour_cost,
            "labour_cost": labour_cost,
            "total_cost": total_cost,
            "unit_rate": unit_rate,
        }

    @classmethod
    def from_analysis(cls, analysis: dict) -> dict:
        if not isinstance(analysis, dict):
            raise ValueError("Analysis must be a dictionary.")

        quantity = analysis.get("quantity", 0)
        unit = analysis.get("unit", analysis.get("quantity_unit", ""))
        description = analysis.get("description", "")

        materials = analysis.get("materials", analysis.get("MATERIALS", []))
        labour = analysis.get("labour", analysis.get("LABOUR", []))

        return cls.build(
            materials=materials,
            labour=labour,
            quantity=quantity,
            quantity_unit=unit,
            description=description,
        )


__all__ = ["CostBuildUpService"]
