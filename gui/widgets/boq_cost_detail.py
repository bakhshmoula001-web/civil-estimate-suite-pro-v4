from __future__ import annotations

import customtkinter as ctk


class BOQCostDetail(ctk.CTkFrame):
    """
    Engineer-friendly detailed cost build-up panel.

    Shows:
        BOQ quantity
        material-wise quantity/rate/amount
        skilled labour quantity/rate/amount
        unskilled labour quantity/rate/amount
        material cost
        labour cost
        total cost
        calculated unit rate

    The panel never changes the original calculator quantities.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.title = ctk.CTkLabel(
            self,
            text="Select a BOQ item to view detailed cost build-up.",
            anchor="w",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.title.grid(
            row=0, column=0, columnspan=2,
            sticky="ew", padx=12, pady=(8, 3)
        )

        self.summary = ctk.CTkLabel(
            self, text="", anchor="w", justify="left"
        )
        self.summary.grid(
            row=1, column=0, columnspan=2,
            sticky="ew", padx=12, pady=(0, 6)
        )

        self.material_frame = ctk.CTkScrollableFrame(
            self, label_text="Material Cost Build-up"
        )
        self.material_frame.grid(
            row=2, column=0, sticky="nsew",
            padx=(10, 5), pady=(0, 8)
        )
        self.material_frame.grid_columnconfigure(1, weight=1)

        self.labour_frame = ctk.CTkScrollableFrame(
            self, label_text="Labour Cost Build-up"
        )
        self.labour_frame.grid(
            row=2, column=1, sticky="nsew",
            padx=(5, 10), pady=(0, 8)
        )
        self.labour_frame.grid_columnconfigure(1, weight=1)

        self.total_frame = ctk.CTkFrame(self)
        self.total_frame.grid(
            row=3, column=0, columnspan=2,
            sticky="ew", padx=10, pady=(0, 10)
        )
        for col in range(4):
            self.total_frame.grid_columnconfigure(col, weight=1)

        self.clear()

    @staticmethod
    def _money(value):
        return f"PKR {float(value or 0):,.2f}"

    @staticmethod
    def _qty(value):
        return f"{float(value or 0):,.3f}"

    @staticmethod
    def _num(value):
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    def _clear(self):
        for frame in (
            self.material_frame,
            self.labour_frame,
            self.total_frame,
        ):
            for child in frame.winfo_children():
                child.destroy()

    def clear(self):
        self._clear()
        self.title.configure(
            text="Select a BOQ item to view detailed cost build-up."
        )
        self.summary.configure(text="")

    def _row(self, frame, row, name, detail, bold=False):
        font = ctk.CTkFont(
            size=11,
            weight="bold" if bold else "normal",
        )
        ctk.CTkLabel(
            frame,
            text=name,
            anchor="w",
            font=font,
        ).grid(
            row=row, column=0,
            sticky="w", padx=8, pady=4
        )
        ctk.CTkLabel(
            frame,
            text=detail,
            anchor="e",
            justify="right",
            font=font,
        ).grid(
            row=row, column=1,
            sticky="e", padx=8, pady=4
        )

    def _labour_type(self, name):
        text = str(name or "").lower()
        if "unskilled" in text:
            return "unskilled"
        if "skilled" in text:
            return "skilled"
        return "other"

    def show_item(self, item, analysis):
        self._clear()

        if not isinstance(analysis, dict):
            self.clear()
            self.title.configure(
                text=(
                    f"{getattr(item, 'item_no', '')} — "
                    "No detailed analysis available."
                )
            )
            return

        item_no = getattr(item, "item_no", "")
        description = getattr(item, "description", "")
        quantity = self._num(getattr(item, "quantity", 0))
        unit = getattr(item, "unit", "")

        self.title.configure(
            text=f"{item_no} — {description}"
        )

        calculator = analysis.get(
            "_calculator_type",
            analysis.get("calculator_type", "—"),
        )

        self.summary.configure(
            text=(
                f"Work Quantity: {self._qty(quantity)} {unit}   |   "
                f"Calculator: {calculator}"
            )
        )

        materials = (
            analysis.get("materials")
            or analysis.get("MATERIALS")
            or []
        )
        labour = (
            analysis.get("labour")
            or analysis.get("LABOUR")
            or []
        )

        # -------------------------------------------------
        # Materials
        # -------------------------------------------------

        row = 0
        for material in materials:
            name = (
                material.get("name")
                or material.get("material_name")
                or "Material"
            )
            qty = self._num(
                material.get("quantity", material.get("QTY"))
            )
            unit_name = material.get("unit", "")
            rate = self._num(material.get("rate", material.get("RATE")))
            amount = self._num(
                material.get(
                    "amount",
                    material.get("cost", qty * rate),
                )
            )

            self._row(
                self.material_frame,
                row,
                str(name),
                (
                    f"{self._qty(qty)} {unit_name} × "
                    f"{self._money(rate)} = {self._money(amount)}"
                ),
            )
            row += 1

        material_total = self._num(
            analysis.get(
                "material_cost",
                analysis.get("material_total", 0),
            )
        )

        self._row(
            self.material_frame,
            row,
            "Material Cost",
            self._money(material_total),
            bold=True,
        )

        # -------------------------------------------------
        # Labour
        # -------------------------------------------------

        row = 0
        skilled_cost = 0.0
        unskilled_cost = 0.0
        other_cost = 0.0

        for labour_item in labour:
            name = (
                labour_item.get("name")
                or labour_item.get("labour")
                or "Labour"
            )
            qty = self._num(
                labour_item.get(
                    "quantity",
                    labour_item.get("days", 0),
                )
            )
            unit_name = labour_item.get("unit", "day")
            rate = self._num(labour_item.get("rate"))
            amount = self._num(
                labour_item.get(
                    "amount",
                    qty * rate,
                )
            )

            labour_type = self._labour_type(name)
            if labour_type == "skilled":
                skilled_cost += amount
            elif labour_type == "unskilled":
                unskilled_cost += amount
            else:
                other_cost += amount

            self._row(
                self.labour_frame,
                row,
                str(name),
                (
                    f"{self._qty(qty)} {unit_name} × "
                    f"{self._money(rate)} = {self._money(amount)}"
                ),
            )
            row += 1

        # Prefer the centralized cost-build-up fields when present.
        skilled_cost = self._num(
            analysis.get("skilled_labour_cost", skilled_cost)
        )
        unskilled_cost = self._num(
            analysis.get("unskilled_labour_cost", unskilled_cost)
        )
        labour_cost = self._num(
            analysis.get(
                "labour_cost",
                analysis.get(
                    "labour_total",
                    skilled_cost + unskilled_cost + other_cost,
                ),
            )
        )

        self._row(
            self.labour_frame,
            row,
            "Skilled Labour Cost",
            self._money(skilled_cost),
            bold=True,
        )
        row += 1

        self._row(
            self.labour_frame,
            row,
            "Unskilled Labour Cost",
            self._money(unskilled_cost),
            bold=True,
        )
        row += 1

        if other_cost:
            self._row(
                self.labour_frame,
                row,
                "Other Labour Cost",
                self._money(other_cost),
                bold=True,
            )

        # -------------------------------------------------
        # Final Cost Summary
        # -------------------------------------------------

        total_cost = self._num(
            analysis.get(
                "total_cost",
                material_total + labour_cost,
            )
        )

        work_quantity = quantity or self._num(
            analysis.get("quantity", 0)
        )
        unit_rate = self._num(
            analysis.get(
                "unit_rate",
                total_cost / work_quantity
                if work_quantity > 0 else 0,
            )
        )

        labels = [
            ("Material Cost", self._money(material_total)),
            ("Labour Cost", self._money(labour_cost)),
            ("Total Cost", self._money(total_cost)),
            (
                f"Unit Rate / {unit or 'Unit'}",
                self._money(unit_rate),
            ),
        ]

        for col, (label, value) in enumerate(labels):
            box = ctk.CTkFrame(self.total_frame)
            box.grid(
                row=0, column=col,
                sticky="ew", padx=5, pady=7
            )
            ctk.CTkLabel(
                box,
                text=label,
                font=ctk.CTkFont(size=11, weight="bold"),
            ).pack(pady=(7, 1))
            ctk.CTkLabel(
                box,
                text=value,
                font=ctk.CTkFont(size=13, weight="bold"),
            ).pack(pady=(0, 7))


__all__ = ["BOQCostDetail"]
