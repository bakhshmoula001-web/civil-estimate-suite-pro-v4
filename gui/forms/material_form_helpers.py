from __future__ import annotations


class MaterialFormHelpers:
    """
    Material Form Helper Functions
    """

    @staticmethod
    def to_float(value: str) -> float:

        value = (value or "").replace(",", "").strip()

        if value == "":
            return 0.0

        try:
            return float(value)
        except ValueError:
            return 0.0

    @staticmethod
    def calculate_amount(
        quantity: str,
        rate: str,
    ) -> float:

        qty = MaterialFormHelpers.to_float(quantity)

        rate = MaterialFormHelpers.to_float(rate)

        return round(qty * rate, 2)

    @staticmethod
    def format_amount(amount: float) -> str:

        return f"{amount:,.2f}"