"""
Civil Estimate Suite Pro v4.0
Engineer-friendly Column Steel / Rebar Form
"""
from __future__ import annotations
from config.rate_defaults import apply_rate_defaults

import customtkinter as ctk
from tkinter import messagebox

from calculations.column_steel_calculator import ColumnSteelCalculator
from core.current_project import CurrentProject
from gui.forms.base_form import BaseForm
from models.boq import BOQ
from services.column_steel_estimate_service import ColumnSteelEstimateService


FT_PER_M = 3.280839895013123
M_PER_FT = 0.3048
CFT_PER_M3 = 35.31466672148859
M3_PER_CFT = 0.028316846592

class ColumnSteelCalculatorForm(BaseForm):
    def __init__(self, parent):
        super().__init__(parent, title="Column Steel / Rebar Calculator",
                         width=1180, height=800)
        self.result = None
        self.analysis = None
        self.vars = {k: ctk.StringVar(value=v) for k, v in {
            "count": "1", "unit": "m", "length": "0.30", "width": "0.30",
            "height": "3.0", "cover": "40",
            "vertical_dia": "16", "vertical_bars": "8",
            "lap": "0", "laps": "0",
            "stirrup_dia": "8", "spacing": "150", "hook": "200",
            "cutting": "2", "binding": "2", "rate": "0"
        }.items()}
        apply_rate_defaults(self.vars)
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        top.pack(fill="x", padx=5, pady=(0, 8))
        for text, cmd, width in [
            ("Calculate", self.calculate, 140),
            ("Reset", self.reset_form, 120),
            ("Generate BOQ", self.generate_boq, 160),
            ("Generate Material", self.generate_material, 175),
        ]:
            ctk.CTkButton(top, text=text, width=width, command=cmd).pack(side="left", padx=6)
        self.status = ctk.CTkLabel(top, text="Ready", anchor="w")
        self.status.pack(side="left", padx=15)

        ws = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        ws.pack(fill="both", expand=True)
        ws.grid_columnconfigure(0, weight=0, minsize=500)
        ws.grid_columnconfigure(1, weight=1)
        ws.grid_rowconfigure(0, weight=1)

        left = ctk.CTkScrollableFrame(ws, corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.grid_columnconfigure(0, minsize=255)
        left.grid_columnconfigure(1, weight=1)

        row = 0
        self._section(left, "1. Column Dimensions", row); row += 1
        for key, label in [
            ("unit", "Length Unit"),
            ("count", "Number of Columns"),
            ("length", "Column Length"),
            ("width", "Column Width"),
            ("height", "Column Height"),
            ("cover", "Clear Cover (mm)"),
        ]:
            self._label(left, label, row)
            if key == "unit":
                ctk.CTkComboBox(
                    left, variable=self.vars[key],
                    values=["m", "ft"], command=self._unit_changed
                ).grid(row=row, column=1, padx=10, pady=7, sticky="ew")
            else:
                self._entry(left, key, row)
            row += 1

        self._section(left, "2. Vertical Main Bars", row); row += 1
        for key, label in [
            ("vertical_dia", "Vertical Bar Diameter (mm)"),
            ("vertical_bars", "Vertical Bars / Column"),
            ("lap", "Lap / Splice Length (m)"),
            ("laps", "Laps / Bar"),
        ]:
            self._label(left, label, row); self._entry(left, key, row); row += 1

        self._section(left, "3. Stirrups / Ties", row); row += 1
        for key, label in [
            ("stirrup_dia", "Stirrup Diameter (mm)"),
            ("spacing", "Stirrup Spacing (mm)"),
            ("hook", "Hook / End Allowance (mm)"),
        ]:
            self._label(left, label, row); self._entry(left, key, row); row += 1

        self._section(left, "4. Allowance & Rate", row); row += 1
        for key, label in [
            ("cutting", "Cutting Allowance (%)"),
            ("binding", "Binding Wire (% Steel)"),
            ("rate", "Steel Rate (PKR / kg)"),
        ]:
            self._label(left, label, row); self._entry(left, key, row); row += 1

        self.result_frame = ctk.CTkScrollableFrame(ws, corner_radius=10)
        self.result_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.result_frame.grid_columnconfigure(0, minsize=225)
        self.result_frame.grid_columnconfigure(1, weight=1)
        self._ready()

    def _label(self, parent, text, row):
        ctk.CTkLabel(parent, text=text, anchor="w").grid(
            row=row, column=0, padx=10, pady=7, sticky="w")

    def _entry(self, parent, key, row):
        ctk.CTkEntry(parent, textvariable=self.vars[key]).grid(
            row=row, column=1, padx=10, pady=7, sticky="ew")

    def _section(self, parent, text, row):
        ctk.CTkLabel(parent, text=text,
                     font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=row, column=0, columnspan=2, padx=10, pady=(15, 8), sticky="w")

    def _unit_changed(self, _value=None):
        unit=self.vars["unit"].get()
        previous=getattr(self,"_last_unit","m")
        if unit != previous:
            try:
                factor=FT_PER_M if previous=="m" and unit=="ft" else M_PER_FT
                for key in ("length","width","height","lap"):
                    text=self.vars[key].get().strip()
                    if text:
                        self.vars[key].set(f"{float(text)*factor:.6f}".rstrip("0").rstrip("."))
            except (ValueError,TypeError):
                pass
        self._last_unit=unit

    def _num(self, key, label, positive=False):
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
            self.result = ColumnSteelCalculator(
                column_length=self._num("length", "Column length", True),
                column_width=self._num("width", "Column width", True),
                column_height=self._num("height", "Column height", True),
                cover_mm=self._num("cover", "Clear cover"),
                vertical_dia_mm=self._num("vertical_dia", "Vertical diameter", True),
                vertical_bars=int(self._num("vertical_bars", "Vertical bars", True)),
                vertical_lap_length_m=self._num("lap", "Lap length"),
                vertical_laps=int(self._num("laps", "Laps")),
                stirrup_dia_mm=self._num("stirrup_dia", "Stirrup diameter", True),
                stirrup_spacing_mm=self._num("spacing", "Stirrup spacing", True),
                stirrup_hook_extra_mm=self._num("hook", "Hook allowance"),
                cutting_allowance_percent=self._num("cutting", "Cutting allowance"),
                binding_wire_percent=self._num("binding", "Binding wire"),
                steel_rate=self._num("rate", "Steel rate"),
                column_count=int(self._num("count", "Number of columns", True)),
                length_unit=self.vars["unit"].get(),
            ).calculate()
            self.analysis = ColumnSteelEstimateService.build_analysis(
                self.result, self._num("rate", "Steel rate"))
            self._show()
            self.status.configure(text="Calculated — ready to Generate BOQ")
        except Exception as exc:
            messagebox.showerror("Column Steel Error", str(exc), parent=self)

    def _ready(self):
        for w in self.result_frame.winfo_children(): w.destroy()
        self._section(self.result_frame, "Column Bar Schedule", 0)
        ctk.CTkLabel(
            self.result_frame,
            text="Enter column dimensions, vertical bars and stirrup spacing, then Calculate.",
            wraplength=550, justify="left").grid(
                row=1, column=0, columnspan=2, padx=14, pady=12, sticky="ew")

    def _show(self):
        for w in self.result_frame.winfo_children(): w.destroy()
        r = 0
        self._section(self.result_frame, "Column Summary", r); r += 1
        a = self.analysis
        r = self._rows([
            ("Columns", str(a["dimensions"]["count"])),
            ("Size", f'{a["dimensions"]["length"]:.3f} × {a["dimensions"]["width"]:.3f} × {a["dimensions"]["height"]:.3f} {a["dimensions"]["unit"]}'),
            ("Clear Cover", f'{a["dimensions"]["cover_mm"]:.1f} mm'),
            ("Base Steel", f'{a["base_steel_kg"]:,.3f} kg'),
            ("Cutting Allowance", f'{a["cutting_kg"]:,.3f} kg'),
            ("Total Steel", f'{a["quantity"]:,.3f} kg'),
            ("Binding Wire", f'{a["binding_wire_kg"]:,.3f} kg'),
        ], r)
        self._section(self.result_frame, "Vertical Bar Schedule", r); r += 1
        r = self._rows([
            ("Main Bars", f'Ø{a["vertical"]["diameter_mm"]:g} — {a["vertical"]["bars"]} bars/column'),
            ("Bar Length", f'{a["vertical"]["length_each_m"]:.3f} m each'),
            ("Total Length", f'{a["vertical"]["total_length_m"]:.3f} m'),
            ("Weight", f'{a["vertical"]["weight_kg"]:.3f} kg'),
        ], r)
        self._section(self.result_frame, "Stirrup / Tie Schedule", r); r += 1
        r = self._rows([
            ("Stirrups", f'Ø{a["stirrups"]["diameter_mm"]:g} @ {a["stirrups"]["spacing_mm"]:g} mm'),
            ("Count / Column", str(a["stirrups"]["count_one"])),
            ("Total Stirrups", str(a["stirrups"]["total_count"])),
            ("Cutting Length", f'{a["stirrups"]["cutting_length_m"]:.3f} m'),
            ("Total Length", f'{a["stirrups"]["total_length_m"]:.3f} m'),
            ("Weight", f'{a["stirrups"]["weight_kg"]:.3f} kg'),
        ], r)
        self._section(self.result_frame, "Cost", r); r += 1
        self._rows([
            ("Steel Amount", f'PKR {a["total_cost"]:,.2f}'),
            ("Unit Rate", f'PKR {a["unit_rate"]:,.2f} / kg'),
        ], r, True)

    def _rows(self, rows, start, bold=False):
        font = ctk.CTkFont(weight="bold") if bold else None
        for label, value in rows:
            ctk.CTkLabel(self.result_frame, text=label, anchor="w",
                         font=font).grid(
                row=start, column=0, padx=(14, 10), pady=5, sticky="w")
            ctk.CTkLabel(self.result_frame, text=value, anchor="w",
                         font=font, justify="left", wraplength=620).grid(
                row=start, column=1, padx=(10, 14), pady=5, sticky="ew")
            start += 1
        return start

    def generate_boq(self):
        if self.result is None:
            messagebox.showwarning("Column Steel → BOQ",
                                   "Please calculate column steel first.",
                                   parent=self); return
        try:
            project = CurrentProject.get()
            if project is None or getattr(project, "id", None) is None:
                raise ValueError("Please select/open a project before generating BOQ.")
            context = self.application_context
            if context is None:
                raise ValueError("Application context is not available.")
            items = context.boq_controller.get_by_project(project.id) or []
            highest = 0
            for item in items:
                no = str(getattr(item, "item_no", "")).upper()
                if no.startswith("COLUMN-STEEL-"):
                    try: highest = max(highest, int(no.split("-", 2)[2]))
                    except (ValueError, IndexError): pass
            item_no = f"COLUMN-STEEL-{highest + 1:02d}"
            d = self.analysis["dimensions"]
            boq = BOQ(
                project_id=project.id, item_no=item_no,
                description="Column Reinforcement Steel",
                unit="kg", quantity=self.result.quantity,
                rate=self.analysis["unit_rate"],
                amount=self.analysis["total_cost"],
                remarks=(
                    f'{d["count"]} columns | {d["length"]:.3f}×{d["width"]:.3f}×'
                    f'{d["height"]:.3f} {d["unit"]} | '
                    f'Vertical Ø{self.analysis["vertical"]["diameter_mm"]:g} '
                    f'× {self.analysis["vertical"]["bars"]}/column | '
                    f'Stirrup Ø{self.analysis["stirrups"]["diameter_mm"]:g} '
                    f'@ {self.analysis["stirrups"]["spacing_mm"]:g} mm'
                ),
            )
            boq_id = context.boq_controller.create(boq)
            context.estimate_analysis_service.save(
                project_id=project.id, boq_id=int(boq_id),
                calculator_type="Column Steel", analysis=self.analysis)
            self.status.configure(text=f"BOQ {item_no} added successfully")
            messagebox.showinfo(
                "Column Steel → BOQ",
                f"BOQ item {item_no} created successfully.\n\n"
                f"Total Steel: {self.result.quantity:,.3f} kg\n"
                f"Binding Wire: {self.analysis['binding_wire_kg']:,.3f} kg",
                parent=self)
        except Exception as exc:
            messagebox.showerror("Column Steel → BOQ Error", str(exc), parent=self)

    def generate_material(self):
        if self.result is None:
            messagebox.showwarning("COLUMN STEEL Material", "Please calculate column steel first.", parent=self)
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
                "COLUMN STEEL Material",
                "Material quantities added to the project material schedule.\n\n"
                + ("\n".join(lines) if lines else "No material records generated.")
                + "\n\nUse Materials / BOQ → Material Report for the consolidated report.",
                parent=self,
            )
        except Exception as ex:
            messagebox.showerror("COLUMN STEEL Material Error", str(ex), parent=self)
    def reset_form(self):
        defaults = {
            "count":"1","unit":"m","length":"0.30","width":"0.30",
            "height":"3.0","cover":"40","vertical_dia":"16",
            "vertical_bars":"8","lap":"0","laps":"0",
            "stirrup_dia":"8","spacing":"150","hook":"200",
            "cutting":"2","binding":"2","rate":"0"}
        for k,v in defaults.items(): self.vars[k].set(v)
        self.result=None; self.analysis=None
        self.status.configure(text="Ready"); self._ready()

    def has_result(self):
        return self.result is not None


__all__ = ["ColumnSteelCalculatorForm"]
