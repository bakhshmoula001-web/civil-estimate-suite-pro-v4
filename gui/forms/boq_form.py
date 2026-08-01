from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox

from models.boq import BOQ


class BOQForm(ctk.CTkToplevel):
    """
    BOQ Entry Form
    """

    def __init__(self, parent, boq: BOQ | None = None):
        super().__init__(parent)

        self.result = None
        self.boq = boq

        self.title("BOQ Item")
        self.geometry("700x650")
        self.resizable(False, False)

        self.grab_set()

        self.project_id = ctk.IntVar(value=0)

        self.item_no = ctk.StringVar()
        self.description = ctk.StringVar()
        self.unit = ctk.StringVar(value="Nos")
        self.quantity = ctk.DoubleVar(value=0.0)
        self.rate = ctk.DoubleVar(value=0.0)
        self.amount = ctk.DoubleVar(value=0.0)
        self.remarks = ctk.StringVar()

        self._build_ui()

        if boq:
            self.load_boq(boq)

    # ---------------------------------------------------------

    def _build_ui(self):

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        row = 0

        self._entry(frame, "Project ID", self.project_id, row)
        row += 1

        self._entry(frame, "Item No", self.item_no, row)
        row += 1

        self._entry(frame, "Description", self.description, row)
        row += 1

        ctk.CTkLabel(frame, text="Unit").grid(
            row=row,
            column=0,
            sticky="w",
            padx=10,
            pady=8,
        )

        self.unit_combo = ctk.CTkComboBox(
            frame,
            variable=self.unit,
            values=[
                "Nos",
                "m",
                "m²",
                "m³",
                "kg",
                "Ton",
                "L.S",
            ],
            width=350,
        )

        self.unit_combo.grid(
            row=row,
            column=1,
            padx=10,
            pady=8,
            sticky="ew",
        )

        row += 1

        self._entry(frame, "Quantity", self.quantity, row)
        row += 1

        self._entry(frame, "Rate", self.rate, row)
        row += 1

        self._entry(
            frame,
            "Amount",
            self.amount,
            row,
            state="readonly",
        )
        row += 1

        self._entry(frame, "Remarks", self.remarks, row)
        row += 1

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.grid(
            row=row,
            column=0,
            columnspan=2,
            pady=20,
        )

        ctk.CTkButton(
            btn_frame,
            text="Save",
            command=self.save,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Save & New",
            command=self.save_and_new,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Reset",
            command=self.reset,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.cancel,
        ).pack(side="left", padx=5)

        self.quantity.trace_add("write", self.calculate_amount)
        self.rate.trace_add("write", self.calculate_amount)

    # ---------------------------------------------------------

    def _entry(self, parent, text, variable, row, state="normal"):

        ctk.CTkLabel(parent, text=text).grid(
            row=row,
            column=0,
            sticky="w",
            padx=10,
            pady=8,
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

    # ---------------------------------------------------------

    def calculate_amount(self, *_):

        try:

            amount = (
                float(self.quantity.get())
                * float(self.rate.get())
            )

            self.amount.set(round(amount, 2))

        except Exception:
            self.amount.set(0.0)

    # ---------------------------------------------------------

    def load_boq(self, boq: BOQ):

        self.project_id.set(boq.project_id)
        self.item_no.set(boq.item_no)
        self.description.set(boq.description)
        self.unit.set(boq.unit)
        self.quantity.set(boq.quantity)
        self.rate.set(boq.rate)
        self.amount.set(boq.amount)
        self.remarks.set(boq.remarks)

    # ---------------------------------------------------------

    def validate(self):

        if self.project_id.get() <= 0:
            messagebox.showerror(
                "Validation",
                "Project is required.",
            )
            return False

        if self.item_no.get().strip() == "":
            messagebox.showerror(
                "Validation",
                "Item No is required.",
            )
            return False

        if self.description.get().strip() == "":
            messagebox.showerror(
                "Validation",
                "Description is required.",
            )
            return False

        if self.quantity.get() <= 0:
            messagebox.showerror(
                "Validation",
                "Quantity must be greater than zero.",
            )
            return False

        return True

    # ---------------------------------------------------------

    def save(self):

        if not self.validate():
            return

        self.result = BOQ(
            id=self.boq.id if self.boq else None,
            project_id=self.project_id.get(),
            item_no=self.item_no.get().strip(),
            description=self.description.get().strip(),
            unit=self.unit.get(),
            quantity=self.quantity.get(),
            rate=self.rate.get(),
            amount=self.amount.get(),
            remarks=self.remarks.get().strip(),
        )

        self.destroy()

    # ---------------------------------------------------------

    def save_and_new(self):

        self.save()

    # ---------------------------------------------------------

    def reset(self):

        self.item_no.set("")
        self.description.set("")
        self.unit.set("Nos")
        self.quantity.set(0.0)
        self.rate.set(0.0)
        self.amount.set(0.0)
        self.remarks.set("")

    # ---------------------------------------------------------

    def cancel(self):

        self.result = None
        self.destroy()