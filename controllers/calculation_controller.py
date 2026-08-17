"""
=========================================================
Civil Estimate Suite Pro v4.0
Calculation Controller
---------------------------------------------------------
Central bridge between CalculationResult, BOQ and Material.
=========================================================
"""

from __future__ import annotations

from typing import Any

from models.boq import BOQ
from models.material import Material
from services.calculation_integration_service import (
    CalculationIntegrationService,
)
from services.cost_build_up_service import CostBuildUpService


class CalculationController:
    """Coordinate calculator output with application modules."""

    def __init__(
        self,
        boq_controller=None,
        material_controller=None,
        integration_service=None,
        rate_controller=None,
    ):
        self.boq_controller = boq_controller
        self.material_controller = material_controller
        self.rate_controller = rate_controller
        self.integration_service = (
            integration_service
            or CalculationIntegrationService()
        )

    def build_cost(
        self,
        analysis: dict,
    ) -> dict:
        """
        Build the complete material + labour cost breakdown from
        one calculator analysis.
        """
        return CostBuildUpService.from_analysis(analysis)

    def generate_boq(
        self,
        calculation_type: str,
        result: Any,
        project_id: int,
        rate: float,
    ):
        if result is None:
            raise ValueError("Calculation result is required.")

        project_id = int(project_id)
        if project_id <= 0:
            raise ValueError("Project ID must be greater than zero.")

        rate = float(rate)
        if rate < 0:
            raise ValueError("BOQ rate cannot be negative.")

        if self.boq_controller is None:
            raise RuntimeError("BOQ Controller is not available.")

        quantity = self._get_value(
            result,
            ("concrete_volume", "volume", "quantity"),
            0.0,
        )

        if quantity <= 0:
            raise ValueError(
                "Calculated concrete quantity must be greater than zero."
            )

        normalized = self._normalize_type(calculation_type)

        description = {
            "RCC": "Reinforced Cement Concrete",
        }.get(
            normalized,
            f"{normalized} Calculation",
        )

        existing = []
        getter = getattr(
            self.boq_controller,
            "get_by_project",
            None,
        )

        if callable(getter):
            try:
                existing = getter(project_id) or []
            except Exception:
                existing = []

        item_no = self._next_item_no(
            normalized,
            existing,
        )

        boq = BOQ(
            project_id=project_id,
            item_no=item_no,
            description=description,
            unit="m³",
            quantity=round(quantity, 3),
            rate=round(rate, 2),
            amount=round(quantity * rate, 2),
            remarks=(
                f"Generated from {normalized} calculator. "
                f"Quantity: {quantity:,.3f} m³."
            ),
        )

        boq.validate()

        return self.boq_controller.create(boq)

    def generate_material(
        self,
        calculation_type: str,
        result: Any,
        project_id: int,
        rates: dict | None = None,
    ) -> list[Material]:
        if result is None:
            raise ValueError("Calculation result is required.")

        project_id = int(project_id)
        if project_id <= 0:
            raise ValueError("Project ID must be greater than zero.")

        if self.material_controller is None:
            raise RuntimeError(
                "Material Controller is not available."
            )

        # If rates are not explicitly supplied by the caller, pull
        # the current project's rates from the central Rate Database.
        effective_rates = dict(rates or {})

        if not effective_rates:
            rate_controller = self.rate_controller
            if rate_controller is not None:
                effective_rates = (
                    self.integration_service.resolve_project_rates(
                        rate_controller,
                        project_id,
                    )
                )

        items = self.integration_service.build_material_items(
            calculation_type=calculation_type,
            result=result,
            rates=effective_rates,
            project_id=project_id,
        )

        created = []

        for data in items:
            material = Material(
                project_id=project_id,
                material_name=str(data.get("material_name", "")),
                unit=str(data.get("unit", "Nos")),
                quantity=float(data.get("quantity", 0.0)),
                rate=float(data.get("rate", 0.0)),
                amount=float(data.get("amount", 0.0)),
                remarks=str(data.get("remarks", "")),
            )

            material.calculate_amount()
            material.validate()

            created.append(
                self.material_controller.create(material)
            )

        return created

    @staticmethod
    def _get_value(
        result: Any,
        names: tuple[str, ...],
        default: float = 0.0,
    ) -> float:
        for name in names:
            values = getattr(result, "values", None)

            if isinstance(values, dict) and name in values:
                try:
                    return float(values[name])
                except (TypeError, ValueError):
                    pass

            try:
                value = getattr(result, name)
            except AttributeError:
                value = None

            if value is not None:
                try:
                    return float(value)
                except (TypeError, ValueError):
                    pass

            getter = getattr(result, "get_value", None)

            if callable(getter):
                try:
                    value = getter(name, None)
                    if value is not None:
                        return float(value)
                except (TypeError, ValueError):
                    pass

        return float(default)

    @staticmethod
    def _normalize_type(calculation_type: str) -> str:
        if calculation_type is None:
            raise ValueError("Calculation type is required.")

        value = (
            str(calculation_type)
            .strip()
            .upper()
            .replace("-", "_")
            .replace(" ", "_")
        )

        if value.endswith("_CALCULATOR"):
            value = value[:-11]

        return {
            "RCC": "RCC",
            "REINFORCED_CONCRETE": "RCC",
            "REINFORCED_CEMENT_CONCRETE": "RCC",
        }.get(value, value)

    @staticmethod
    def _next_item_no(
        calculation_type: str,
        existing_items: list,
    ) -> str:
        prefix = (
            "RCC"
            if calculation_type == "RCC"
            else calculation_type[:6]
        )

        highest = 0

        for item in existing_items:
            value = str(
                getattr(item, "item_no", "")
            ).strip().upper()

            if not value.startswith(prefix + "-"):
                continue

            suffix = value[len(prefix) + 1:]

            if suffix.isdigit():
                highest = max(highest, int(suffix))

        return f"{prefix}-{highest + 1:03d}"


CalculationIntegrationController = CalculationController


if __name__ == "__main__":
    print("CalculationController syntax/import structure OK.")
