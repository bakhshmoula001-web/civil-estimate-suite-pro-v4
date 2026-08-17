"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Calculator Page
Purpose   : Engineering Calculator Hub
Author    : OpenAI + Moula Bakhsh
Version   : 4.0.0
=========================================================
"""

from __future__ import annotations

import importlib
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk


class CalculatorPage(ctk.CTkFrame):
    """
    Central Engineering Calculator Page.

    Responsibilities
    ----------------
    • Display available calculators
    • Open calculator forms
    • Keep calculator navigation independent
    • Provide a clean extension point for future calculators

    The actual engineering calculations remain inside the
    calculator forms/calculation layer.
    """

    PAGE_TITLE = "Engineering Calculators"

    CALCULATORS = (
        {
            "key": "excavation",
            "title": "Excavation",
            "description": "Calculate excavation quantity.",
            "module": "gui.forms.excavation_calculator_form",
            "class": "ExcavationCalculatorForm",
        },
        {
            "key": "pcc",
            "title": "PCC",
            "description": "Plain Cement Concrete calculator.",
            "module": "gui.forms.pcc_calculator_form",
            "class": "PCCCalculatorForm",
        },
        {
            "key": "rcc",
            "title": "RCC",
            "description": "Reinforced Cement Concrete calculator.",
            "module": "gui.forms.rcc_calculator_form",
            "class": "RCCCalculatorForm",
        },
        {
            "key": "brickwork",
            "title": "Brickwork",
            "description": "Brick masonry quantity calculator.",
            "module": "gui.forms.brickwork_calculator_form",
            "class": "BrickworkCalculatorForm",
        },
        {
            "key": "plaster",
            "title": "Plaster",
            "description": "Plaster quantity calculator.",
            "module": "gui.forms.plaster_calculator_form",
            "class": "PlasterCalculatorForm",
        },
        {
            "key": "steel",
            "title": "Steel Weight",
            "description": "Calculate reinforcement steel weight.",
            "module": "gui.forms.steel_calculator_form",
            "class": "SteelCalculatorForm",
        },
        {
            "key": "slab_steel",
            "title": "Slab Steel",
            "description": "Calculate slab reinforcement.",
            "module": "gui.forms.slab_steel_calculator_form",
            "class": "SlabSteelCalculatorForm",
        },
        {
            "key": "column_steel",
            "title": "Column Steel",
            "description": "Calculate column reinforcement and stirrups.",
            "module": "gui.forms.column_steel_calculator_form",
            "class": "ColumnSteelCalculatorForm",
        },
        {
            "key": "beam_steel",
            "title": "Beam Steel",
            "description": "Calculate beam reinforcement and stirrups.",
            "module": "gui.forms.beam_steel_calculator_form",
            "class": "BeamSteelCalculatorForm",
        },
        {
            "key": "footing",
            "title": "Footing / Foundation",
            "description": "Calculate footing concrete, reinforcement, materials and labour.",
            "module": "gui.forms.footing_calculator_form",
            "class": "FootingCalculatorForm",
        },
        {
            "key": "staircase",
            "title": "Staircase",
            "description": "Calculate staircase concrete, reinforcement, materials and labour.",
            "module": "gui.forms.staircase_calculator_form",
            "class": "StaircaseCalculatorForm",
        },
    )

    def __init__(
        self,
        master,
        context=None,
        window_manager=None,
    ):
        super().__init__(master)

        self.context = context
        self.window_manager = window_manager

        self._buttons: dict[str, ctk.CTkButton] = {}
        self._build_page()

    # =========================================================
    # PAGE BUILD
    # =========================================================

    def _build_page(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_calculator_area()

    # =========================================================
    # HEADER
    # =========================================================

    def _build_header(self):
        header = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="transparent",
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=(20, 10),
        )

        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text=self.PAGE_TITLE,
            font=ctk.CTkFont(
                size=28,
                weight="bold",
            ),
        )

        title.grid(
            row=0,
            column=0,
            sticky="w",
        )

        subtitle = ctk.CTkLabel(
            header,
            text=(
                "Select an engineering calculator to perform "
                "quantity and material calculations."
            ),
            font=ctk.CTkFont(
                size=14,
            ),
        )

        subtitle.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(4, 0),
        )

    # =========================================================
    # CALCULATOR AREA
    # =========================================================

    def _build_calculator_area(self):
        container = ctk.CTkScrollableFrame(
            self,
            corner_radius=10,
        )

        container.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=20,
            pady=(0, 20),
        )

        columns = 3

        for column in range(columns):
            container.grid_columnconfigure(
                column,
                weight=1,
            )

        for index, calculator in enumerate(self.CALCULATORS):
            row = index // columns
            column = index % columns

            self._create_calculator_card(
                container,
                calculator,
                row,
                column,
            )

    # =========================================================
    # CALCULATOR CARD
    # =========================================================

    def _create_calculator_card(
        self,
        parent,
        calculator: dict,
        row: int,
        column: int,
    ):
        card = ctk.CTkFrame(
            parent,
            corner_radius=12,
        )

        card.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=8,
            pady=8,
        )

        card.grid_columnconfigure(
            0,
            weight=1,
        )

        title = ctk.CTkLabel(
            card,
            text=calculator["title"],
            font=ctk.CTkFont(
                size=20,
                weight="bold",
            ),
        )

        title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=(18, 5),
        )

        description = ctk.CTkLabel(
            card,
            text=calculator["description"],
            justify="left",
            anchor="w",
            wraplength=260,
        )

        description.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=18,
            pady=(0, 15),
        )

        button = ctk.CTkButton(
            card,
            text="Open Calculator",
            height=38,
            command=lambda key=calculator["key"]:
                self.open_calculator(key),
        )

        button.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=18,
            pady=(0, 18),
        )

        self._buttons[calculator["key"]] = button

    # =========================================================
    # OPEN CALCULATOR
    # =========================================================

    def open_calculator(self, calculator_key: str):
        """
        Open the selected calculator form.

        Imports are deliberately performed here instead of at
        module import time. This prevents one optional calculator
        from breaking the complete Calculator Page.
        """

        calculator = self._find_calculator(
            calculator_key
        )

        if calculator is None:
            messagebox.showerror(
                "Calculator",
                f"Calculator '{calculator_key}' is not registered.",
                parent=self,
            )
            return

        try:
            module = importlib.import_module(
                calculator["module"]
            )

            form_class = getattr(
                module,
                calculator["class"],
            )

        except ModuleNotFoundError as error:
            messagebox.showerror(
                "Calculator Module Missing",
                (
                    f"The {calculator['title']} calculator "
                    "form could not be loaded.\n\n"
                    f"Module:\n{calculator['module']}\n\n"
                    f"Error:\n{error}"
                ),
                parent=self,
            )
            return

        except AttributeError as error:
            messagebox.showerror(
                "Calculator Class Missing",
                (
                    f"The calculator module was found, "
                    "but the expected form class is missing.\n\n"
                    f"Class:\n{calculator['class']}\n\n"
                    f"Error:\n{error}"
                ),
                parent=self,
            )
            return

        except Exception as error:
            messagebox.showerror(
                "Calculator Load Error",
                str(error),
                parent=self,
            )
            return

        try:
            form = form_class(
                self.winfo_toplevel()
            )

            self._prepare_form(
                form,
                calculator,
            )

        except Exception as error:
            messagebox.showerror(
                "Calculator Error",
                (
                    f"Unable to open "
                    f"{calculator['title']} calculator.\n\n"
                    f"{error}"
                ),
                parent=self,
            )

    # =========================================================
    # FORM PREPARATION
    # =========================================================

    def _prepare_form(
        self,
        form,
        calculator: dict,
    ):
        """
        Attach common runtime information to calculator forms.

        Existing calculator forms do not need to depend on this
        method. It simply provides optional references for the
        next integration stage.
        """

        try:
            form.calculator_key = calculator["key"]
        except Exception:
            pass

        try:
            form.calculator_page = self
        except Exception:
            pass

        try:
            form.application_context = self.context
        except Exception:
            pass

        try:
            form.window_manager = self.window_manager
        except Exception:
            pass

    # =========================================================
    # LOOKUP
    # =========================================================

    def _find_calculator(
        self,
        calculator_key: str,
    ) -> dict | None:

        normalized_key = str(
            calculator_key
        ).strip().lower()

        for calculator in self.CALCULATORS:
            if calculator["key"] == normalized_key:
                return calculator

        return None

    # =========================================================
    # REFRESH
    # =========================================================

    def refresh(self):
        """
        Refresh hook used by WindowManager.

        Calculator forms are independent windows, therefore
        there is currently no database refresh required here.
        """

        return None

    # =========================================================
    # SEARCH
    # =========================================================

    def search(self, keyword: str):
        """
        Search calculator cards by title or description.
        """

        keyword = str(
            keyword or ""
        ).strip().lower()

        for calculator in self.CALCULATORS:
            button = self._buttons.get(
                calculator["key"]
            )

            if button is None:
                continue

            searchable = (
                f"{calculator['title']} "
                f"{calculator['description']}"
            ).lower()

            if not keyword or keyword in searchable:
                button.grid()
            else:
                button.grid_remove()

    # =========================================================
    # CURRENT PAGE
    # =========================================================

    def get_calculator(
        self,
        calculator_key: str,
    ):
        """
        Return the registered calculator metadata.
        """

        return self._find_calculator(
            calculator_key
        )


__all__ = [
    "CalculatorPage",
]
