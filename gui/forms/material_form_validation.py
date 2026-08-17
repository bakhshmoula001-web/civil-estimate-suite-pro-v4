from __future__ import annotations

from gui.forms.material_form_helpers import MaterialFormHelpers


class MaterialFormValidation:

    @staticmethod
    def validate_form(
        material_name: str,
        quantity: str,
        rate: str,
    ):

        if material_name.strip() == "":
            return False, "Material Name is required."

        qty = MaterialFormHelpers.to_float(quantity)

        if qty <= 0:
            return False, "Quantity must be greater than zero."

        price = MaterialFormHelpers.to_float(rate)

        if price < 0:
            return False, "Rate cannot be negative."

        return True, ""