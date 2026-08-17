from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox

from core.current_project import CurrentProject
from gui.forms.base_form import BaseForm

from models.material import Material

from gui.forms.material_form_helpers import MaterialFormHelpers
from gui.forms.material_form_validation import MaterialFormValidation


class MaterialForm(BaseForm):
    """
    Material Entry Dialog
    """

    def __init__(
        self,
        parent,
        material: Material | None = None,
    ):

        super().__init__(
            parent,
            title="Material",
            width=720,
            height=600,
        )

        self.material = material

        self.project = CurrentProject.get()

        self.vars = {

            "material_name": ctk.StringVar(),

            "unit": ctk.StringVar(value="Nos"),

            "quantity": ctk.StringVar(value="0"),

            "rate": ctk.StringVar(value="0"),

            "amount": ctk.StringVar(value="0.00"),

            "remarks": ctk.StringVar(),
        }

        self._build_form()

        self.vars["quantity"].trace_add(
            "write",
            self.calculate_amount,
        )

        self.vars["rate"].trace_add(
            "write",
            self.calculate_amount,
        )

        if material is not None:
            self.load_data(material)
    def _build_form(self):

        frame = self.content_frame

        frame.grid_columnconfigure(
            1,
            weight=1,
    )

        row = 0

    # ------------------------------
    # Project
    # ------------------------------

        ctk.CTkLabel(
            frame,
            text="Project",
        ).grid(
            row=row,
            column=0,
            padx=10,
            pady=8,
            sticky="w",
       )

        project_name = ""

        if self.project:

            project_name = (
                f"{self.project.project_code}"
                f" - "
                f"{self.project.project_name}"
        )

        ctk.CTkLabel(
            frame,
            text=project_name,
            anchor="w",
        ).grid(
            row=row,
            column=1,
            padx=10,
            pady=8,
            sticky="ew",
        )

        row += 1

    # ------------------------------
    # Material Name
    # ------------------------------

        self._entry(
            frame,
            "Material",
            self.vars["material_name"],
            row,
        )

        row += 1
            # ------------------------------
    # Unit
    # ------------------------------

        ctk.CTkLabel(
            frame,
            text="Unit",
        ).grid(
            row=row,
            column=0,
            padx=10,
            pady=8,
            sticky="w",
        )

        self.unit_combo = ctk.CTkComboBox(
            frame,
            variable=self.vars["unit"],
            width=350,
            values=[
                "Nos",
                "Bag",
                "Kg",
                "Ton",
                "cft",
                "sft",
                "rft",
                "m",
                "m²",
                "m³",
                "L.S",
            ],
        )

        self.unit_combo.grid(
            row=row,
            column=1,
            padx=10,
            pady=8,
            sticky="ew",
        )

        row += 1

    # ------------------------------
    # Quantity
    # ------------------------------

        self._entry(
            frame,
            "Quantity",
            self.vars["quantity"],
            row,
        )

        row += 1

    # ------------------------------
    # Rate
    # ------------------------------

        self._entry(
            frame,
            "Rate",
            self.vars["rate"],
            row,
        )

        row += 1

    # ------------------------------
    # Amount
    # ------------------------------

        self._entry(
            frame,
            "Amount",
            self.vars["amount"],
            row,
            state="readonly",
        )

        row += 1

    # ------------------------------
    # Remarks
    # ------------------------------

        self._entry(
            frame,
            "Remarks",
            self.vars["remarks"],
            row,
        )
    def _entry(
        self,
        parent,
        text,
        variable,
        row,
        state="normal",
    ):

        ctk.CTkLabel(
            parent,
            text=text,
        ).grid(
            row=row,
            column=0,
            padx=10,
            pady=8,
            sticky="w",
       )

        entry = ctk.CTkEntry(
            parent,
            textvariable=variable,
            width=350,
            state=state,
        )

        entry.grid(
            row=row,
            column=1,
            padx=10,
            pady=8,
            sticky="ew",
        )

        return entry    
    def calculate_amount(self, *_):

        amount = MaterialFormHelpers.calculate_amount(
            self.vars["quantity"].get(),
            self.vars["rate"].get(),
        )

        self.vars["amount"].set(
            MaterialFormHelpers.format_amount(amount)
        )
    def validate(self):

        ok, message = MaterialFormValidation.validate_form(
            self.vars["material_name"].get(),
            self.vars["quantity"].get(),
            self.vars["rate"].get(),
       )

        if not ok:
            messagebox.showerror(
                "Validation",
                message,
           )
            return False

        return True
    def collect_data(self):

        project = CurrentProject.get()

        if project is None:
            raise ValueError("No project selected.")

        return Material(

            id=self.material.id if self.material else None,

            project_id=project.id,

            material_name=self.vars["material_name"].get().strip(),

            unit=self.vars["unit"].get().strip(),

            quantity=MaterialFormHelpers.to_float(
                self.vars["quantity"].get()
        ),

            rate=MaterialFormHelpers.to_float(
                self.vars["rate"].get()
        ),

            amount=MaterialFormHelpers.to_float(
                self.vars["amount"].get()
        ),

            remarks=self.vars["remarks"].get().strip(),
    )
    def load_data(
        self,
        material: Material,
   ):

        self.vars["material_name"].set(
            material.material_name
    )

        self.vars["unit"].set(
            material.unit
    )

        self.vars["quantity"].set(
            str(material.quantity)
    )

        self.vars["rate"].set(
            str(material.rate)
    )

        self.vars["amount"].set(
            str(material.amount)
    )

        self.vars["remarks"].set(
            material.remarks
        )
    def reset(self):

        self.vars["material_name"].set("")

        self.vars["unit"].set("Nos")

        self.vars["quantity"].set("0")

        self.vars["rate"].set("0")

        self.vars["amount"].set("0.00")

        self.vars["remarks"].set("")