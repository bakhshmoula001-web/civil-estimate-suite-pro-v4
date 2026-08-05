
from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox

from models import boq
from models.boq import BOQ
from core.current_project import CurrentProject
from gui.forms.boq_form_helpers import BOQFormHelpers
from gui.forms.boq_form_validation import BOQFormValidation
from gui.forms.base_form import BaseForm
class BOQForm(BaseForm):
    """
    BOQ Entry Dialog

    Features
    --------
    • Add BOQ Item
    • Edit BOQ Item
    • Auto Amount Calculation
    • Current Project Integration
    • Validation
    """

    # =====================================================
    # Constructor
    # =====================================================

    def __init__(self, parent, boq: BOQ | None = None):
         super().__init__(
         parent,
         title="BOQ Item",
         width=720,
         height=620,
    )

         self.boq = boq
         self.project = CurrentProject.get()

         self.vars = {
         "item_no": ctk.StringVar(),
         "description": ctk.StringVar(),
         "unit": ctk.StringVar(value="Nos"),
         "quantity": ctk.StringVar(value="0"),
         "rate": ctk.StringVar(value="0"),
         "amount": ctk.StringVar(value="0.00"),
         "remarks": ctk.StringVar(),
}
         print(type(self.vars))
         print(self.vars)
         self._build_form()

         self.vars["quantity"].trace_add(
             "write",
            self.calculate_amount,
)

         self.vars["rate"].trace_add(
             "write",
             self.calculate_amount,
)

         if boq is not None:
          self.load_data(boq)

    def _build_form(self):
        
    # ---------------------------------------------
    # Main Container
    # ---------------------------------------------

        frame = self.content_frame

        self.content_frame.grid_columnconfigure(
        1,
         weight=1,
    )

        row = 0

    # ---------------------------------------------
    # Current Project
    # ---------------------------------------------

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

    # ---------------------------------------------
    # Item No
    # ---------------------------------------------

        self._entry(
          frame,
          "Item No",
         self.vars["item_no"],
          row,
    )

        row += 1

    # ---------------------------------------------
    # Description
    # ---------------------------------------------

        self._entry(
           frame,
           "Description",
           self.vars["description"],
           row,
    )

        row += 1

    # ---------------------------------------------
    # Unit
    # ---------------------------------------------

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

    # ---------------------------------------------
    # Quantity
    # ---------------------------------------------

        self._entry(
            frame,
            "Quantity",
            self.vars["quantity"],
            row,
        )

        row += 1

    # ---------------------------------------------
    # Rate
    # ---------------------------------------------

        self._entry(
            frame,
            "Rate",
            self.vars["rate"],
            row,
        )

        row += 1

    # ---------------------------------------------
    # Amount
    # ---------------------------------------------

        self._entry(
            frame,
            "Amount",
            self.vars["amount"],
            row,
            state="readonly",
        )

        row += 1

    # ---------------------------------------------
    # Remarks
    # ---------------------------------------------

        self._entry(
            frame,
            "Remarks",
            self.vars["remarks"],
            row,
        )
       #--------------------------------
# Common Entry Widget
# ---------------------------------------------------------

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

        amount = BOQFormHelpers.calculate_amount(
        self.vars["quantity"].get(),
        self.vars["rate"].get(),
    )

        self.vars["amount"].set(
        BOQFormHelpers.format_amount(amount)
    )
        
    def validate(self):

        ok, message = BOQFormValidation.validate_form(
          self.vars["item_no"].get(),
          self.vars["description"].get(),
          self.vars["quantity"].get(),
          self.vars["rate"].get(),
    )

        if not ok:
          messagebox.showerror("Validation", message)
          return False

        return True
    def collect_data(self):

        project = CurrentProject.get()

        if project is None:
            raise ValueError(
                "No project selected."
        )

        return BOQ(

            id=self.boq.id if self.boq else None,

            project_id=project.id,

            item_no=self.vars["item_no"].get().strip(),

            description=self.vars["description"].get().strip(),

            unit=self.vars["unit"].get().strip(),

            quantity=float(
               self.vars["quantity"].get() or 0
        ),

            rate=float(
               self.vars["rate"].get() or 0
        ),

            amount = BOQFormHelpers.to_float(
              self.vars["amount"].get()
        ),

            remarks=self.vars["remarks"].get().strip(),
    )
    def load_data(
        self,
        boq: BOQ,
    ):

        self.vars["item_no"].set(
            boq.item_no
    )

        self.vars["description"].set(
           boq.description
    )

        self.vars["unit"].set(
           boq.unit
    )

        self.vars["quantity"].set(
            str(boq.quantity)
    )

        self.vars["rate"].set(
           str(boq.rate)
    )

        self.vars["amount"].set(
           str(boq.amount)
    )

        self.vars["remarks"].set(
           boq.remarks
    )
    def reset(self):

        self.vars["item_no"].set("")

        self.vars["description"].set("")

        self.vars["unit"].set("Nos")

        self.vars["quantity"].set("0")

        self.vars["rate"].set("0")

        self.vars["amount"].set("0.00")

        self.vars["remarks"].set("")
    def save_and_new(self):

        self.save()

        if self.result is not None:

          self.result = None

          self.reset()