from __future__ import annotations

from models.material import Material


class MaterialService:
    """Material business logic with safe calculator-material accumulation."""

    def __init__(self, repository):
        self.repository = repository

    def get(self, material_id: int):
        return self.repository.get(material_id)

    def get_all(self):
        return self.repository.get_all()

    def get_by_project(self, project_id: int):
        return self.repository.get_by_project(project_id)

    def count(self):
        return self.repository.count()

    def create(self, material: Material):
        self._validate(material)
        if self.repository.exists(
            material.project_id, material.material_name, material.unit
        ):
            raise ValueError(
                f"Material '{material.material_name}' "
                f"({material.unit}) already exists in this project."
            )
        material.calculate_amount()
        return self.repository.create(material)

    def upsert_generated(self, material: Material):
        """
        Save calculator-generated material.

        Same project + same material + same unit:
            quantity and amount are accumulated.

        Different units:
            separate records are maintained.
        """
        self._validate(material)
        material.calculate_amount()

        existing = self.repository.find_by_project_name_unit(
            material.project_id,
            material.material_name,
            material.unit,
        )

        if existing is None:
            material_id = self.repository.create(material)

            # Repository.create() historically returned the SQLite row id.
            # The calculator integration, however, needs a Material object
            # so the UI can safely read material_name/unit/quantity/etc.
            created = self.repository.get(material_id)
            if created is None:
                material.id = material_id
                return material
            return created

        old_qty = float(existing.quantity or 0)
        old_amount = float(existing.amount or 0)
        new_qty = float(material.quantity or 0)
        new_amount = float(material.amount or 0)

        existing.quantity = round(old_qty + new_qty, 3)
        existing.amount = round(old_amount + new_amount, 2)

        if existing.quantity:
            existing.rate = round(
                existing.amount / existing.quantity, 6
            )

        old_remarks = str(existing.remarks or "").strip()
        new_remarks = str(material.remarks or "").strip()

        if new_remarks and new_remarks not in old_remarks:
            existing.remarks = (
                f"{old_remarks} | {new_remarks}"
                if old_remarks else new_remarks
            )

        self._validate(existing)
        self.repository.update(existing.id, existing)

        # Repository.update() historically returned True. Returning the
        # refreshed Material object keeps calculator integration consistent
        # for both NEW and EXISTING material records.
        updated = self.repository.get(existing.id)
        return updated if updated is not None else existing

    def update(self, material_id: int, material: Material):
        self._validate(material)
        material.calculate_amount()
        return self.repository.update(material_id, material)

    def delete(self, material_id: int):
        if self.repository.get(material_id) is None:
            raise ValueError("Material not found.")
        return self.repository.delete(material_id)

    def search(self, keyword: str):
        keyword = str(keyword or "").strip()
        return self.get_all() if not keyword else self.repository.search(keyword)

    def total_items(self):
        return self.repository.count()

    def project_total(self, project_id: int):
        return round(
            sum(
                float(item.amount or 0)
                for item in self.get_by_project(project_id)
            ),
            2,
        )

    @staticmethod
    def _validate(material: Material):
        if material is None:
            raise ValueError("Material cannot be None.")
        material.validate()
