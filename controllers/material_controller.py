from __future__ import annotations

from models.material import Material


class MaterialController:
    """
    Material Controller

    GUI
        │
        ▼
    MaterialController
        │
        ▼
    MaterialService
    """

    def __init__(self, service):
        self.service = service

    # =====================================================
    # READ
    # =====================================================

    def get(self, material_id: int):
        return self.service.get(material_id)

    def get_all(self):
        return self.service.get_all()

    def get_by_project(self, project_id: int):
        return self.service.get_by_project(project_id)

    # =====================================================
    # CREATE
    # =====================================================

    def create(self, material: Material):

        if material is None:
            raise ValueError("Material cannot be None.")

        material.validate()

        return self.service.create(material)

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        material_id: int,
        material: Material,
    ):

        if material is None:
            raise ValueError("Material cannot be None.")

        material.validate()

        return self.service.update(
            material_id,
            material,
        )

    # =====================================================
    # DELETE
    # =====================================================

    def delete(self, material_id: int):
        return self.service.delete(material_id)

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