"""
Civil Estimate Suite Pro v4.0
Engineer-friendly Steel / Rebar Calculator Form
"""
from __future__ import annotations
from config.rate_defaults import apply_rate_defaults

import customtkinter as ctk
from tkinter import messagebox

from calculations.steel_calculator import SteelCalculator
from core.current_project import CurrentProject
from gui.forms.base_form import BaseForm
from models.boq import BOQ
from services.steel_estimate_service import SteelEstimateService


FT_PER_M = 3.280839895013123
M_PER_FT = 0.3048
CFT_PER_M3 = 35.31466672148859
M3_PER_CFT = 0.028316846592

class SteelCalculatorForm(BaseForm):
    def __init__(self, parent):
        super().__init__(
            parent,
            title="Steel / Rebar Calculator",
            width=1120,
            height=760,
        )
        self.result = None
        self.analysis = None
        self._build()

    def _build(self):
        bar = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent",
        )
        bar.pack(fill="x", padx=5, pady=(0, 8))

        for text, command, width in [
            ("Calculate", self.calculate, 140),
            ("Reset", self.reset_form, 120),
            ("Generate BOQ", self.generate_boq, 160),
            ("Generate Material", self.generate_material, 175),
        ]:
            ctk.CTkButton(
                bar,
                text=text,
                width=width,
                command=command,
            ).pack(side="left", padx=6)

        self.status = ctk.CTkLabel(
            bar,
            text="Ready",
            anchor="w",
        )
        self.status.pack(side="left", padx=15)

        workspace = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent",
        )
        workspace.pack(fill="both", expand=True)

        workspace.grid_columnconfigure(
            0, weight=0, minsize=480
        )
        workspace.grid_columnconfigure(
            1, weight=1
        )
        workspace.grid_rowconfigure(0, weight=1)

        left = ctk.CTkScrollableFrame(
            workspace,
            corner_radius=10,
        )
        left.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8),
        )
        left.grid_columnconfigure(0, minsize=240)
        left.grid_columnconfigure(1, weight=1)

        self.vars = {
            "diameter": ctk.StringVar(value="12"),
            "mode": ctk.StringVar(value="Number of Bars"),
            "number": ctk.StringVar(value=""),
            "bar_length": ctk.StringVar(value=""),
            "spacing": ctk.StringVar(value=""),
            "distribution_length": ctk.StringVar(value=""),
            "lap_length": ctk.StringVar(value="0"),
            "laps": ctk.StringVar(value="0"),
            "cutting": ctk.StringVar(value="2"),
            "binding": ctk.StringVar(value="2"),
            "length_unit": ctk.StringVar(value="m"),
            "steel_rate": ctk.StringVar(value="0"),
        }
        apply_rate_defaults(self.vars)

        row = 0
        self._section(left, "1. Bar Details", row)
        row += 1

        self._label(left, "Bar Diameter (mm)", row)
        ctk.CTkComboBox(
            left,
            variable=self.vars["diameter"],
            values=[
                "8", "10", "12", "16",
                "20", "25", "32", "40",
            ],
        ).grid(
            row=row, column=1, padx=10, pady=7,
            sticky="ew",
        )
        row += 1

        self._label(left, "Calculation Method", row)
        ctk.CTkComboBox(
            left,
            variable=self.vars["mode"],
            values=["Number of Bars", "Spacing"],
            command=self._mode_changed,
        ).grid(
            row=row, column=1, padx=10, pady=7,
            sticky="ew",
        )
        row += 1

        self.number_label = self._label(
            left, "Number of Bars", row
        )
        self._entry(left, "number", row)
        row += 1

        self.bar_length_label = self._label(
            left, "Bar Length (m)", row
        )
        self._entry(left, "bar_length", row)
        row += 1

        self.spacing_label = self._label(
            left, "Spacing (mm)", row
        )
        self._entry(left, "spacing", row)
        row += 1

        self.distribution_label = self._label(
            left, "Distribution Length (m)", row
        )
        self._entry(left, "distribution_length", row)
        row += 1

        self._label(left, "Length Unit", row)
        ctk.CTkComboBox(
            left,
            variable=self.vars["length_unit"],
            values=["m", "ft"],
            command=self._unit_changed,
        ).grid(
            row=row, column=1, padx=10, pady=7,
            sticky="ew",
        )
        row += 1

        self._section(
            left, "2. Lapping & Allowances", row
        )
        row += 1

        self._label(left, "Lap Length / Bar (m)", row)
        self._entry(left, "lap_length", row)
        row += 1

        self._label(left, "Laps / Bar", row)
        self._entry(left, "laps", row)
        row += 1

        self._label(left, "Cutting Allowance (%)", row)
        self._entry(left, "cutting", row)
        row += 1

        self._label(left, "Binding Wire (% of Steel)", row)
        self._entry(left, "binding", row)
        row += 1

        self._section(left, "3. Cost", row)
        row += 1

        self._label(left, "Steel Rate (PKR / kg)", row)
        self._entry(left, "steel_rate", row)

        self.result_frame = ctk.CTkScrollableFrame(
            workspace,
            corner_radius=10,
        )
        self.result_frame.grid(
            row=0, column=1, sticky="nsew",
            padx=(8, 0),
        )
        self.result_frame.grid_columnconfigure(
            0, minsize=215
        )
        self.result_frame.grid_columnconfigure(
            1, weight=1
        )

        self._mode_changed()
        self._ready()

    def _label(self, parent, text, row):
        label = ctk.CTkLabel(
            parent, text=text, anchor="w"
        )
        label.grid(
            row=row, column=0,
            padx=10, pady=7, sticky="w"
        )
        return label

    def _entry(self, parent, key, row):
        entry = ctk.CTkEntry(
            parent,
            textvariable=self.vars[key],
        )
        entry.grid(
            row=row, column=1,
            padx=10, pady=7, sticky="ew"
        )
        return entry

    def _section(self, parent, text, row):
        ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(
            row=row, column=0, columnspan=2,
            padx=10, pady=(15, 8), sticky="w"
        )

    def _mode_changed(self, _=None):
        mode = self.vars["mode"].get()
        if mode == "Number of Bars":
            self.number_label.configure(
                text="Number of Bars"
            )
            self.bar_length_label.configure(
                text="Bar Length (m)"
            )
            self.spacing_label.configure(
                text="Spacing (not used)"
            )
            self.distribution_label.configure(
                text="Distribution Length (not used)"
            )
        else:
            self.number_label.configure(
                text="Number of Bars (auto)"
            )
            self.bar_length_label.configure(
                text="Bar Length (not used)"
            )
            self.spacing_label.configure(
                text="Spacing (mm)"
            )
            self.distribution_label.configure(
                text="Distribution Length (m)"
            )

    def _unit_changed(self, _=None):
        unit=self.vars["length_unit"].get()
        previous=getattr(self,"_last_length_unit","m")
        if unit != previous:
            try:
                factor=FT_PER_M if previous=="m" and unit=="ft" else M_PER_FT
                for key in ("bar_length","distribution_length","lap_length"):
                    text=self.vars[key].get().strip()
                    if text:
                        self.vars[key].set(f"{float(text)*factor:.6f}".rstrip("0").rstrip("."))
            except (ValueError,TypeError):
                pass
        self._last_length_unit=unit
        self.bar_length_label.configure(text=f"Bar Length ({unit})" if self.vars["mode"].get()=="Number of Bars" else "Bar Length (not used)")
        self.distribution_label.configure(text=f"Distribution Length ({unit})" if self.vars["mode"].get()=="Spacing" else "Distribution Length (not used)")

    def _num(self, key, label, positive=False):
        try:
            value = float(self.vars[key].get())
        except ValueError as exc:
            raise ValueError(
                f"{label} must be a valid number."
            ) from exc

        if positive and value <= 0:
            raise ValueError(
                f"{label} must be greater than zero."
            )
        if not positive and value < 0:
            raise ValueError(
                f"{label} cannot be negative."
            )
        return value

    def calculate(self):
        try:
            mode = self.vars["mode"].get()

            number = (
                int(self._num("number", "Number of bars", True))
                if mode == "Number of Bars"
                else 0
            )
            bar_length = (
                self._num(
                    "bar_length",
                    "Bar length",
                    True,
                )
                if mode == "Number of Bars"
                else 0
            )
            spacing = (
                self._num("spacing", "Spacing", True)
                if mode == "Spacing"
                else 0
            )
            distribution = (
                self._num(
                    "distribution_length",
                    "Distribution length",
                    True,
                )
                if mode == "Spacing"
                else 0
            )

            self.result = SteelCalculator(
                diameter_mm=self._num(
                    "diameter", "Bar diameter", True
                ),
                number_of_bars=number,
                bar_length=bar_length,
                spacing_mm=spacing,
                distribution_length=distribution,
                cutting_allowance_percent=self._num(
                    "cutting", "Cutting allowance"
                ),
                lap_length=self._num(
                    "lap_length", "Lap length"
                ),
                laps_per_bar=int(
                    self._num("laps", "Laps per bar")
                ),
                binding_wire_percent=self._num(
                    "binding", "Binding wire percentage"
                ),
                length_unit=self.vars["length_unit"].get(),
                steel_rate=self._num(
                    "steel_rate", "Steel rate"
                ),
            ).calculate()

            self.analysis = SteelEstimateService.build_analysis(
                self.result,
                self._num("steel_rate", "Steel rate"),
            )
            self._show()
            self.status.configure(
                text="Calculated — ready to Generate BOQ"
            )
        except Exception as exc:
            messagebox.showerror(
                "Steel / Rebar Error",
                str(exc),
                parent=self,
            )

    def _ready(self):
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
                "Enter bar diameter and either Number of Bars "
                "or Spacing. Add lap and cutting allowances, "
                "then Calculate."
            ),
            wraplength=520,
            justify="left",
        ).grid(
            row=1, column=0, columnspan=2,
            padx=14, pady=12, sticky="ew",
        )

    def _show(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        r = self.result
        a = self.analysis
        row = 0

        self._section(
            self.result_frame,
            "Bar Schedule / Quantity",
            row,
        )
        row += 1

        rows = [
            (
                "Bar",
                f"Ø{r.get_value('diameter_mm', 0):g} mm"
            ),
            (
                "Number of Bars",
                str(r.get_value("bar_count", 0)),
            ),
            (
                "Spacing",
                (
                    f"{r.get_value('spacing_mm', 0):,.0f} mm"
                    if r.get_value("spacing_mm", 0) > 0
                    else "N/A"
                ),
            ),
            (
                "Base Length",
                f"{r.get_value('base_length_m', 0):,.3f} m",
            ),
            (
                "Lap Length",
                f"{r.get_value('lap_total_m', 0):,.3f} m",
            ),
            (
                "Cutting Allowance",
                f"{r.get_value('cutting_extra_m', 0):,.3f} m",
            ),
            (
                "Total Bar Length",
                f"{r.get_value('total_length_m', 0):,.3f} m",
            ),
            (
                "Unit Weight",
                f"{r.get_value('weight_per_m', 0):,.4f} kg/m",
            ),
            (
                "Total Steel",
                f"{r.quantity:,.3f} kg",
            ),
            (
                "Binding Wire",
                f"{r.get_value('binding_wire_kg', 0):,.3f} kg",
            ),
        ]

        row = self._rows(rows, row)

        self._section(
            self.result_frame,
            "Cost",
            row,
        )
        row += 1

        self._rows(
            [
                (
                    "Steel Amount",
                    f"PKR {a['material_total']:,.2f}",
                ),
                (
                    "Unit Rate",
                    f"PKR {a['unit_rate']:,.2f} / kg",
                ),
            ],
            row,
            bold=True,
        )

    def _rows(self, rows, start, bold=False):
        font = (
            ctk.CTkFont(weight="bold")
            if bold else None
        )
        for label, value in rows:
            ctk.CTkLabel(
                self.result_frame,
                text=label,
                anchor="w",
                font=font,
            ).grid(
                row=start, column=0,
                padx=(14, 10), pady=5,
                sticky="w",
            )
            ctk.CTkLabel(
                self.result_frame,
                text=value,
                anchor="w",
                font=font,
            ).grid(
                row=start, column=1,
                padx=(10, 14), pady=5,
                sticky="ew",
            )
            start += 1
        return start

    def generate_boq(self):
        if self.result is None:
            messagebox.showwarning(
                "Steel → BOQ",
                "Please calculate steel first.",
                parent=self,
            )
            return

        try:
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

            existing = (
                context.boq_controller.get_by_project(project.id)
                or []
            )
            highest = 0
            for item in existing:
                item_no = str(
                    getattr(item, "item_no", "")
                ).upper()
                if item_no.startswith("STEEL-"):
                    try:
                        highest = max(
                            highest,
                            int(item_no.split("-", 1)[1]),
                        )
                    except (ValueError, IndexError):
                        pass

            item_no = f"STEEL-{highest + 1:02d}"
            boq = BOQ(
                project_id=project.id,
                item_no=item_no,
                description=(
                    f"Reinforcement Steel "
                    f"Ø{self.result.get_value('diameter_mm', 0):g} mm"
                ),
                unit="kg",
                quantity=self.result.quantity,
                rate=self.analysis["unit_rate"],
                amount=self.analysis["total_cost"],
                remarks=(
                    f"Bars={self.result.get_value('bar_count', 0)}, "
                    f"Total length="
                    f"{self.result.get_value('total_length_m', 0):.3f} m, "
                    f"Lap={self.result.get_value('lap_total_m', 0):.3f} m, "
                    f"Cutting="
                    f"{self.result.get_value('cutting_allowance_percent', 0):.1f}%"
                ),
            )

            boq_id = context.boq_controller.create(boq)

            context.estimate_analysis_service.save(
                project_id=project.id,
                boq_id=int(boq_id),
                calculator_type="Steel",
                analysis=self.analysis,
            )

            self.status.configure(
                text=f"BOQ {item_no} added successfully"
            )

            messagebox.showinfo(
                "Steel → BOQ",
                (
                    f"BOQ item {item_no} created successfully.\n\n"
                    f"Steel: {self.result.quantity:,.3f} kg\n"
                    f"Total length: "
                    f"{self.result.get_value('total_length_m', 0):,.3f} m\n"
                    f"Binding wire: "
                    f"{self.result.get_value('binding_wire_kg', 0):,.3f} kg"
                ),
                parent=self,
            )

        except Exception as exc:
            messagebox.showerror(
                "Steel → BOQ Error",
                str(exc),
                parent=self,
            )

    def generate_material(self):
        if self.result is None:
            messagebox.showwarning("STEEL Material", "Please calculate steel first.", parent=self)
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
                "STEEL Material",
                "Material quantities added to the project material schedule.\n\n"
                + ("\n".join(lines) if lines else "No material records generated.")
                + "\n\nUse Materials / BOQ → Material Report for the consolidated report.",
                parent=self,
            )
        except Exception as ex:
            messagebox.showerror("STEEL Material Error", str(ex), parent=self)
    def reset_form(self):
        defaults = {
            "diameter": "12",
            "mode": "Number of Bars",
            "number": "",
            "bar_length": "",
            "spacing": "",
            "distribution_length": "",
            "lap_length": "0",
            "laps": "0",
            "cutting": "2",
            "binding": "2",
            "length_unit": "m",
            "steel_rate": "0",
        }
        for key, value in defaults.items():
            self.vars[key].set(value)
        self.result = None
        self.analysis = None
        self.status.configure(text="Ready")
        self._mode_changed()
        self._ready()

    def has_result(self):
        return self.result is not None


__all__ = ["SteelCalculatorForm"]
