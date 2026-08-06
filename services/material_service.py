from __future__ import annotations

from models.material import Material


class MaterialService:
    """
    Material Business Logic Layer

    Controller
        │
        ▼
    MaterialService
        │
        ▼
    MaterialRepository
    """

    def __init__(self, repository):
        self.repository = repository

    # =====================================================
    # READ
    # =====================================================

    def get(self, material_id: int):
        return self.repository.get(material_id)

    def get_all(self):
        return self.repository.get_all()

    def get_by_project(self, project_id: int):
        return self.repository.get_by_project(project_id)

    def count(self):
        return self.repository.count()

    # =====================================================
    # CREATE
    # =====================================================

    def create(self, material: Material):

        self._validate(material)

        if self.repository.exists(
            material.project_id,
            material.material_name,
        ):
            raise ValueError(
                f"Material '{material.material_name}' already exists in this project."
            )

        material.calculate_amount()

        return self.repository.create(material)

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        material_id: int,
        material: Material,
    ):

        self._validate(material)

        material.calculate_amount()

        return self.repository.update(
            material_id,
            material,
        )

    # =====================================================
    # DELETE
    # =====================================================

    def delete(self, material_id: int):

        if self.repository.get(material_id) is None:
            raise ValueError("Material not found.")

        return self.repository.delete(material_id)

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

    def _validate(self, material: Material):

        if material is None:
            raise ValueError("Material cannot be None.")

        material.validate()

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