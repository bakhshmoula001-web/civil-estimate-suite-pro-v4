"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : BOQ Form
Purpose   : Create / Edit BOQ Item
Version   : 4.0.0
=========================================================
"""

from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox

from core.current_project import CurrentProject
from models.boq import BOQ


class BOQForm(ctk.CTkToplevel):
    """
    Professional BOQ entry dialog.

    The form is intentionally self-contained so it does not
    depend on unstable helper/validation implementations.

    Result
    ------
    self.result is None when cancelled.

    self.result contains a validated BOQ object when saved.
    """

    WIDTH = 720
    HEIGHT = 650

    UNIT_OPTIONS = [
        "Nos",
        "inch",
        "rft",
        "sft",
        "cft",
        "sq-yard",
        "cm",
        "m",
        "m²",
        "m³",
        "kg",
        "Ton",
        "L.S",
    ]

    def __init__(
        self,
        parent,
        boq: BOQ | None = None,
        project=None,
    ):
        super().__init__(parent)

        self.parent = parent
        self.boq = boq
        self.result = None

        # Accept an explicitly supplied project from BOQPage while
        # retaining compatibility with older callers.
        self.project = project if project is not None else self._get_current_project()

        self.item_no_var = ctk.StringVar()
        self.description_var = ctk.StringVar()
        self.unit_var = ctk.StringVar(value="Nos")
        self.quantity_var = ctk.StringVar(value="0")
        self.rate_var = ctk.StringVar(value="0")
        self.amount_var = ctk.StringVar(value="0.00")
        self.remarks_var = ctk.StringVar()

        self._configure_window()
        self._build_ui()
        self._bind_calculation_events()

        if self.boq is not None:
            self.load_data(self.boq)
        else:
            self._update_amount()

        self._make_modal()

    # =====================================================
    # WINDOW
    # =====================================================

    def _configure_window(self) -> None:
        title = (
            "Edit BOQ Item"
            if self.boq is not None
            else "New BOQ Item"
        )

        self.title(title)
        self.geometry(
            f"{self.WIDTH}x{self.HEIGHT}"
        )
        self.resizable(False, False)
        self.transient(self.parent)

        self.protocol(
            "WM_DELETE_WINDOW",
            self.cancel,
        )

    def _make_modal(self) -> None:
        self.grab_set()
        self.focus_force()

        try:
            self.lift()
        except Exception:
            pass

    # =====================================================
    # PROJECT
    # =====================================================

    def _get_current_project(self):
        try:
            return CurrentProject.get()
        except Exception:
            return None

    def _project_text(self) -> str:
        if self.project is None:
            return "No project selected"

        code = str(
            getattr(
                self.project,
                "project_code",
                "",
            )
        ).strip()

        name = str(
            getattr(
                self.project,
                "project_name",
                "",
            )
        ).strip()

        if code and name:
            return f"{code} - {name}"

        return code or name or "Current Project"

    # =====================================================
    # UI
    # =====================================================

    def _build_ui(self) -> None:
        outer = ctk.CTkFrame(
            self,
            corner_radius=10,
        )

        outer.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18,
        )

        outer.grid_columnconfigure(
            1,
            weight=1,
        )

        row = 0

        # -------------------------------------------------
        # Project
        # -------------------------------------------------

        self._create_label(
            outer,
            "Project",
            row,
        )

        self.project_label = ctk.CTkLabel(
            outer,
            text=self._project_text(),
            anchor="w",
        )

        self.project_label.grid(
            row=row,
            column=1,
            padx=10,
            pady=7,
            sticky="ew",
        )

        row += 1

        # -------------------------------------------------
        # Item No
        # -------------------------------------------------

        self._create_entry(
            outer,
            "Item No",
            self.item_no_var,
            row,
        )

        row += 1

        # -------------------------------------------------
        # Description
        # -------------------------------------------------

        self._create_entry(
            outer,
            "Description",
            self.description_var,
            row,
        )

        row += 1

        # -------------------------------------------------
        # Unit
        # -------------------------------------------------

        self._create_label(
            outer,
            "Unit",
            row,
        )

        self.unit_combo = ctk.CTkComboBox(
            outer,
            variable=self.unit_var,
            values=self.UNIT_OPTIONS,
            width=350,
        )

        self.unit_combo.grid(
            row=row,
            column=1,
            padx=10,
            pady=7,
            sticky="ew",
        )

        row += 1

        # -------------------------------------------------
        # Quantity
        # -------------------------------------------------

        self._create_entry(
            outer,
            "Quantity",
            self.quantity_var,
            row,
        )

        row += 1

        # -------------------------------------------------
        # Rate
        # -------------------------------------------------

        self._create_entry(
            outer,
            "Rate",
            self.rate_var,
            row,
        )

        row += 1

        # -------------------------------------------------
        # Amount
        # -------------------------------------------------

        self._create_label(
            outer,
            "Amount",
            row,
        )

        self.amount_entry = ctk.CTkEntry(
            outer,
            textvariable=self.amount_var,
            width=350,
            state="readonly",
        )

        self.amount_entry.grid(
            row=row,
            column=1,
            padx=10,
            pady=7,
            sticky="ew",
        )

        row += 1

        # -------------------------------------------------
        # Remarks
        # -------------------------------------------------

        self._create_entry(
            outer,
            "Remarks",
            self.remarks_var,
            row,
        )

        row += 1

        # -------------------------------------------------
        # Separator / info
        # -------------------------------------------------

        self.info_label = ctk.CTkLabel(
            outer,
            text="Amount = Quantity × Rate",
            anchor="w",
        )

        self.info_label.grid(
            row=row,
            column=0,
            columnspan=2,
            padx=10,
            pady=(12, 5),
            sticky="w",
        )

        row += 1

        self.status_label = ctk.CTkLabel(
            outer,
            text="Ready",
            anchor="w",
        )

        self.status_label.grid(
            row=row,
            column=0,
            columnspan=2,
            padx=10,
            pady=5,
            sticky="w",
        )

        row += 1

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        button_frame = ctk.CTkFrame(
            outer,
            fg_color="transparent",
        )

        button_frame.grid(
            row=row,
            column=0,
            columnspan=2,
            padx=10,
            pady=(12, 5),
            sticky="e",
        )

        self.cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=110,
            command=self.cancel,
        )

        self.cancel_button.pack(
            side="left",
            padx=5,
        )

        self.save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            width=120,
            command=self.save,
        )

        self.save_button.pack(
            side="left",
            padx=5,
        )

    def _create_label(
        self,
        parent,
        text: str,
        row: int,
    ) -> None:
        ctk.CTkLabel(
            parent,
            text=text,
        ).grid(
            row=row,
            column=0,
            padx=10,
            pady=7,
            sticky="w",
        )

    def _create_entry(
        self,
        parent,
        label: str,
        variable,
        row: int,
    ):
        self._create_label(
            parent,
            label,
            row,
        )

        entry = ctk.CTkEntry(
            parent,
            textvariable=variable,
            width=350,
        )

        entry.grid(
            row=row,
            column=1,
            padx=10,
            pady=7,
            sticky="ew",
        )

        return entry

    # =====================================================
    # CALCULATION
    # =====================================================

    def _bind_calculation_events(self) -> None:
        self.quantity_var.trace_add(
            "write",
            self._on_numeric_change,
        )

        self.rate_var.trace_add(
            "write",
            self._on_numeric_change,
        )

    def _on_numeric_change(
        self,
        *_,
    ) -> None:
        self._update_amount()

    def _to_float(
        self,
        value: str,
    ) -> float:
        value = str(
            value or ""
        ).strip()

        if value == "":
            return 0.0

        return float(value)

    def _update_amount(self) -> None:
        try:
            quantity = self._to_float(
                self.quantity_var.get()
            )

            rate = self._to_float(
                self.rate_var.get()
            )

            amount = quantity * rate

            self.amount_var.set(
                f"{amount:,.2f}"
            )

            self.status_label.configure(
                text="Amount calculated automatically."
            )

        except (TypeError, ValueError):
            self.amount_var.set(
                "0.00"
            )

            self.status_label.configure(
                text="Enter numeric Quantity and Rate."
            )

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(self) -> bool:
        if self.project is None:
            messagebox.showerror(
                "BOQ Validation",
                "No project is currently selected.",
                parent=self,
            )
            return False

        item_no = self.item_no_var.get().strip()

        if not item_no:
            messagebox.showerror(
                "BOQ Validation",
                "Item No is required.",
                parent=self,
            )
            return False

        description = (
            self.description_var.get().strip()
        )

        if not description:
            messagebox.showerror(
                "BOQ Validation",
                "Description is required.",
                parent=self,
            )
            return False

        unit = self.unit_var.get().strip()

        if not unit:
            messagebox.showerror(
                "BOQ Validation",
                "Unit is required.",
                parent=self,
            )
            return False

        try:
            quantity = self._to_float(
                self.quantity_var.get()
            )
        except (TypeError, ValueError):
            messagebox.showerror(
                "BOQ Validation",
                "Quantity must be a valid number.",
                parent=self,
            )
            return False

        if quantity <= 0:
            messagebox.showerror(
                "BOQ Validation",
                "Quantity must be greater than zero.",
                parent=self,
            )
            return False

        try:
            rate = self._to_float(
                self.rate_var.get()
            )
        except (TypeError, ValueError):
            messagebox.showerror(
                "BOQ Validation",
                "Rate must be a valid number.",
                parent=self,
            )
            return False

        if rate < 0:
            messagebox.showerror(
                "BOQ Validation",
                "Rate cannot be negative.",
                parent=self,
            )
            return False

        return True

    # =====================================================
    # DATA
    # =====================================================

    def collect_data(self) -> BOQ:
        if self.project is None:
            raise ValueError(
                "No project selected."
            )

        quantity = self._to_float(
            self.quantity_var.get()
        )

        rate = self._to_float(
            self.rate_var.get()
        )

        amount = round(
            quantity * rate,
            2,
        )

        project_id = getattr(
            self.project,
            "id",
            None,
        )

        return BOQ(
            id=(
                self.boq.id
                if self.boq is not None
                else None
            ),
            project_id=project_id,
            item_no=(
                self.item_no_var
                .get()
                .strip()
            ),
            description=(
                self.description_var
                .get()
                .strip()
            ),
            unit=(
                self.unit_var
                .get()
                .strip()
            ),
            quantity=quantity,
            rate=rate,
            amount=amount,
            remarks=(
                self.remarks_var
                .get()
                .strip()
            ),
        )

    # =====================================================
    # LOAD EDIT DATA
    # =====================================================

    def load_data(
        self,
        boq: BOQ,
    ) -> None:
        self.item_no_var.set(
            str(
                getattr(
                    boq,
                    "item_no",
                    "",
                )
            )
        )

        self.description_var.set(
            str(
                getattr(
                    boq,
                    "description",
                    "",
                )
            )
        )

        unit = str(
            getattr(
                boq,
                "unit",
                "Nos",
            )
        )

        if unit:
            self.unit_var.set(unit)
        else:
            self.unit_var.set("Nos")

        self.quantity_var.set(
            str(
                getattr(
                    boq,
                    "quantity",
                    0,
                )
            )
        )

        self.rate_var.set(
            str(
                getattr(
                    boq,
                    "rate",
                    0,
                )
            )
        )

        self.remarks_var.set(
            str(
                getattr(
                    boq,
                    "remarks",
                    "",
                )
            )
        )

        self._update_amount()

    # =====================================================
    # SAVE
    # =====================================================

    def save(self) -> None:
        if not self.validate():
            return

        try:
            result = self.collect_data()

            # Final model-level validation.
            result.validate()

            self.result = result

            self.status_label.configure(
                text="BOQ item ready to save."
            )

            self._close()

        except Exception as exc:
            messagebox.showerror(
                "BOQ Save Error",
                str(exc),
                parent=self,
            )

    # =====================================================
    # CANCEL / CLOSE
    # =====================================================

    def cancel(self) -> None:
        self.result = None
        self._close()

    def _close(self) -> None:
        try:
            self.grab_release()
        except Exception:
            pass

        self.destroy()
