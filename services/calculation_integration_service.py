"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module : Calculation Integration Service
Purpose: Central integration between calculators,
         BOQ Controller and Material Controller.
=========================================================
"""

from __future__ import annotations

from typing import Any


class CalculationIntegrationService:
    """
    Central integration layer.

    Calculator
        ↓
    CalculationResult
        ↓
    CalculationIntegrationService
        ↓
    BOQ / Material Controllers
        ↓
    Database
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        boq_controller=None,
        material_controller=None,
    ):
        """
        Store application controllers.

        ApplicationContext passes these dependencies during
        application startup.
        """

        self.boq_controller = (
            boq_controller
        )

        self.material_controller = (
            material_controller
        )

    # =====================================================
    # PROJECT RATE DATABASE INTEGRATION
    # =====================================================

    @staticmethod
    def resolve_project_rates(
        rate_controller,
        project_id: int,
    ) -> dict:
        """
        Convert project-wise Rate Database records into the
        normalized rate dictionary expected by calculators.

        Unit aliases are intentionally normalized so rates saved as
        Bag/Bags and kg/Kg are both usable by the calculation layer.
        """
        if rate_controller is None:
            return {}

        try:
            items = rate_controller.get_by_project(int(project_id)) or []
        except Exception:
            return {}

        rates = {}

        aliases = {
            "cement": {"cement", "cement bag", "cement bags"},
            "sand": {"sand"},
            "aggregate": {"aggregate", "coarse aggregate", "coarse_aggregate"},
            "steel": {"steel", "reinforcement steel", "reinforcement_steel"},
            "binding_wire": {"binding wire", "binding_wire", "binding"},
            "skilled_labour": {"skilled labour", "skilled labor", "skilled_labour"},
            "unskilled_labour": {"unskilled labour", "unskilled labor", "unskilled_labour"},
        }

        for item in items:
            name = str(getattr(item, "item_name", "") or "").strip().lower()
            unit = str(getattr(item, "unit", "") or "").strip().lower()
            try:
                rate = float(getattr(item, "rate", 0) or 0)
            except (TypeError, ValueError):
                continue

            normalized_name = name.replace("_", " ").replace("-", " ")
            normalized_name = " ".join(normalized_name.split())

            # Main name aliases.
            for key, names in aliases.items():
                if normalized_name in names:
                    rates[key] = rate

            # Unit-aware aliases for direct calculator lookups.
            if normalized_name == "cement":
                rates["cement_bag"] = rate
                rates["cement_bags"] = rate
            elif normalized_name in {"coarse aggregate", "aggregate"}:
                rates["aggregate"] = rate
                rates["coarse_aggregate"] = rate
            elif normalized_name in {"reinforcement steel", "steel"}:
                rates["steel"] = rate
                rates["reinforcement_steel"] = rate
            elif normalized_name == "sand":
                rates["sand"] = rate
            elif normalized_name == "binding wire":
                rates["binding_wire"] = rate
                rates["binding"] = rate

            # Preserve a safe normalized key for future calculators.
            safe_name = normalized_name.replace(" ", "_")
            if safe_name:
                rates[safe_name] = rate

        return rates

    # =====================================================
    # BOQ INTEGRATION
    # =====================================================

    def generate_boq(
        self,
        calculation_type: str,
        result: Any,
        project_id: int,
        rate: float = 0.0,
    ):
        """
        Generate BOQ through BOQ Controller.
        """

        if result is None:
            raise ValueError(
                "Calculation result is required."
            )

        if self.boq_controller is None:
            raise ValueError(
                "BOQ Controller is not connected."
            )

        method = getattr(
            self.boq_controller,
            "generate_from_calculation",
            None,
        )

        if not callable(method):
            raise AttributeError(
                "BOQ Controller does not support "
                "calculator integration."
            )

        return method(
            calculation_type=calculation_type,
            result=result,
            project_id=project_id,
            rate=rate,
        )

    # =====================================================
    # MATERIAL INTEGRATION
    # =====================================================

    def generate_material(
        self,
        calculation_type: str,
        result: Any,
        project_id: int,
        rates: dict | None = None,
    ):
        """
        Generate Material records through Material Controller.
        """

        if result is None:
            raise ValueError(
                "Calculation result is required."
            )

        if self.material_controller is None:
            raise ValueError(
                "Material Controller is not connected."
            )

        method = getattr(
            self.material_controller,
            "generate_from_calculation",
            None,
        )

        if not callable(method):
            raise AttributeError(
                "Material Controller does not support "
                "calculator integration."
            )

        return method(
            calculation_type=calculation_type,
            result=result,
            project_id=project_id,
            rates=rates or {},
        )

    # =====================================================
    # MATERIAL ITEM BUILDER
    # =====================================================

    @classmethod
    def build_material_items(
        cls,
        calculation_type: str,
        result: Any,
        rates: dict | None = None,
        project_id: int | None = None,
    ) -> list[dict]:
        """
        Convert calculator result into material dictionaries.

        Currently supported:
            RCC
        """

        if result is None:
            raise ValueError(
                "Calculation result is required."
            )

        if project_id is None:
            raise ValueError(
                "Project ID is required."
            )

        try:
            project_id = int(
                project_id
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "Project ID must be numeric."
            ) from exc

        if project_id <= 0:
            raise ValueError(
                "Project ID must be greater than zero."
            )

        calculation_type = (
            cls._normalize_type(
                calculation_type
            )
        )

        rates = rates or {}

        # -------------------------------------------------
        # Generic calculator result support
        # -------------------------------------------------
        # Current calculators return a calculation dictionary
        # containing MATERIALS/materials. Older integration code
        # only understood an object with named attributes, which
        # caused:
        # "No material quantities were found..."
        #
        # Prefer the calculator's own material schedule when it is
        # available. This keeps the exact calculator quantities,
        # units and rates instead of trying to reconstruct them.
        embedded = cls._get_embedded_materials(result)

        if embedded:
            return cls._build_embedded_materials(
                embedded=embedded,
                rates=rates,
                project_id=project_id,
                calculation_type=calculation_type,
            )

        if calculation_type == "RCC":

            return cls._build_rcc_materials(
                result=result,
                rates=rates,
                project_id=project_id,
            )

        if calculation_type == "PCC":

            return cls._build_pcc_materials(
                result=result,
                rates=rates,
                project_id=project_id,
            )

        raise ValueError(
            "No material quantities were found for "
            f"'{calculation_type}' calculation. "
            "The calculator result contains no MATERIALS schedule."
        )

    # =====================================================
    # GENERIC EMBEDDED MATERIAL SCHEDULE
    # =====================================================

    @staticmethod
    def _get_embedded_materials(result: Any) -> list:
        """
        Read the calculator's embedded MATERIALS schedule.

        Supports plain dictionaries, Mapping-like results, result
        objects exposing to_dict(), and result objects exposing a
        values dictionary.
        """
        candidates = [result]

        to_dict = getattr(result, "to_dict", None)
        if callable(to_dict):
            try:
                payload = to_dict()
                if payload is not None:
                    candidates.append(payload)
            except Exception:
                pass

        values = getattr(result, "values", None)
        if isinstance(values, dict):
            candidates.append(values)

        for candidate in candidates:
            if isinstance(candidate, dict):
                for key in ("MATERIALS", "materials", "Materials"):
                    value = candidate.get(key)
                    if isinstance(value, (list, tuple)):
                        return list(value)

            getter = getattr(candidate, "get", None)
            if callable(getter):
                for key in ("MATERIALS", "materials", "Materials"):
                    try:
                        value = getter(key, None)
                    except TypeError:
                        try:
                            value = getter(key)
                        except Exception:
                            value = None
                    except Exception:
                        value = None

                    if isinstance(value, (list, tuple)):
                        return list(value)

        return []

    @classmethod
    def _build_embedded_materials(
        cls,
        embedded: list,
        rates: dict,
        project_id: int,
        calculation_type: str,
    ) -> list[dict]:
        """
        Convert a calculator's own material schedule into the
        standard Material model dictionaries.

        Supports both lower-case dataclass-style keys and the
        upper-case keys used by existing calculator result dicts.
        """
        materials = []

        for raw in embedded:
            if not isinstance(raw, dict):
                continue

            def pick(*names, default=None):
                for name in names:
                    if name in raw and raw[name] is not None:
                        return raw[name]
                return default

            name = pick(
                "material_name", "MATERIAL", "NAME", "name",
                default=""
            )
            unit = pick(
                "unit", "UNIT", "Unit",
                default="Nos"
            )
            quantity = pick(
                "quantity", "QUANTITY", "QTY", "qty",
                default=0
            )
            rate = pick(
                "rate", "RATE",
                default=None
            )
            amount = pick(
                "amount", "AMOUNT",
                default=None
            )

            name = str(name).strip()
            unit = str(unit).strip()

            try:
                quantity = float(quantity or 0)
            except (TypeError, ValueError):
                quantity = 0.0

            if rate is None:
                rate = cls._get_rate(
                    rates,
                    (
                        name.lower(),
                        name.lower().replace(" ", "_"),
                    ),
                )
            else:
                try:
                    rate = float(rate or 0)
                except (TypeError, ValueError):
                    rate = 0.0

            # If the calculator supplied amount, retain its exact
            # quantity/rate relationship only when possible.
            # Material model amount is always quantity * rate.
            if quantity <= 0 or not name:
                continue

            if rate <= 0 and amount is not None:
                try:
                    supplied_amount = float(amount or 0)
                    if quantity > 0:
                        rate = supplied_amount / quantity
                except (TypeError, ValueError):
                    pass

            remarks = pick(
                "remarks", "REMARKS", "Remarks",
                default=f"Generated from {calculation_type} calculator."
            )

            materials.append(
                cls._material(
                    project_id=project_id,
                    material_name=name,
                    unit=unit,
                    quantity=quantity,
                    rate=rate,
                    remarks=str(remarks or ""),
                )
            )

        return materials

    # =====================================================
    # PCC MATERIALS
    # =====================================================

    @classmethod
    def _build_pcc_materials(
        cls,
        result: Any,
        rates: dict,
        project_id: int,
    ) -> list[dict]:
        """Fallback PCC material builder for older result objects."""
        concrete_volume = cls._get_value(
            result,
            ("wet_volume", "wet_concrete", "concrete_volume", "volume", "quantity"),
            0.0,
        )

        cement_bags = cls._get_value(
            result, ("cement_bags", "cement"), 0.0
        )
        sand = cls._get_value(
            result, ("sand", "sand_volume"), 0.0
        )
        aggregate = cls._get_value(
            result, ("aggregate", "coarse_aggregate", "aggregate_volume"),
            0.0,
        )

        materials = []

        if cement_bags > 0:
            materials.append(cls._material(
                project_id, "Cement", "Bags", cement_bags,
                cls._get_rate(rates, ("cement", "cement_bag", "cement_bags")),
                f"Generated from PCC calculation. Concrete volume: {concrete_volume:,.3f}",
            ))

        if sand > 0:
            materials.append(cls._material(
                project_id, "Sand", "m³", sand,
                cls._get_rate(rates, ("sand",)),
                "Generated from PCC calculation.",
            ))

        if aggregate > 0:
            materials.append(cls._material(
                project_id, "Coarse Aggregate", "m³", aggregate,
                cls._get_rate(rates, ("aggregate", "coarse_aggregate")),
                "Generated from PCC calculation.",
            ))

        return materials

    # =====================================================
    # RCC MATERIALS
    # =====================================================

    @classmethod
    def _build_rcc_materials(
        cls,
        result: Any,
        rates: dict,
        project_id: int,
    ) -> list[dict]:
        """
        Build RCC material records.

        Materials:
            Cement
            Sand
            Coarse Aggregate
            Reinforcement Steel
            Binding Wire
        """

        materials = []

        # -------------------------------------------------
        # Concrete Volume
        # -------------------------------------------------

        concrete_volume = cls._get_value(
            result,
            (
                "concrete_volume",
                "volume",
                "quantity",
            ),
            0.0,
        )

        # -------------------------------------------------
        # Cement
        # -------------------------------------------------

        cement_bags = cls._get_value(
            result,
            (
                "cement_bags",
            ),
            0.0,
        )

        if cement_bags > 0:

            materials.append(
                cls._material(
                    project_id=project_id,
                    material_name="Cement",
                    unit="Bags",
                    quantity=cement_bags,
                    rate=cls._get_rate(
                        rates,
                        (
                            "cement",
                            "cement_bag",
                            "cement_bags",
                        ),
                    ),
                    remarks=(
                        "Generated from RCC calculation. "
                        f"Concrete volume: "
                        f"{concrete_volume:,.3f} m³"
                    ),
                )
            )

        # -------------------------------------------------
        # Sand
        # -------------------------------------------------

        sand = cls._get_value(
            result,
            (
                "sand",
                "sand_volume",
            ),
            0.0,
        )

        if sand > 0:

            materials.append(
                cls._material(
                    project_id=project_id,
                    material_name="Sand",
                    unit="m³",
                    quantity=sand,
                    rate=cls._get_rate(
                        rates,
                        (
                            "sand",
                        ),
                    ),
                    remarks=(
                        "Generated from RCC calculation."
                    ),
                )
            )

        # -------------------------------------------------
        # Coarse Aggregate
        # -------------------------------------------------

        aggregate = cls._get_value(
            result,
            (
                "aggregate",
                "aggregate_volume",
            ),
            0.0,
        )

        if aggregate > 0:

            materials.append(
                cls._material(
                    project_id=project_id,
                    material_name="Coarse Aggregate",
                    unit="m³",
                    quantity=aggregate,
                    rate=cls._get_rate(
                        rates,
                        (
                            "aggregate",
                            "coarse_aggregate",
                        ),
                    ),
                    remarks=(
                        "Generated from RCC calculation."
                    ),
                )
            )

        # -------------------------------------------------
        # Reinforcement Steel
        # -------------------------------------------------

        steel = cls._get_value(
            result,
            (
                "steel_kg",
                "steel_weight",
                "steel",
            ),
            0.0,
        )

        if steel > 0:

            materials.append(
                cls._material(
                    project_id=project_id,
                    material_name="Reinforcement Steel",
                    unit="Kg",
                    quantity=steel,
                    rate=cls._get_rate(
                        rates,
                        (
                            "steel",
                            "reinforcement_steel",
                        ),
                    ),
                    remarks=(
                        "Generated from RCC calculation."
                    ),
                )
            )

        # -------------------------------------------------
        # Binding Wire
        # -------------------------------------------------

        binding_percentage = cls._get_value(
            result,
            (
                "binding_wire",
                "binding_wire_percent",
            ),
            0.0,
        )

        if (
            binding_percentage > 0
            and steel > 0
        ):

            binding_wire_kg = (
                steel
                * binding_percentage
                / 100.0
            )

            materials.append(
                cls._material(
                    project_id=project_id,
                    material_name="Binding Wire",
                    unit="Kg",
                    quantity=binding_wire_kg,
                    rate=cls._get_rate(
                        rates,
                        (
                            "binding_wire",
                            "binding",
                        ),
                    ),
                    remarks=(
                        f"Calculated at "
                        f"{binding_percentage:,.2f}% "
                        "of reinforcement steel."
                    ),
                )
            )

        return materials

    # =====================================================
    # MATERIAL DICTIONARY
    # =====================================================

    @staticmethod
    def _material(
        project_id: int,
        material_name: str,
        unit: str,
        quantity: float,
        rate: float,
        remarks: str = "",
    ) -> dict:

        quantity = float(
            quantity
        )

        rate = float(
            rate
        )

        return {
            "project_id": project_id,
            "material_name": material_name,
            "unit": unit,
            "quantity": round(
                quantity,
                3,
            ),
            "rate": round(
                rate,
                2,
            ),
            "amount": round(
                quantity * rate,
                2,
            ),
            "remarks": remarks,
        }

    # =====================================================
    # RESULT VALUE READER
    # =====================================================

    @staticmethod
    def _get_value(
        result: Any,
        names: tuple[str, ...],
        default: float = 0.0,
    ) -> float:

        for name in names:

            # -------------------------------------------------
            # Direct dictionary
            # -------------------------------------------------

            if isinstance(result, dict):
                for key in (name, name.upper(), name.lower()):
                    if key in result and result[key] is not None:
                        try:
                            return float(result[key])
                        except (TypeError, ValueError):
                            pass

            # -------------------------------------------------
            # get_value()
            # -------------------------------------------------

            getter = getattr(
                result,
                "get_value",
                None,
            )

            if callable(getter):

                try:

                    value = getter(
                        name,
                        None,
                    )

                    if value is not None:

                        return float(
                            value
                        )

                except (
                    TypeError,
                    ValueError,
                ):
                    pass

            # -------------------------------------------------
            # values dictionary
            # -------------------------------------------------

            values = getattr(
                result,
                "values",
                None,
            )

            if isinstance(
                values,
                dict,
            ):

                value = values.get(
                    name,
                    None,
                )

                if value is not None:

                    try:

                        return float(
                            value
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):
                        pass

            # -------------------------------------------------
            # Direct attribute
            # -------------------------------------------------

            value = getattr(
                result,
                name,
                None,
            )

            if value is not None:

                try:

                    return float(
                        value
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    pass

        return float(
            default
        )

    # =====================================================
    # RATE READER
    # =====================================================

    @staticmethod
    def _get_rate(
        rates: dict,
        names: tuple[str, ...],
    ) -> float:

        if not isinstance(
            rates,
            dict,
        ):

            return 0.0

        for name in names:

            if name not in rates:
                continue

            try:

                value = float(
                    rates[name]
                )

            except (
                TypeError,
                ValueError,
            ) as exc:

                raise ValueError(
                    f"Invalid rate for '{name}'."
                ) from exc

            if value < 0:

                raise ValueError(
                    f"Rate for '{name}' "
                    "cannot be negative."
                )

            return value

        return 0.0

    # =====================================================
    # CALCULATION TYPE
    # =====================================================

    @staticmethod
    def _normalize_type(
        calculation_type: str,
    ) -> str:

        if calculation_type is None:

            raise ValueError(
                "Calculation type is required."
            )

        value = (
            str(calculation_type)
            .strip()
            .upper()
        )

        value = (
            value
            .replace("-", "_")
            .replace(" ", "_")
        )

        aliases = {
            "RCC": "RCC",
            "RCC_CALCULATOR": "RCC",
            "REINFORCED_CONCRETE": "RCC",
            "REINFORCED_CEMENT_CONCRETE": "RCC",

            "PCC": "PCC",
            "PCC_CALCULATOR": "PCC",

            "BRICKWORK": "BRICKWORK",
            "BRICK_WORK": "BRICKWORK",
            "BRICKWORK_CALCULATOR": "BRICKWORK",
            "EXCAVATION": "EXCAVATION",
            "EXCAVATION_CALCULATOR": "EXCAVATION",
            "PLASTER": "PLASTER",
            "PLASTER_CALCULATOR": "PLASTER",
            "STEEL": "STEEL",
            "STEEL_CALCULATOR": "STEEL",
            "SLAB_STEEL": "SLAB_STEEL",
            "SLAB_STEEL_CALCULATOR": "SLAB_STEEL",
            "COLUMN_STEEL": "COLUMN_STEEL",
            "COLUMN_STEEL_CALCULATOR": "COLUMN_STEEL",
            "BEAM_STEEL": "BEAM_STEEL",
            "BEAM_STEEL_CALCULATOR": "BEAM_STEEL",
            "FOOTING": "FOOTING",
            "FOOTING_CALCULATOR": "FOOTING",
            "FOUNDATION": "FOOTING",
            "STAIRCASE": "STAIRCASE",
            "STAIRCASE_CALCULATOR": "STAIRCASE",
        }

        return aliases.get(
            value,
            value,
        )


# =========================================================
# Standalone Test
# =========================================================

if __name__ == "__main__":

    class TestResult:

        values = {
            "concrete_volume": 10.0,
            "cement_bags": 73.0,
            "sand": 5.0,
            "aggregate": 10.0,
            "steel_kg": 500.0,
            "binding_wire": 2.5,
        }

        def get_value(
            self,
            key,
            default=0,
        ):

            return self.values.get(
                key,
                default,
            )

    result = TestResult()

    service = (
        CalculationIntegrationService(
            boq_controller=None,
            material_controller=None,
        )
    )

    materials = (
        service.build_material_items(
            calculation_type="RCC",
            result=result,
            project_id=1,
            rates={
                "cement": 1500,
                "sand": 3000,
                "aggregate": 3500,
                "steel": 250,
                "binding_wire": 300,
            },
        )
    )

    for material in materials:

        print(
            material
        )