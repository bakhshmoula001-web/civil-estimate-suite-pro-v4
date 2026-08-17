"""
Civil Estimate Suite Pro v4.0
Material Controller
---------------------------------------------------------
Single, stable entry point for:
    Calculator -> Material Analysis -> Material Records

Important compatibility:
Older calculator forms call:
    generate_from_analysis(analysis, project_id)

Newer integrations call:
    generate_from_calculation(
        calculation_type,
        result,
        project_id,
        rates,
    )
"""
from __future__ import annotations

from typing import Any

from models.material import Material
from services.calculation_integration_service import CalculationIntegrationService


class MaterialController:
    def __init__(self, service):
        self.service = service

    # -----------------------------------------------------
    # Basic CRUD
    # -----------------------------------------------------

    def get(self, material_id: int):
        return self.service.get(material_id)

    def get_all(self):
        return self.service.get_all()

    def get_by_project(self, project_id: int):
        return self.service.get_by_project(project_id)

    def create(self, material: Material):
        if material is None:
            raise ValueError("Material cannot be None.")
        material.calculate_amount()
        material.validate()
        return self.service.create(material)

    # -----------------------------------------------------
    # Calculator -> Material
    # -----------------------------------------------------

    def generate_from_analysis(
        self,
        analysis: dict,
        project_id: int,
    ):
        """
        Generate materials directly from a calculator analysis.

        This is the method used by the current calculator forms.

        Expected analysis:
            {
                "calculator": "PCC",
                "materials": [
                    {
                        "name": "Cement",
                        "unit": "Bags",
                        "quantity": 26.690,
                        "rate": 1650.0,
                        "amount": 44038.50,
                    },
                    ...
                ]
            }

        Also accepts uppercase MATERIALS / NAME / UNIT / QUANTITY /
        RATE / AMOUNT for compatibility with older result payloads.
        """
        if not isinstance(analysis, dict):
            raise ValueError("Calculator analysis must be a dictionary.")

        project_id = self._project_id(project_id)

        embedded = (
            analysis.get("materials")
            or analysis.get("MATERIALS")
            or analysis.get("Materials")
        )

        if not isinstance(embedded, (list, tuple)) or not embedded:
            raise ValueError(
                "No material quantities were found in the calculator analysis."
            )

        saved_items = []

        for raw in embedded:
            if not isinstance(raw, dict):
                continue

            name = self._pick(raw, "name", "NAME", "material_name", "MATERIAL")
            unit = self._pick(raw, "unit", "UNIT", default="Nos")
            quantity = self._number(
                self._pick(raw, "quantity", "QUANTITY", "QTY", "qty", default=0),
                "Material quantity",
            )
            rate = self._number(
                self._pick(raw, "rate", "RATE", default=0),
                "Material rate",
            )
            amount = self._pick(raw, "amount", "AMOUNT", default=None)
            remarks = self._pick(
                raw,
                "remarks",
                "REMARKS",
                default=(
                    f"Generated from "
                    f"{analysis.get('calculator', analysis.get('CALCULATOR', 'calculator'))} "
                    "calculator."
                ),
            )

            name = str(name or "").strip()
            unit = str(unit or "").strip()

            if not name or quantity <= 0:
                continue

            # Prefer calculator-supplied rate. If an old payload only
            # supplies amount, derive the rate from quantity.
            if rate <= 0 and amount is not None:
                supplied_amount = self._number(amount, "Material amount")
                rate = supplied_amount / quantity if quantity else 0.0

            material = Material(
                project_id=project_id,
                material_name=name,
                unit=unit or "Nos",
                quantity=quantity,
                rate=rate,
                amount=round(quantity * rate, 2),
                remarks=str(remarks or ""),
            )
            material.validate()

            # Same material + same unit is consolidated by the service.
            saved_items.append(
                self.service.upsert_generated(material)
            )

        if not saved_items:
            raise ValueError(
                "No valid material quantities were found in the calculator analysis."
            )

        return saved_items

    def generate_from_calculation(
        self,
        calculation_type: str,
        result: Any,
        project_id: int | None = None,
        rates: dict | None = None,
    ):
        """
        Generate materials from either:
          1. a calculation analysis dictionary, or
          2. a CalculationResult object.

        This method intentionally supports both old and new callers.
        """
        if result is None:
            raise ValueError("Calculation result is required.")

        if project_id is None:
            from core.current_project import CurrentProject
            project_id = CurrentProject.id()

        project_id = self._project_id(project_id)

        # Some legacy forms pass the complete analysis dictionary as
        # `result`. Handle that directly rather than trying to rebuild
        # quantities from the generic CalculationResult.
        if isinstance(result, dict):
            embedded = (
                result.get("materials")
                or result.get("MATERIALS")
                or result.get("Materials")
            )
            if isinstance(embedded, (list, tuple)):
                return self.generate_from_analysis(
                    result,
                    project_id,
                )

        items = CalculationIntegrationService.build_material_items(
            calculation_type=calculation_type,
            result=result,
            rates=rates or {},
            project_id=project_id,
        )

        if not items:
            raise ValueError("No material items were generated.")

        return self._save_items(items, project_id)

    # Explicit compatibility name. Do NOT alias this to the
    # calculation method because its positional signature is different.
    def generate_from_analysis_legacy(
        self,
        analysis: dict,
        project_id: int,
    ):
        return self.generate_from_analysis(analysis, project_id)

    # -----------------------------------------------------
    # Internal
    # -----------------------------------------------------

    def _save_items(self, items: list[dict], project_id: int):
        saved_items = []

        for data in items:
            material = Material(
                id=data.get("id"),
                project_id=project_id,
                material_name=str(
                    data.get("material_name", "")
                ).strip(),
                unit=str(data.get("unit", "Nos")).strip(),
                quantity=float(data.get("quantity", 0)),
                rate=float(data.get("rate", 0)),
                amount=float(data.get("amount", 0)),
                remarks=data.get("remarks", ""),
            )

            material.calculate_amount()
            material.validate()

            saved_items.append(
                self.service.upsert_generated(material)
            )

        return saved_items

    @staticmethod
    def _pick(data: dict, *keys, default=None):
        for key in keys:
            if key in data and data[key] is not None:
                return data[key]
        return default

    @staticmethod
    def _number(value, label: str) -> float:
        try:
            number = float(value or 0)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{label} must be numeric.") from exc

        if number < 0:
            raise ValueError(f"{label} cannot be negative.")

        return number

    @staticmethod
    def _project_id(project_id) -> int:
        if project_id is None:
            raise ValueError(
                "No active project is selected. "
                "Please select/open a project before generating material."
            )

        try:
            project_id = int(project_id)
        except (TypeError, ValueError) as exc:
            raise ValueError("Project ID must be numeric.") from exc

        if project_id <= 0:
            raise ValueError("Project ID must be greater than zero.")

        return project_id

    def update(self, material_id: int, material: Material):
        if material is None:
            raise ValueError("Material cannot be None.")
        material.calculate_amount()
        material.validate()
        return self.service.update(material_id, material)

    def delete(self, material_id: int):
        if self.get(material_id) is None:
            raise ValueError("Material not found.")
        return self.service.delete(material_id)

    def search(self, keyword: str):
        keyword = str(keyword or "").strip()
        return self.get_all() if not keyword else self.service.search(keyword)

    def count(self):
        return (
            self.service.count()
            if hasattr(self.service, "count")
            else len(self.get_all())
        )

    def total_items(self):
        return self.count()

    def project_total(self, project_id: int):
        return round(
            sum(
                float(getattr(item, "amount", 0) or 0)
                for item in self.get_by_project(project_id)
            ),
            2,
        )


__all__ = ["MaterialController"]
