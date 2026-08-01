from __future__ import annotations

from models.boq import BOQ


class BOQService:
    """
    BOQ Business Logic Layer

    Controller
        │
        ▼
    BOQService
        │
        ▼
    BOQRepository
    """

    def __init__(self, repository):
        self.repository = repository

    # =====================================================
    # READ
    # =====================================================

    def get(self, boq_id: int):
        return self.repository.get(boq_id)

    def get_all(self):
        return self.repository.get_all()

    def get_by_project(self, project_id: int):
        return self.repository.get_by_project(project_id)

    def count(self):
        return self.repository.count()

    # =====================================================
    # CREATE
    # =====================================================

    def create(self, boq: BOQ):

        self._validate(boq)

        if self.repository.exists(
            boq.project_id,
            boq.item_no,
        ):
            raise ValueError(
                f"Item No '{boq.item_no}' already exists in this project."
            )

        boq.calculate_amount()

        return self.repository.create(boq)

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        boq_id: int,
        boq: BOQ,
    ):

        self._validate(boq)

        boq.calculate_amount()

        return self.repository.update(
            boq_id,
            boq,
        )

    # =====================================================
    # DELETE
    # =====================================================

    def delete(self, boq_id: int):

        if self.repository.get(boq_id) is None:
            raise ValueError("BOQ Item not found.")

        return self.repository.delete(boq_id)

    # =====================================================
    # SEARCH
    # =====================================================

    def search(self, keyword: str):

        keyword = keyword.strip()

        if keyword == "":
            return self.get_all()

        return self.repository.search(keyword)

    # =====================================================
    # VALIDATION
    # =====================================================

    def _validate(self, boq: BOQ):

        if boq is None:
            raise ValueError("BOQ item cannot be None.")

        boq.validate()

    # =====================================================
    # HELPERS
    # =====================================================

    def total_items(self):
        return self.repository.count()

    def project_total(self, project_id: int):

        items = self.get_by_project(project_id)

        return round(
            sum(item.amount for item in items),
            2,
        )