"""
Civil Estimate Suite Pro v4.0
Brickwork Calculator Form

Engineer workflow:
Dimensions -> Quantity -> Material -> Labour -> BOQ
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
from services.brickwork_estimate_service import BrickworkEstimateService


class BrickworkCalculatorForm(BaseForm):
    def __init__(self, parent):
        super().__init__(
            parent,
            title="Brickwork Calculator",
            width=1120,
            height=760,
        )

        self.result: CalculationResult | None = None
        self.analysis: dict | None = None
        self._last_unit = "m³"

        self.vars = {
            "volume_unit": ctk.StringVar(value="m³"),
            "length": ctk.StringVar(value=""),
            "height": ctk.StringVar(value=""),
            "thickness": ctk.StringVar(value="0.23"),
            "brick_size": ctk.StringVar(value="Standard"),
            "mortar_ratio": ctk.StringVar(value="1:6"),
            "waste_percent": ctk.StringVar(value="5"),
            "brick_rate": ctk.StringVar(value="0"),
            "cement_bag_rate": ctk.StringVar(value="0"),
            "sand_rate": ctk.StringVar(value="0"),
            "skilled_productivity": ctk.StringVar(value="10"),
            "skilled_rate": ctk.StringVar(value="0"),
            "unskilled_productivity": ctk.StringVar(value="15"),
            "unskilled_rate": ctk.StringVar(value="0"),
        }

        apply_rate_defaults(self.vars)
        self._build_action_bar()
        self._build_form()
        self.after(100, lambda: self.length_entry.focus_set())

    # -----------------------------------------------------
    # ACTION BAR
    # -----------------------------------------------------
    def _build_action_bar(self):
        self.action_bar = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent",
        )
        self.action_bar.pack(
            fill="x",
            padx=5,
            pady=(0, 8),
        )

        self.calculate_button = ctk.CTkButton(
            self.action_bar,
            text="Calculate",
            width=140,
            command=self.calculate,
        )
        self.calculate_button.pack(side="left", padx=(0, 8))

        self.reset_button = ctk.CTkButton(
            self.action_bar,
            text="Reset",
            width=120,
            command=self.reset_form,
        )
        self.reset_button.pack(side="left", padx=8)

        self.boq_button = ctk.CTkButton(
            self.action_bar,
            text="Generate BOQ",
            width=160,
            command=self.generate_boq,
        )
        self.boq_button.pack(side="left", padx=8)

        self.material_button = ctk.CTkButton(
            self.action_bar,
            text="Generate Material",
            width=170,
            command=self.generate_material,
        )
        self.material_button.pack(side="left", padx=8)

        self.status = ctk.CTkLabel(
            self.action_bar,
            text="Ready",
            anchor="w",
        )
        self.status.pack(side="left", padx=15)

    # -----------------------------------------------------
    # FORM
    # -----------------------------------------------------
    def _build_form(self):
        workspace = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent",
        )
        workspace.pack(fill="both", expand=True)

        workspace.grid_columnconfigure(0, weight=0, minsize=475)
        workspace.grid_columnconfigure(1, weight=1)
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
        left.grid_columnconfigure(0, minsize=215)
        left.grid_columnconfigure(1, weight=1)

        row = 0
        self._section(left, "1. Brickwork Quantity", row)
        row += 1

        self._label(left, "Quantity Unit", row)
        self.unit_combo = ctk.CTkComboBox(
            left,
            variable=self.vars["volume_unit"],
            values=["m³", "Cft"],
            width=230,
            command=self._on_unit_change,
        )
        self.unit_combo.grid(
            row=row, column=1, padx=10, pady=7, sticky="ew"
        )
        row += 1

        self.length_label = self._label(left, "Length (m)", row)
        self.length_entry = self._entry_only(
            left, self.vars["length"], row
        )
        row += 1

        self.height_label = self._label(left, "Height (m)", row)
        self.height_entry = self._entry_only(
            left, self.vars["height"], row
        )
        row += 1

        self.thickness_label = self._label(left, "Wall Thickness (m)", row)
        self.thickness_entry = self._entry_only(
            left, self.vars["thickness"], row
        )
        row += 1

        self._label(left, "Brick Size", row)
        self.brick_combo = ctk.CTkComboBox(
            left,
            variable=self.vars["brick_size"],
            values=[
                "Standard",
                "9x4.5x3 inch",
                "9x4x3 inch",
                "Custom",
            ],
            width=230,
        )
        self.brick_combo.grid(
            row=row, column=1, padx=10, pady=7, sticky="ew"
        )
        row += 1

        self._label(left, "Mortar Ratio", row)
        self.mortar_combo = ctk.CTkComboBox(
            left,
            variable=self.vars["mortar_ratio"],
            values=["1:4", "1:5", "1:6"],
            width=230,
        )
        self.mortar_combo.grid(
            row=row, column=1, padx=10, pady=7, sticky="ew"
        )
        row += 1

        self._label(left, "Brick Waste (%)", row)
        self._entry_only(left, self.vars["waste_percent"], row)
        row += 1

        self._section(left, "2. Material Rates", row)
        row += 1
        self._label(left, "Bricks (PKR / No.)", row)
        self._entry_only(left, self.vars["brick_rate"], row)
        row += 1

        self.cement_rate_label = self._label(
            left, "Cement (PKR / Bag)", row
        )
        self._entry_only(left, self.vars["cement_bag_rate"], row)
        row += 1

        self.sand_rate_label = self._label(
            left, "Sand (PKR / m³)", row
        )
        self._entry_only(left, self.vars["sand_rate"], row)
        row += 1

        self._section(left, "3. Labour Norms & Rates", row)
        row += 1

        self.skilled_prod_label = self._label(
            left, "Skilled productivity (m³ / day)", row
        )
        self._entry_only(left, self.vars["skilled_productivity"], row)
        row += 1

        self._label(left, "Skilled labour (PKR / day)", row)
        self._entry_only(left, self.vars["skilled_rate"], row)
        row += 1

        self.unskilled_prod_label = self._label(
            left, "Unskilled productivity (m³ / day)", row
        )
        self._entry_only(left, self.vars["unskilled_productivity"], row)
        row += 1

        self._label(left, "Unskilled labour (PKR / day)", row)
        self._entry_only(left, self.vars["unskilled_rate"], row)

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
        self.result_frame.grid_columnconfigure(0, minsize=185)
        self.result_frame.grid_columnconfigure(1, weight=1)

        self._show_ready()

    def _label(self, parent, text, row):
        label = ctk.CTkLabel(
            parent,
            text=text,
            anchor="w",
        )
        label.grid(
            row=row,
            column=0,
            padx=10,
            pady=7,
            sticky="w",
        )
        return label

    def _entry_only(self, parent, variable, row):
        entry = ctk.CTkEntry(
            parent,
            textvariable=variable,
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

    # -----------------------------------------------------
    # UNIT
    # -----------------------------------------------------
    def _on_unit_change(self, _value=None):
        unit = self.vars["volume_unit"].get()
        previous = self._last_unit

        if unit != previous:
            try:
                dimension_factor = (
                    3.280839895 if previous == "m³" and unit == "Cft"
                    else 0.3048
                )
                for key in ("length", "height", "thickness"):
                    text = self.vars[key].get().strip()
                    if text:
                        self.vars[key].set(
                            f"{float(text) * dimension_factor:.6f}".rstrip("0").rstrip(".")
                        )

                # Price per volume unit: m3 -> Cft divides by 35.3147.
                rate_factor = (
                    0.028316846592
                    if unit == "Cft"
                    else 35.3146667215
                )
                text = self.vars["sand_rate"].get().strip()
                if text:
                    self.vars["sand_rate"].set(
                        f"{float(text) * rate_factor:.4f}".rstrip("0").rstrip(".")
                    )

                # Productivity is quantity/day: m3/day -> Cft/day.
                productivity_factor = (
                    35.3146667215
                    if unit == "Cft"
                    else 0.028316846592
                )
                for key in ("skilled_productivity", "unskilled_productivity"):
                    text = self.vars[key].get().strip()
                    if text:
                        self.vars[key].set(
                            f"{float(text) * productivity_factor:.4f}".rstrip("0").rstrip(".")
                        )
            except ValueError:
                pass

        self._last_unit = unit
        dimension = "m" if unit == "m³" else "ft"
        self.length_label.configure(text=f"Length ({dimension})")
        self.height_label.configure(text=f"Height ({dimension})")
        self.thickness_label.configure(text=f"Wall Thickness ({dimension})")
        self.sand_rate_label.configure(text=f"Sand (PKR / {unit})")
        self.skilled_prod_label.configure(text=f"Skilled productivity ({unit} / day)")
        self.unskilled_prod_label.configure(text=f"Unskilled productivity ({unit} / day)")

    # -----------------------------------------------------
    # VALIDATION / CALCULATION
    # -----------------------------------------------------
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
            length = self._number("length", "Length", True)
            height = self._number("height", "Height", True)
            thickness = self._number("thickness", "Wall thickness", True)
            waste = self._number("waste_percent", "Waste percentage")

            calculator = CalculatorFactory.create(
                "Brickwork",
                length=length,
                height=height,
                thickness=thickness,
                mortar_ratio=self.vars["mortar_ratio"].get(),
                brick_size=self.vars["brick_size"].get(),
                waste_percent=waste,
                volume_unit=self.vars["volume_unit"].get(),
            )
            self.result = calculator.calculate()
            self.analysis = self._build_analysis()
            self.show_result()
            self.status.configure(text="Calculated — ready to Generate BOQ")
        except Exception as ex:
            messagebox.showerror(
                "Brickwork Calculation Error",
                str(ex),
                parent=self,
            )

    def _labour_days(self, key):
        productivity = self._number(key, key.replace("_", " ").title(), True)
        return float(self.result.quantity) / productivity

    def _build_analysis(self):
        return BrickworkEstimateService.build_analysis(
            result=self.result,
            material_rates={
                "brick": self._number("brick_rate", "Brick rate"),
                "cement_bag": self._number(
                    "cement_bag_rate", "Cement rate"
                ),
                "sand": self._number("sand_rate", "Sand rate"),
            },
            skilled_days=self._labour_days("skilled_productivity"),
            skilled_rate=self._number("skilled_rate", "Skilled labour rate"),
            unskilled_days=self._labour_days("unskilled_productivity"),
            unskilled_rate=self._number(
                "unskilled_rate",
                "Unskilled labour rate",
            ),
        )

    # -----------------------------------------------------
    # RESULTS
    # -----------------------------------------------------
    def _show_ready(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        self._section(self.result_frame, "Calculation Result", 0)
        ctk.CTkLabel(
            self.result_frame,
            text=(
                "Enter dimensions, select m³ or Cft, enter brick/material "
                "rates and labour norms, then press Calculate."
            ),
            justify="left",
            anchor="w",
            wraplength=520,
        ).grid(
            row=1, column=0, columnspan=2,
            padx=14, pady=12, sticky="ew"
        )

    def show_result(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        r = self.result
        a = self.analysis
        row = 0

        self._section(self.result_frame, "Quantity Result", row)
        row += 1

        rows = [
            (
                "Dimensions",
                (
                    f"L {r.get_value('length', 0):,.3f} × "
                    f"H {r.get_value('height', 0):,.3f} × "
                    f"T {r.get_value('thickness', 0):,.3f} "
                    f"{r.get_value('dimension_unit', 'm')}"
                ),
            ),
            ("Brick Size", str(r.get_value("brick_size", ""))),
            ("Mortar Ratio", str(r.get_value("mortar_ratio", ""))),
            ("Wall Quantity", f"{r.quantity:,.3f} {r.unit}"),
            (
                "Bricks",
                f"{r.get_value('brick_quantity', 0):,.0f} Nos",
            ),
            (
                "Mortar",
                f"{r.get_value('mortar_volume', 0):,.3f} {r.unit}",
            ),
            ("Cement", f"{r.cement_bags:,.2f} Bags"),
            ("Sand", f"{r.sand_volume:,.3f} {r.unit}"),
        ]
        row = self._rows(rows, row)

        self._section(self.result_frame, "Material Cost Build-up", row)
        row += 1
        material_rows = [
            (
                item["name"],
                (
                    f"{item['quantity']:,.3f} {item['unit']} × "
                    f"PKR {item['rate']:,.2f} = PKR {item['amount']:,.2f}"
                ),
            )
            for item in a["materials"]
        ]
        row = self._rows(material_rows, row)
        row = self._rows(
            [("Material Total", f"PKR {a['material_total']:,.2f}")],
            row,
            bold=True,
        )

        self._section(self.result_frame, "Labour Cost Build-up", row)
        row += 1
        labour_rows = [
            (
                item["name"],
                (
                    f"{item['quantity']:,.2f} {item['unit']} × "
                    f"PKR {item['rate']:,.2f} = PKR {item['amount']:,.2f}"
                ),
            )
            for item in a["labour"]
        ]
        row = self._rows(labour_rows, row)
        row = self._rows(
            [("Labour Total", f"PKR {a['labour_total']:,.2f}")],
            row,
            bold=True,
        )

        self._section(self.result_frame, "Final Cost", row)
        row += 1
        row = self._rows(
            [
                ("Total Cost", f"PKR {a['total_cost']:,.2f}"),
                ("Unit Rate", f"PKR {a['unit_rate']:,.2f} / {r.unit}"),
            ],
            row,
            bold=True,
        )

        ctk.CTkLabel(
            self.result_frame,
            text=(
                "BOQ stores dimensions, physical quantity, material quantities "
                "and labour quantities. Cost build-up remains in detailed analysis."
            ),
            justify="left",
            anchor="w",
            wraplength=520,
        ).grid(
            row=row, column=0, columnspan=2,
            padx=14, pady=(18, 12), sticky="ew"
        )

    def _rows(self, rows, start_row, bold=False):
        font = ctk.CTkFont(weight="bold") if bold else None
        row = start_row
        for label, value in rows:
            ctk.CTkLabel(
                self.result_frame,
                text=label,
                anchor="w",
                font=font,
            ).grid(
                row=row, column=0,
                padx=(14, 10), pady=5,
                sticky="w",
            )
            ctk.CTkLabel(
                self.result_frame,
                text=value,
                anchor="w",
                justify="left",
                font=font,
            ).grid(
                row=row, column=1,
                padx=(10, 14), pady=5,
                sticky="ew",
            )
            row += 1
        return row

    # -----------------------------------------------------
    # BOQ
    # -----------------------------------------------------
    def generate_boq(self):
        if self.result is None:
            messagebox.showwarning(
                "Brickwork → BOQ",
                "Please calculate brickwork first.",
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
                raise ValueError("Application context is not available.")

            controller = context.boq_controller
            existing = controller.get_by_project(project.id) or []
            highest = 0
            for item in existing:
                item_no = str(getattr(item, "item_no", "")).upper()
                if item_no.startswith("BRICK-"):
                    try:
                        highest = max(highest, int(item_no.split("-", 1)[1]))
                    except (ValueError, IndexError):
                        pass

            item_no = f"BRICK-{highest + 1:02d}"
            d = self.analysis["dimensions"]

            remarks = (
                f"Detailed Brickwork analysis | "
                f"L={d['length']:.3f} {d['dimension_unit']}, "
                f"H={d['height']:.3f} {d['dimension_unit']}, "
                f"T={d['thickness']:.3f} {d['dimension_unit']} | "
                f"Brick={self.analysis['brick_size']} | "
                f"Mortar={self.analysis['mortar_ratio']}"
            )

            boq = BOQ(
                project_id=project.id,
                item_no=item_no,
                description=f"Brickwork ({self.analysis['mortar_ratio']})",
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
                calculator_type="Brickwork",
                analysis=self.analysis,
            )

            self.status.configure(
                text=f"BOQ {item_no} added successfully"
            )

            messagebox.showinfo(
                "Brickwork → BOQ",
                (
                    f"BOQ item {item_no} created successfully.\n\n"
                    f"Quantity: {self.analysis['quantity']:,.3f} {self.analysis['unit']}\n"
                    f"Bricks: {self.analysis['materials'][0]['quantity']:,.0f} Nos\n"
                    f"Cement: {self.analysis['materials'][1]['quantity']:,.3f} Bags\n"
                    f"Sand: {self.analysis['materials'][2]['quantity']:,.3f} {self.analysis['unit']}"
                ),
                parent=self,
            )
        except Exception as ex:
            messagebox.showerror(
                "Brickwork → BOQ Error",
                str(ex),
                parent=self,
            )

    # -----------------------------------------------------
    # MATERIAL
    # -----------------------------------------------------
    def generate_material(self):
        if self.result is None:
            messagebox.showwarning("BRICKWORK Material", "Please calculate brickwork first.", parent=self)
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
                "BRICKWORK Material",
                "Material quantities added to the project material schedule.\n\n"
                + ("\n".join(lines) if lines else "No material records generated.")
                + "\n\nUse Materials / BOQ → Material Report for the consolidated report.",
                parent=self,
            )
        except Exception as ex:
            messagebox.showerror("BRICKWORK Material Error", str(ex), parent=self)
    def reset_form(self):
        self.vars["length"].set("")
        self.vars["height"].set("")
        self.vars["thickness"].set("0.23")
        self.vars["brick_size"].set("Standard")
        self.vars["mortar_ratio"].set("1:6")
        self.vars["waste_percent"].set("5")
        self.vars["brick_rate"].set("0")
        self.vars["cement_bag_rate"].set("0")
        self.vars["sand_rate"].set("0")
        self.vars["skilled_productivity"].set("10")
        self.vars["skilled_rate"].set("0")
        self.vars["unskilled_productivity"].set("15")
        self.vars["unskilled_rate"].set("0")
        self._last_unit = "m³"
        self.vars["volume_unit"].set("m³")
        self._on_unit_change()

        self.result = None
        self.analysis = None
        self.status.configure(text="Ready")
        self._show_ready()

    def has_result(self):
        return self.result is not None
