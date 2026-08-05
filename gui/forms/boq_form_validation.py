from __future__ import annotations

from gui.forms.boq_form_helpers import BOQFormHelpers


class BOQFormValidation:

    @staticmethod
    def validate_item_no(item_no):

        if str(item_no).strip() == "":
            return False, "Item No is required."

        return True, ""

    @staticmethod
    def validate_description(description):

        if str(description).strip() == "":
            return False, "Description is required."

        return True, ""

    @staticmethod
    def validate_quantity(quantity):

        qty = BOQFormHelpers.safe_float(quantity)

        if qty <= 0:
            return False, "Quantity must be greater than zero."

        return True, ""

    @staticmethod
    def validate_rate(rate):

        value = BOQFormHelpers.safe_float(rate)

        if value < 0:
            return False, "Rate cannot be negative."

        return True, ""

    @classmethod
    def validate_form(cls, item_no, description, quantity, rate):

        ok, msg = cls.validate_item_no(item_no)
        if not ok:
            return ok, msg

        ok, msg = cls.validate_description(description)
        if not ok:
            return ok, msg

        ok, msg = cls.validate_quantity(quantity)
        if not ok:
            return ok, msg

        ok, msg = cls.validate_rate(rate)
        if not ok:
            return ok, msg

        return True, ""