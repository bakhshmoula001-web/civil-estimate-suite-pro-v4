"""
=========================================================
Civil Estimate Suite Pro v4.1
---------------------------------------------------------
File    : boq_form_helpers.py
Module  : BOQ
Purpose : Helper functions for BOQ Form
Author  : Integration Pack-03B
=========================================================
"""

from __future__ import annotations


class BOQFormHelpers:
    """
    Helper methods used by BOQ Form.
    """

    @staticmethod
    def safe_float(value) -> float:
        """
        Safely convert any value to float.
        """

        if value is None:
            return 0.0

        if isinstance(value, (int, float)):
            return float(value)

        value = str(value).strip()

        if value == "":
            return 0.0

        value = value.replace(",", "")

        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def calculate_amount(quantity, rate) -> float:
        """
        Calculate BOQ amount.
        """

        qty = BOQFormHelpers.safe_float(quantity)
        rate = BOQFormHelpers.safe_float(rate)

        return round(qty * rate, 2)

    @staticmethod
    def format_amount(value) -> str:
        """
        Format amount for display.
        """

        amount = BOQFormHelpers.safe_float(value)

        return f"{amount:,.2f}"

    @staticmethod
    def format_quantity(value) -> str:
        """
        Format quantity for display.
        """

        qty = BOQFormHelpers.safe_float(value)

        if qty.is_integer():
            return str(int(qty))

        return f"{qty:.2f}"

    @staticmethod
    def reset_numeric_fields(form):
        """
        Reset numeric fields on BOQ form.
        """

        form.quantity.set("0")

        form.rate.set("0")

        form.amount.set("0.00")
    def to_float(value: str) -> float:
         value = value.replace(",", "").strip()

         if value == "":
           return 0.0

         return float(value)