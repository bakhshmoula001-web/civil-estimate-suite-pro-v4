from __future__ import annotations

from models.boq import BOQ


class BOQController:
    """
    BOQ Controller

    GUI
        │
        ▼
    BOQController
        │
        ▼
    BOQService
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
            raise ValueError("BOQ item cannot be None.")

        boq.validate()

        return self.service.create(boq)

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        boq_id: int,
        boq: BOQ,
    ):

        if boq is None:
            raise ValueError("BOQ item cannot be None.")

        boq.validate()

        return self.service.update(
            boq_id,
            boq,
        )

    # =====================================================
    # DELETE
    # =====================================================

    def delete(self, boq_id: int):
        return self.service.delete(boq_id)

    # =====================================================
    # SEARCH
    # =====================================================

    def search(self, keyword: str):

        keyword = keyword.strip()

        if keyword == "":
            return self.get_all()

        return self.service.search(keyword)

    # =====================================================
    # SUMMARY
    # =====================================================

    def total_items(self):
        return self.service.total_items()

    def project_total(self, project_id: int):
        return self.service.project_total(project_id)