"""
Civil Estimate Suite Pro v4.0
Plaster Calculator Form
"""
from __future__ import annotations
from config.rate_defaults import apply_rate_defaults

import customtkinter as ctk
from tkinter import messagebox

from calculations.calculator_factory import CalculatorFactory
from calculations.calculation_result import CalculationResult
from core.current_project import CurrentProject
from gui.forms.base_form import BaseForm
from models.boq import BOQ
from services.plaster_estimate_service import PlasterEstimateService


class PlasterCalculatorForm(BaseForm):
    """Plaster quantity + material + labour + BOQ workflow."""

    def __init__(self, parent):
        super().__init__(
            parent,
            title="Plaster Calculator",
            width=1120,
            height=760,
        )

        self.result: CalculationResult | None = None
        self.analysis: dict | None = None
        self._last_unit = "m²"

        self.vars = {
            "area_unit": ctk.StringVar(value="m²"),
            "length": ctk.StringVar(value=""),
            "height": ctk.StringVar(value=""),
            "thickness_mm": ctk.StringVar(value="12"),
            "surfaces": ctk.StringVar(value="1"),
            "mortar_ratio": ctk.StringVar(value="1:4"),
            "cement_rate": ctk.StringVar(value="0"),
            "sand_rate": ctk.StringVar(value="0"),
            "skilled_productivity": ctk.StringVar(value="10"),
            "skilled_rate": ctk.StringVar(value="2500"),
            "unskilled_productivity": ctk.StringVar(value="15"),
            "unskilled_rate": ctk.StringVar(value="1250"),
        }

        apply_rate_defaults(self.vars)
        self._build_action_bar()
        self._build_form()

    def _build_action_bar(self):
        bar = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent",
        )
        bar.pack(fill="x", padx=5, pady=(0, 8))

        ctk.CTkButton(
            bar,
            text="Calculate",
            width=140,
            command=self.calculate,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            bar,
            text="Reset",
            width=120,
            command=self.reset_form,
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            bar,
            text="Generate BOQ",
            width=160,
            command=self.generate_boq,
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            bar,
            text="Generate Material",
            width=170,
            command=self.generate_material,
        ).pack(side="left", padx=8)

        self.status = ctk.CTkLabel(
            bar,
            text="Ready",
            anchor="w",
        )
        self.status.pack(side="left", padx=15)

    def _build_form(self):
        workspace = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent",
        )
        workspace.pack(fill="both", expand=True)

        workspace.grid_columnconfigure(0, weight=0, minsize=475)
        workspace.grid_columnconfigure(1, weight=1)
        workspace.grid_rowconfigure(0, weight=1)

        left = ctk.CTkScrollableFrame(workspace, corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.grid_columnconfigure(0, minsize=225)
        left.grid_columnconfigure(1, weight=1)

        row = 0
        self._section(left, "1. Plaster Quantity", row)
        row += 1

        self._label(left, "Area Unit", row)
        ctk.CTkComboBox(
            left,
            variable=self.vars["area_unit"],
            values=["m²", "Sft"],
            width=230,
            command=self._on_unit_change,
        ).grid(row=row, column=1, padx=10, pady=7, sticky="ew")
        row += 1

        self.length_label = self._label(left, "Length (m)", row)
        self._entry(left, "length", row)
        row += 1

        self.height_label = self._label(left, "Height (m)", row)
        self._entry(left, "height", row)
        row += 1

        self._label(left, "Plaster Thickness (mm)", row)
        self._entry(left, "thickness_mm", row)
        row += 1

        self._label(left, "Surfaces", row)
        ctk.CTkComboBox(
            left,
            variable=self.vars["surfaces"],
            values=["1", "2"],
            width=230,
        ).grid(row=row, column=1, padx=10, pady=7, sticky="ew")
        row += 1

        self._label(left, "Mortar Ratio", row)
        ctk.CTkComboBox(
            left,
            variable=self.vars["mortar_ratio"],
            values=["1:4", "1:5", "1:6"],
            width=230,
        ).grid(row=row, column=1, padx=10, pady=7, sticky="ew")
        row += 1

        self._section(left, "2. Material Rates", row)
        row += 1

        self._label(left, "Cement (PKR / Bag)", row)
        self._entry(left, "cement_rate", row)
        row += 1

        self.sand_rate_label = self._label(
            left,
            "Sand (PKR / m³)",
            row,
        )
        self._entry(left, "sand_rate", row)
        row += 1

        self._section(left, "3. Labour Norms & Rates", row)
        row += 1

        self.skilled_prod_label = self._label(
            left,
            "Skilled productivity (m² / day)",
            row,
        )
        self._entry(left, "skilled_productivity", row)
        row += 1

        self._label(left, "Skilled labour (PKR / day)", row)
        self._entry(left, "skilled_rate", row)
        row += 1

        self.unskilled_prod_label = self._label(
            left,
            "Unskilled productivity (m² / day)",
            row,
        )
        self._entry(left, "unskilled_productivity", row)
        row += 1

        self._label(left, "Unskilled labour (PKR / day)", row)
        self._entry(left, "unskilled_rate", row)

        self.result_frame = ctk.CTkScrollableFrame(
            workspace,
            corner_radius=10,
        )
        self.result_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(8, 0),
        )
        self.result_frame.grid_columnconfigure(0, minsize=190)
        self.result_frame.grid_columnconfigure(1, weight=1)

        self._show_ready()

    def _label(self, parent, text, row):
        label = ctk.CTkLabel(parent, text=text, anchor="w")
        label.grid(
            row=row,
            column=0,
            padx=10,
            pady=7,
            sticky="w",
        )
        return label

    def _entry(self, parent, key, row):
        entry = ctk.CTkEntry(
            parent,
            textvariable=self.vars[key],
            width=230,
        )
        entry.grid(
            row=row,
            column=1,
            padx=10,
            pady=7,
            sticky="ew",
        )
        return entry

    def _section(self, parent, text, row):
        ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(
            row=row,
            column=0,
            columnspan=2,
            padx=10,
            pady=(15, 8),
            sticky="w",
        )

    def _on_unit_change(self, _value=None):
        unit = self.vars["area_unit"].get()
        previous = self._last_unit

        if unit != previous:
            try:
                dimension_factor = (
                    3.280839895
                    if previous == "m²" and unit == "Sft"
                    else 0.3048
                )
                for key in ("length", "height"):
                    text = self.vars[key].get().strip()
                    if text:
                        self.vars[key].set(
                            f"{float(text) * dimension_factor:.6f}".rstrip("0").rstrip(".")
                        )

                # Area productivity m2/day <-> Sft/day.
                for key in ("skilled_productivity", "unskilled_productivity"):
                    text = self.vars[key].get().strip()
                    if text:
                        factor = (
                            10.7639104167
                            if unit == "Sft"
                            else 0.09290304
                        )
                        self.vars[key].set(
                            f"{float(text) * factor:.4f}".rstrip("0").rstrip(".")
                        )
            except ValueError:
                pass

        self._last_unit = unit
        dimension = "m" if unit == "m²" else "ft"
        self.length_label.configure(text=f"Length ({dimension})")
        self.height_label.configure(text=f"Height ({dimension})")
        self.sand_rate_label.configure(text=f"Sand (PKR / {'m³' if unit == 'm²' else 'Cft'})")
        self.skilled_prod_label.configure(
            text=f"Skilled productivity ({unit} / day)"
        )
        self.unskilled_prod_label.configure(
            text=f"Unskilled productivity ({unit} / day)"
        )

    def _number(self, key, label, positive=False):
        try:
            value = float(self.vars[key].get())
        except ValueError as exc:
            raise ValueError(f"{label} must be a valid number.") from exc
        if positive and value <= 0:
            raise ValueError(f"{label} must be greater than zero.")
        if not positive and value < 0:
            raise ValueError(f"{label} cannot be negative.")
        return value

    def calculate(self):
        try:
            self.result = CalculatorFactory.create(
                "Plaster",
                length=self._number("length", "Length", True),
                height=self._number("height", "Height", True),
                thickness_mm=self._number(
                    "thickness_mm",
                    "Plaster thickness",
                    True,
                ),
                mortar_ratio=self.vars["mortar_ratio"].get(),
                surfaces=int(self.vars["surfaces"].get()),
                area_unit=self.vars["area_unit"].get(),
            ).calculate()

            self.analysis = self._build_analysis()
            self.show_result()
            self.status.configure(
                text="Calculated — ready to Generate BOQ"
            )
        except Exception as ex:
            messagebox.showerror(
                "Plaster Calculation Error",
                str(ex),
                parent=self,
            )

    def _build_analysis(self):
        quantity = float(self.result.quantity)

        skilled_productivity = self._number(
            "skilled_productivity",
            "Skilled productivity",
            True,
        )
        unskilled_productivity = self._number(
            "unskilled_productivity",
            "Unskilled productivity",
            True,
        )

        return PlasterEstimateService.build_analysis(
            result=self.result,
            material_rates={
                "cement_bag": self._number(
                    "cement_rate",
                    "Cement rate",
                ),
                "sand": self._number(
                    "sand_rate",
                    "Sand rate",
                ),
            },
            skilled_days=quantity / skilled_productivity,
            skilled_rate=self._number(
                "skilled_rate",
                "Skilled labour rate",
            ),
            unskilled_days=quantity / unskilled_productivity,
            unskilled_rate=self._number(
                "unskilled_rate",
                "Unskilled labour rate",
            ),
        )

    def _show_ready(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        self._section(
            self.result_frame,
            "Calculation Result",
            0,
        )
        ctk.CTkLabel(
            self.result_frame,
            text=(
                "Enter plaster dimensions, thickness, mortar ratio and "
                "labour/material rates, then press Calculate."
            ),
            justify="left",
            anchor="w",
            wraplength=520,
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            padx=14,
            pady=12,
            sticky="ew",
        )

    def show_result(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        r = self.result
        a = self.analysis
        row = 0

        self._section(
            self.result_frame,
            "Quantity Result",
            row,
        )
        row += 1

        rows = [
            (
                "Dimensions",
                (
                    f"L={r.get_value('length', 0):,.3f} × "
                    f"H={r.get_value('height', 0):,.3f} "
                    f"{r.get_value('dimension_unit', 'm')}"
                ),
            ),
            (
                "Surfaces",
                f"{r.get_value('surfaces', 1)} side(s)",
            ),
            (
                "Thickness",
                f"{r.get_value('thickness_mm', 0):,.1f} mm",
            ),
            (
                "Mortar Ratio",
                str(r.get_value('mortar_ratio', "")),
            ),
            (
                "Plaster Area",
                f"{r.quantity:,.3f} {r.unit}",
            ),
            (
                "Wet Mortar",
                f"{r.get_value('wet_mortar_m3', 0):,.3f} m³",
            ),
            (
                "Dry Mortar",
                f"{r.get_value('dry_mortar_m3', 0):,.3f} m³",
            ),
            (
                "Cement",
                f"{r.cement_bags:,.3f} Bags",
            ),
            (
                "Sand",
                f"{r.get_value('sand_quantity', 0):,.3f} "
                f"{'m³' if r.unit == 'm²' else 'Cft'}",
            ),
        ]
        row = self._rows(rows, row)

        self._section(
            self.result_frame,
            "Material Cost Build-up",
            row,
        )
        row += 1
        row = self._rows(
            [
                (
                    x["name"],
                    (
                        f"{x['quantity']:,.3f} {x['unit']} × "
                        f"PKR {x['rate']:,.2f} = "
                        f"PKR {x['amount']:,.2f}"
                    ),
                )
                for x in a["materials"]
            ],
            row,
        )
        row = self._rows(
            [(
                "Material Total",
                f"PKR {a['material_total']:,.2f}",
            )],
            row,
            bold=True,
        )

        self._section(
            self.result_frame,
            "Labour Cost Build-up",
            row,
        )
        row += 1
        row = self._rows(
            [
                (
                    x["name"],
                    (
                        f"{x['quantity']:,.2f} {x['unit']} × "
                        f"PKR {x['rate']:,.2f} = "
                        f"PKR {x['amount']:,.2f}"
                    ),
                )
                for x in a["labour"]
            ],
            row,
        )
        row = self._rows(
            [(
                "Labour Total",
                f"PKR {a['labour_total']:,.2f}",
            )],
            row,
            bold=True,
        )

        self._section(
            self.result_frame,
            "Final Cost",
            row,
        )
        row += 1
        self._rows(
            [
                (
                    "Total Cost",
                    f"PKR {a['total_cost']:,.2f}",
                ),
                (
                    "Unit Rate",
                    f"PKR {a['unit_rate']:,.2f} / {r.unit}",
                ),
            ],
            row,
            bold=True,
        )

    def _rows(self, rows, start_row, bold=False):
        row = start_row
        font = ctk.CTkFont(weight="bold") if bold else None
        for label, value in rows:
            ctk.CTkLabel(
                self.result_frame,
                text=label,
                anchor="w",
                font=font,
            ).grid(
                row=row,
                column=0,
                padx=(14, 10),
                pady=5,
                sticky="w",
            )
            ctk.CTkLabel(
                self.result_frame,
                text=value,
                anchor="w",
                justify="left",
                font=font,
            ).grid(
                row=row,
                column=1,
                padx=(10, 14),
                pady=5,
                sticky="ew",
            )
            row += 1
        return row

    def generate_boq(self):
        if self.result is None:
            messagebox.showwarning(
                "Plaster → BOQ",
                "Please calculate plaster first.",
                parent=self,
            )
            return

        try:
            self.analysis = self._build_analysis()
            project = CurrentProject.get()
            if project is None or getattr(project, "id", None) is None:
                raise ValueError(
                    "Please select/open a project before generating BOQ."
                )

            context = self.application_context
            if context is None:
                raise ValueError(
                    "Application context is not available."
                )

            controller = context.boq_controller
            existing = controller.get_by_project(project.id) or []
            highest = 0
            for item in existing:
                value = str(
                    getattr(item, "item_no", "")
                ).upper()
                if value.startswith("PLASTER-"):
                    try:
                        highest = max(
                            highest,
                            int(value.split("-", 1)[1]),
                        )
                    except (ValueError, IndexError):
                        pass

            item_no = f"PLASTER-{highest + 1:02d}"
            d = self.analysis["dimensions"]

            remarks = (
                "Detailed Plaster analysis | "
                f"L={d['length']:.3f} {d['dimension_unit']}, "
                f"H={d['height']:.3f} {d['dimension_unit']} | "
                f"Thickness={self.analysis['thickness_mm']:.1f} mm | "
                f"Surfaces={self.analysis['surfaces']} | "
                f"Mix={self.analysis['mortar_ratio']}"
            )

            boq = BOQ(
                project_id=project.id,
                item_no=item_no,
                description=(
                    f"Plaster ({self.analysis['mortar_ratio']})"
                ),
                unit=self.analysis["unit"],
                quantity=self.analysis["quantity"],
                rate=self.analysis["unit_rate"],
                amount=self.analysis["total_cost"],
                remarks=remarks,
            )

            boq_id = controller.create(boq)

            context.estimate_analysis_service.save(
                project_id=project.id,
                boq_id=int(boq_id),
                calculator_type="Plaster",
                analysis=self.analysis,
            )

            self.status.configure(
                text=f"BOQ {item_no} added successfully"
            )

            messagebox.showinfo(
                "Plaster → BOQ",
                (
                    f"BOQ item {item_no} created successfully.\n\n"
                    f"Quantity: {self.analysis['quantity']:,.3f} {self.analysis['unit']}\n"
                    f"Cement: {self.analysis['materials'][0]['quantity']:,.3f} Bags\n"
                    f"Sand: {self.analysis['materials'][1]['quantity']:,.3f} "
                    f"{self.analysis['materials'][1]['unit']}\n"
                    f"Skilled Labour: {self.analysis['labour'][0]['quantity']:,.2f} day\n"
                    f"Unskilled Labour: {self.analysis['labour'][1]['quantity']:,.2f} day"
                ),
                parent=self,
            )
        except Exception as ex:
            messagebox.showerror(
                "Plaster → BOQ Error",
                str(ex),
                parent=self,
            )

    def generate_material(self):
        if self.result is None:
            messagebox.showwarning("PLASTER Material", "Please calculate plaster first.", parent=self)
            return
        try:
            project = CurrentProject.get()
            if project is None or getattr(project, "id", None) is None:
                raise ValueError("Please select/open a project before generating material.")
            context = self.application_context
            controller = getattr(context, "material_controller", None) if context else None
            if controller is None:
                raise ValueError("Material Controller is not available.")

            # The calculator already builds a complete engineer-facing
            # analysis immediately after Calculate(). Use that analysis
            # as the single source for Material generation. Older code
            # tried to rebuild it through a generic "CALC" result path,
            # which cannot know the calculator-specific material schedule
            # for steel/slab/column/beam/footing/staircase.
            analysis = getattr(self, "analysis", None)

            # Compatibility for any older form that did not store
            # self.analysis but exposes one of the legacy builders.
            if not (isinstance(analysis, dict) and analysis.get("materials")):
                for method_name in (
                    "_analysis",
                    "_build_analysis",
                    "_try_build_analysis",
                ):
                    method = getattr(self, method_name, None)
                    if callable(method):
                        try:
                            candidate = method()
                        except TypeError:
                            candidate = None
                        if isinstance(candidate, dict):
                            analysis = candidate
                            if candidate.get("materials"):
                                break

            if isinstance(analysis, dict) and analysis.get("materials"):
                records = controller.generate_from_analysis(
                    analysis,
                    project.id,
                )
            else:
                raise ValueError(
                    "The calculator has no material analysis. "
                    "Please press Calculate first."
                )

            lines = []
            for record in records:
                lines.append(
                    f"• {record.material_name}: {float(record.quantity):,.3f} {record.unit}"
                )
            messagebox.showinfo(
                "PLASTER Material",
                "Material quantities added to the project material schedule.\n\n"
                + ("\n".join(lines) if lines else "No material records generated.")
                + "\n\nUse Materials / BOQ → Material Report for the consolidated report.",
                parent=self,
            )
        except Exception as ex:
            messagebox.showerror("PLASTER Material Error", str(ex), parent=self)
    def reset_form(self):
        defaults = {
            "area_unit": "m²",
            "length": "",
            "height": "",
            "thickness_mm": "12",
            "surfaces": "1",
            "mortar_ratio": "1:4",
            "cement_rate": "0",
            "sand_rate": "0",
            "skilled_productivity": "10",
            "skilled_rate": "2500",
            "unskilled_productivity": "15",
            "unskilled_rate": "1250",
        }
        for key, value in defaults.items():
            self.vars[key].set(value)

        self._last_unit = "m²"
        self._on_unit_change()
        self.result = None
        self.analysis = None
        self.status.configure(text="Ready")
        self._show_ready()

    def has_result(self):
        return self.result is not None
