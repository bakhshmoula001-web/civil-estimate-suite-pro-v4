"""
=========================================================
Civil Estimate Suite Pro v4.0
Base Calculator
---------------------------------------------------------
Abstract base class for all calculation modules.
=========================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from calculations.calculation_result import CalculationResult


class BaseCalculator(ABC):
    """
    Base class for all civil engineering calculators.

    Every calculator must inherit this class and implement
    the calculate() method.
    """

    def __init__(self):

        self.result = CalculationResult()

    # =====================================================
    # ABSTRACT
    # =====================================================

    @abstractmethod
    def calculate(self) -> CalculationResult:
        """
        Execute calculation.

        Returns
        -------
        CalculationResult
        """
        raise NotImplementedError

    # =====================================================
    # HELPERS
    # =====================================================

    @staticmethod
    def round(
        value: float,
        digits: int = 2,
    ) -> float:
        """
        Safe rounding helper.
        """

        return round(float(value), digits)

    @staticmethod
    def positive(
        value: float,
        field_name: str,
    ) -> float:
        """
        Ensure value is positive.
        """

        value = float(value)

        if value <= 0:
            raise ValueError(
                f"{field_name} must be greater than zero."
            )

        return value

    @staticmethod
    def non_negative(
        value: float,
        field_name: str,
    ) -> float:
        """
        Ensure value is not negative.
        """

        value = float(value)

        if value < 0:
            raise ValueError(
                f"{field_name} cannot be negative."
            )

        return value

    # =====================================================
    # COMMON FORMULAS
    # =====================================================

    @staticmethod
    def volume(
        length: float,
        width: float,
        height: float,
    ) -> float:
        """
        Calculate volume.
        """

        return round(
            length * width * height,
            3,
        )

    @staticmethod
    def dry_volume(
        wet_volume: float,
        factor: float = 1.54,
    ) -> float:
        """
        Convert wet volume into dry volume.
        """

        return round(
            wet_volume * factor,
            3,
        )

    @staticmethod
    def ratio_part(
        dry_volume: float,
        part: float,
        total_parts: float,
    ) -> float:
        """
        Calculate material volume from mix ratio.
        """

        return round(
            dry_volume * part / total_parts,
            3,
        )

    @staticmethod
    def cement_bags(
        cement_volume: float,
    ) -> float:
        """
        Convert cement volume (m³)
        into number of bags.

        1 Bag = 0.035 m³
        """

        return round(
            cement_volume / 0.035,
            2,
        )

    # =====================================================
    # RESULT
    # =====================================================

    def get_result(self) -> CalculationResult:
        """
        Return calculation result.
        """

        return self.result