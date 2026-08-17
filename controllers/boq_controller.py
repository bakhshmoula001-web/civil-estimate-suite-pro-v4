"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module : BOQ Controller
Purpose: Coordinate GUI, calculation integration,
         BOQ service and BOQ model.
=========================================================
"""

from __future__ import annotations

from models.boq import BOQ
from services.calculation_integration_service import (
    CalculationIntegrationService,
)


class BOQController:
    """
    BOQ Controller

    GUI
        │
        ▼
    BOQController
        │
        ├── CalculationIntegrationService
        │
        ▼
    BOQService
        │
        ▼
    BOQRepository
        │
        ▼
    Database
    """

    def __init__(self, service):
        self.service = service

    # =====================================================
    # READ
    # =====================================================

    def get(self, boq_id: int):
        return self.service.get(boq_id)

    def get_all(self):
        return self.service.get_all()

    def get_by_project(self, project_id: int):
        return self.service.get_by_project(project_id)

    # =====================================================
    # CREATE
    # =====================================================

    def create(self, boq: BOQ):
        if boq is None:
            raise ValueError(
                "BOQ item cannot be None."
            )

        boq.validate()

        return self.service.create(boq)

    # =====================================================
    # CREATE FROM CALCULATOR
    # =====================================================

    def generate_from_calculation(
        self,
        calculation_type: str,
        result,
        project_id: int,
        rate: float = 0.0,
    ):
        """
        Convert calculator result into BOQ item(s)
        and save them through the normal BOQ service.

        Flow:

            RCC Calculator
                  ↓
            Calculation Result
                  ↓
            Integration Service
                  ↓
            BOQ Model
                  ↓
            BOQ Service
                  ↓
            Repository
                  ↓
            Database
        """

        if result is None:
            raise ValueError(
                "Calculation result is required."
            )

        if project_id is None:
            raise ValueError(
                "Project ID is required."
            )

        try:
            project_id = int(project_id)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "Project ID must be numeric."
            ) from exc

        if project_id <= 0:
            raise ValueError(
                "Project ID must be greater than zero."
            )

        try:
            rate = float(rate)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "BOQ rate must be numeric."
            ) from exc

        if rate < 0:
            raise ValueError(
                "BOQ rate cannot be negative."
            )

        # -------------------------------------------------
        # Build BOQ data from calculation result
        # -------------------------------------------------

        items = (
            CalculationIntegrationService.build_boq_items(
                calculation_type,
                result,
                rate=rate,
                project_id=project_id,
            )
        )

        if not items:
            raise ValueError(
                "No BOQ items were generated."
            )

        created_items = []

        # -------------------------------------------------
        # Save each generated BOQ item
        # -------------------------------------------------

        for data in items:

            prefix = self._item_prefix(
                calculation_type
            )

            data["item_no"] = (
                self._next_item_number(
                    project_id,
                    prefix,
                )
            )

            boq = BOQ(
                id=data.get("id"),
                project_id=project_id,
                item_no=data["item_no"],
                description=data.get(
                    "description",
                    "",
                ),
                unit=data.get(
                    "unit",
                    "",
                ),
                quantity=float(
                    data.get(
                        "quantity",
                        0,
                    )
                ),
                rate=float(
                    data.get(
                        "rate",
                        rate,
                    )
                ),
                amount=float(
                    data.get(
                        "amount",
                        0,
                    )
                ),
                remarks=data.get(
                    "remarks",
                    "",
                ),
            )

            created = self.create(boq)

            created_items.append(created)

        return created_items

    # =====================================================
    # ITEM NUMBERING
    # =====================================================

    def _next_item_number(
        self,
        project_id: int,
        prefix: str,
    ) -> str:
        """
        Generate next automatic item number.

        Example:

            RCC-01
            RCC-02
            RCC-03
        """

        existing_items = (
            self.get_by_project(project_id)
        )

        highest = 0

        for item in existing_items:

            item_no = str(
                getattr(
                    item,
                    "item_no",
                    "",
                )
            ).strip().upper()

            if not item_no.startswith(
                f"{prefix}-"
            ):
                continue

            suffix = item_no[
                len(prefix) + 1:
            ]

            try:
                number = int(suffix)
            except ValueError:
                continue

            highest = max(
                highest,
                number,
            )

        return (
            f"{prefix}-{highest + 1:02d}"
        )

    # =====================================================
    # PREFIX
    # =====================================================

    @staticmethod
    def _item_prefix(
        calculation_type: str,
    ) -> str:

        value = (
            str(calculation_type)
            .strip()
            .upper()
        )

        if value.startswith("RCC"):
            return "RCC"

        if value.startswith("PCC"):
            return "PCC"

        if (
            "BRICK" in value
        ):
            return "BRICK"

        return "CALC"

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        boq_id: int,
        boq: BOQ,
    ):

        if boq is None:
            raise ValueError(
                "BOQ item cannot be None."
            )

        boq.validate()

        return self.service.update(
            boq_id,
            boq,
        )

    # =====================================================
    # DELETE
    # =====================================================

    def delete(
        self,
        boq_id: int,
    ):

        return self.service.delete(
            boq_id
        )

    # =====================================================
    # SEARCH
    # =====================================================

    def search(
        self,
        keyword: str,
    ):

        keyword = (
            keyword
            .strip()
        )

        if keyword == "":
            return self.get_all()

        return self.service.search(
            keyword
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def total_items(self):
        return self.service.total_items()

    def project_total(
        self,
        project_id: int,
    ):
        return self.service.project_total(
            project_id
        )