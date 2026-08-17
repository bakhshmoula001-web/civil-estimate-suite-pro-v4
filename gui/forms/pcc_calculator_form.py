"""
Civil Estimate Suite Pro v4.0
PCC Calculator + Detailed Cost Build-up

Reference workflow for the new estimation architecture:

Dimensions -> Quantity -> Materials -> Labour -> Cost -> BOQ
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
from services.pcc_estimate_service import PCCEstimateService


class PCCCalculatorForm(BaseForm):
    """PCC quantity and detailed rate-analysis form."""

    def __init__(self, parent):
        super().__init__(
            parent,
            title="PCC Calculator",
            width=1120,
            height=760,
        )

        self.result: CalculationResult | None = None
        self.analysis: dict | None = None
        self.calculator_key = "pcc"
        self.application_context = None
        self._last_volume_unit = "m³"

        self.vars = {
            "length": ctk.StringVar(value=""),
            "width": ctk.StringVar(value=""),
            "height": ctk.StringVar(value=""),
            "volume_unit": ctk.StringVar(value="m³"),
            "mix_ratio": ctk.StringVar(value="1:2:4"),
            "cement_bag_rate": ctk.StringVar(value="0"),
            "sand_rate": ctk.StringVar(value="0"),
            "aggregate_rate": ctk.StringVar(value="0"),
            "skilled_productivity": ctk.StringVar(value="1.00"),
            "skilled_rate": ctk.StringVar(value="0"),
            "unskilled_productivity": ctk.StringVar(value="2.00"),
            "unskilled_rate": ctk.StringVar(value="0"),
        }

        self._create_fixed_boq_action()
        apply_rate_defaults(self.vars)
        self._build_form()
        self.bind("<Return>", lambda _e: self.calculate())
        self.bind("<Escape>", lambda _e: self.cancel())

    def _create_fixed_boq_action(self):
        """Create fixed actions outside the scrollable calculation area.

        The engineer must always be able to Calculate, Reset, or Generate
        BOQ without scrolling to the end of a long result.
        """
        self.action_bar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.action_bar.pack(fill="x", side="top", padx=5, pady=(0, 8))

        self.calculate_button = ctk.CTkButton(
            self.action_bar, text="Calculate", width=150, command=self.calculate
        )
        self.calculate_button.pack(side="left", padx=(0, 8))

        self.reset_button = ctk.CTkButton(
            self.action_bar, text="Reset", width=120, command=self.reset_form
        )
        self.reset_button.pack(side="left", padx=8)

        self.boq_footer_button = ctk.CTkButton(
            self.action_bar,
            text="Generate BOQ",
            width=170,
            command=self.generate_boq,
        )
        self.boq_footer_button.pack(side="left", padx=8)

        self.material_button = ctk.CTkButton(
            self.action_bar,
            text="Generate Material",
            width=180,
            command=self.generate_material,
        )
        self.material_button.pack(side="left", padx=8)

        self.action_status = ctk.CTkLabel(self.action_bar, text="Ready", anchor="w")
        self.action_status.pack(side="left", padx=15)

    # =========================================================
    # UI
    # =========================================================

    def _build_form(self):
        """Build an aligned two-column engineer workspace.

        Left: input/calculation controls.
        Right: calculation results.
        The action bar remains fixed at the top so Generate BOQ is
        always visible regardless of result length.
        """
        workspace = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent",
        )
        workspace.pack(fill="both", expand=True)
        workspace.grid_columnconfigure(0, weight=0, minsize=470)
        workspace.grid_columnconfigure(1, weight=1)
        workspace.grid_rowconfigure(0, weight=1)

        # -----------------------------
        # LEFT: Inputs
        # -----------------------------
        left = ctk.CTkScrollableFrame(
            workspace,
            corner_radius=10,
        )
        left.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8),
            pady=0,
        )
        left.grid_columnconfigure(0, weight=0, minsize=205)
        left.grid_columnconfigure(1, weight=1, minsize=220)

        row = 0
        self._section(left, "1. PCC Quantity", row)
        row += 1

        ctk.CTkLabel(
            left, text="Quantity Unit", anchor="w"
        ).grid(row=row, column=0, padx=12, pady=7, sticky="w")
        self.unit_combo = ctk.CTkComboBox(
            left,
            variable=self.vars["volume_unit"],
            values=["m³", "Cft"],
            width=220,
            command=self._on_unit_change,
        )
        self.unit_combo.grid(row=row, column=1, padx=12, pady=7, sticky="ew")
        row += 1

        self.length_label = ctk.CTkLabel(left, text="Length (m)", anchor="w")
        self.length_label.grid(row=row, column=0, padx=12, pady=7, sticky="w")
        self.length_entry = ctk.CTkEntry(left, textvariable=self.vars["length"])
        self.length_entry.grid(row=row, column=1, padx=12, pady=7, sticky="ew")
        row += 1

        self.width_label = ctk.CTkLabel(left, text="Width (m)", anchor="w")
        self.width_label.grid(row=row, column=0, padx=12, pady=7, sticky="w")
        self.width_entry = ctk.CTkEntry(left, textvariable=self.vars["width"])
        self.width_entry.grid(row=row, column=1, padx=12, pady=7, sticky="ew")
        row += 1

        self.height_label = ctk.CTkLabel(
            left, text="Thickness / Height (m)", anchor="w"
        )
        self.height_label.grid(row=row, column=0, padx=12, pady=7, sticky="w")
        self.height_entry = ctk.CTkEntry(left, textvariable=self.vars["height"])
        self.height_entry.grid(row=row, column=1, padx=12, pady=7, sticky="ew")
        row += 1

        ctk.CTkLabel(left, text="Mix Ratio", anchor="w").grid(
            row=row, column=0, padx=12, pady=7, sticky="w"
        )
        self.mix_combo = ctk.CTkComboBox(
            left,
            variable=self.vars["mix_ratio"],
            values=["1:2:4", "1:3:6", "1:1.5:3", "1:4:8"],
        )
        self.mix_combo.grid(row=row, column=1, padx=12, pady=7, sticky="ew")
        row += 1

        self._section(left, "2. Material Rates", row)
        row += 1

        row = self._rate_entry(left, "Cement (PKR / Bag)", self.vars["cement_bag_rate"], row)

        self.sand_rate_label = ctk.CTkLabel(left, text="Sand (PKR / m³)", anchor="w")
        self.sand_rate_label.grid(row=row, column=0, padx=12, pady=7, sticky="w")
        self._entry_only(left, self.vars["sand_rate"], row)
        row += 1

        self.aggregate_rate_label = ctk.CTkLabel(
            left, text="Coarse Aggregate (PKR / m³)", anchor="w"
        )
        self.aggregate_rate_label.grid(row=row, column=0, padx=12, pady=7, sticky="w")
        self._entry_only(left, self.vars["aggregate_rate"], row)
        row += 1

        self._section(left, "3. Labour Norms & Rates", row)
        row += 1

        self.skilled_productivity_label = ctk.CTkLabel(
            left, text="Skilled productivity (m³ / day)", anchor="w"
        )
        self.skilled_productivity_label.grid(
            row=row, column=0, padx=12, pady=7, sticky="w"
        )
        self._entry_only(left, self.vars["skilled_productivity"], row)
        row += 1

        row = self._rate_entry(
            left, "Skilled labour rate (PKR / day)", self.vars["skilled_rate"], row
        )

        self.unskilled_productivity_label = ctk.CTkLabel(
            left, text="Unskilled productivity (m³ / day)", anchor="w"
        )
        self.unskilled_productivity_label.grid(
            row=row, column=0, padx=12, pady=7, sticky="w"
        )
        self._entry_only(left, self.vars["unskilled_productivity"], row)
        row += 1

        self._rate_entry(
            left, "Unskilled labour rate (PKR / day)", self.vars["unskilled_rate"], row
        )

        # -----------------------------
        # RIGHT: Results
        # -----------------------------
        self.result_frame = ctk.CTkScrollableFrame(
            workspace,
            corner_radius=10,
        )
        self.result_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(8, 0),
            pady=0,
        )
        self.result_frame.grid_columnconfigure(1, weight=1)

        self._show_ready_result()

        self.after(100, lambda: self.length_entry.focus_set())

    def _show_ready_result(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        self._section(self.result_frame, "Calculation Result", 0)
        ctk.CTkLabel(
            self.result_frame,
            text=(
                "Enter the PCC dimensions, select m³ or Cft, enter material "
                "and labour rates, then press Calculate."
            ),
            justify="left",
            anchor="w",
            wraplength=520,
        ).grid(
            row=1, column=0, columnspan=2,
            padx=14, pady=12, sticky="ew"
        )

    def _section(self, parent, text, row):
        ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=row, column=0, columnspan=2, padx=10, pady=(15, 8), sticky="w")

    def _entry(self, parent, text, variable, row):
        ctk.CTkLabel(parent, text=text).grid(row=row, column=0, padx=10, pady=7, sticky="w")
        entry = ctk.CTkEntry(parent, textvariable=variable, width=260)
        entry.grid(row=row, column=1, padx=10, pady=7, sticky="w")
        return entry

    def _rate_entry(self, parent, text, variable, row):
        self._entry(parent, text, variable, row)
        return row + 1

    def _entry_only(self, parent, variable, row):
        entry = ctk.CTkEntry(parent, textvariable=variable, width=260)
        entry.grid(row=row, column=1, padx=10, pady=7, sticky="w")
        return entry

    def _on_unit_change(self, _value=None):
        unit = self.vars["volume_unit"].get()
        previous = self._last_volume_unit

        if unit != previous:
            # Keep the physical estimate unchanged when the engineer switches
            # between metric volume and cubic feet.
            try:
                factor = 3.280839895 if previous == "m³" and unit == "Cft" else 0.3048

                for key in ("length", "width", "height"):
                    text = self.vars[key].get().strip()
                    if text:
                        self.vars[key].set(f"{float(text) * factor:.6f}".rstrip("0").rstrip("."))

                # Volumetric material rates are converted inversely because
                # the same material price is being expressed per selected unit.
                rate_factor = 0.028316846592 if unit == "Cft" else 35.3146667215
                for key in ("sand_rate", "aggregate_rate"):
                    text = self.vars[key].get().strip()
                    if text:
                        self.vars[key].set(f"{float(text) * rate_factor:.4f}".rstrip("0").rstrip("."))

                # Productivity is a quantity-per-day value, so its direction
                # is the opposite of a unit-rate conversion.
                productivity_factor = 35.3146667215 if unit == "Cft" else 0.028316846592
                for key in ("skilled_productivity", "unskilled_productivity"):
                    text = self.vars[key].get().strip()
                    if text:
                        self.vars[key].set(f"{float(text) * productivity_factor:.4f}".rstrip("0").rstrip("."))
            except ValueError:
                # If a field is empty/non-numeric, simply leave it for the
                # engineer to enter; changing the unit must never crash the UI.
                pass

        self._last_volume_unit = unit
        dimension_unit = "m" if unit == "m³" else "ft"
        self.length_label.configure(text=f"Length ({dimension_unit})")
        self.width_label.configure(text=f"Width ({dimension_unit})")
        self.height_label.configure(text=f"Thickness / Height ({dimension_unit})")
        self.sand_rate_label.configure(text=f"Sand (PKR / {unit})")
        self.aggregate_rate_label.configure(text=f"Coarse Aggregate (PKR / {unit})")
        self.skilled_productivity_label.configure(text=f"Skilled productivity ({unit} / day)")
        self.unskilled_productivity_label.configure(text=f"Unskilled productivity ({unit} / day)")

    # =========================================================
    # CALCULATION
    # =========================================================

    def _number(self, key, label, allow_zero=True):
        try:
            value = float(self.vars[key].get())
        except ValueError as exc:
            raise ValueError(f"{label} must be a valid number.") from exc
        if allow_zero:
            if value < 0:
                raise ValueError(f"{label} cannot be negative.")
        elif value <= 0:
            raise ValueError(f"{label} must be greater than zero.")
        return value

    def _validate_dimensions(self):
        return (
            self._number("length", "Length", False),
            self._number("width", "Width", False),
            self._number("height", "Thickness / Height", False),
            self.vars["mix_ratio"].get(),
            self.vars["volume_unit"].get(),
        )

    def calculate(self):
        try:
            length, width, height, mix_ratio, volume_unit = self._validate_dimensions()
            calculator = CalculatorFactory.create(
                "PCC",
                length=length,
                width=width,
                height=height,
                mix_ratio=mix_ratio,
                volume_unit=volume_unit,
            )
            self.result = calculator.calculate()
            self.analysis = self._try_build_analysis()
            self.show_result()
            self.action_status.configure(text="Calculated — ready to Generate BOQ")
        except Exception as ex:
            messagebox.showerror("PCC Calculation Error", str(ex), parent=self)

    def _try_build_analysis(self):
        if self.result is None:
            return None
        try:
            return PCCEstimateService.build_analysis(
                result=self.result,
                material_rates={
                    "cement_bag": self._number("cement_bag_rate", "Cement rate"),
                    "sand": self._number("sand_rate", "Sand rate"),
                    "aggregate": self._number("aggregate_rate", "Aggregate rate"),
                },
                skilled_days=self._calculated_days("skilled"),
                skilled_rate=self._number("skilled_rate", "Skilled labour rate"),
                unskilled_days=self._calculated_days("unskilled"),
                unskilled_rate=self._number("unskilled_rate", "Unskilled labour rate"),
            )
        except ValueError:
            return None

    def _calculated_days(self, labour_type):
        if self.result is None:
            return 0.0
        if labour_type == "skilled":
            productivity = self._number("skilled_productivity", "Skilled productivity", False)
        else:
            productivity = self._number("unskilled_productivity", "Unskilled productivity", False)
        return float(self.result.quantity) / productivity

    # =========================================================
    # RESULT DISPLAY
    # =========================================================

    def show_result(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        self.result_frame.grid_columnconfigure(0, weight=0, minsize=175)
        self.result_frame.grid_columnconfigure(1, weight=1)

        r = self.result
        row = 0

        self._section(self.result_frame, "Quantity Result", row)
        row += 1

        quantity_rows = [
            (
                "Dimensions",
                (
                    f"L {r.get_value('length', 0):,.3f} × "
                    f"W {r.get_value('width', 0):,.3f} × "
                    f"T {r.get_value('height', 0):,.3f} "
                    f"{r.get_value('dimension_unit', 'm')}"
                ),
            ),
            ("Mix Ratio", str(r.get_value("mix_ratio", ""))),
            ("Wet Volume", f"{r.wet_volume:,.3f} {r.unit}"),
            ("Dry Volume", f"{r.dry_volume:,.3f} {r.unit}"),
            ("Cement", f"{r.cement_bags:,.2f} Bags"),
            ("Sand", f"{r.sand_volume:,.3f} {r.unit}"),
            ("Coarse Aggregate", f"{r.aggregate_volume:,.3f} {r.unit}"),
        ]
        row = self._rows(self.result_frame, quantity_rows, row)

        self._section(self.result_frame, "Material Cost Build-up", row)
        row += 1
        if self.analysis:
            material_rows = [
                (
                    item["name"],
                    (
                        f"{item['quantity']:,.3f} {item['unit']} × "
                        f"PKR {item['rate']:,.2f} = "
                        f"PKR {item['amount']:,.2f}"
                    ),
                )
                for item in self.analysis["materials"]
            ]
            row = self._rows(self.result_frame, material_rows, row)
            row = self._rows(
                self.result_frame,
                [("Material Total", f"PKR {self.analysis['material_total']:,.2f}")],
                row,
                bold=True,
            )
        else:
            row = self._rows(
                self.result_frame,
                [("Status", "Enter material rates to calculate cost.")],
                row,
            )

        self._section(self.result_frame, "Labour Cost Build-up", row)
        row += 1
        if self.analysis:
            labour_rows = [
                (
                    item["name"],
                    (
                        f"{item['quantity']:,.2f} {item['unit']} × "
                        f"PKR {item['rate']:,.2f} = "
                        f"PKR {item['amount']:,.2f}"
                    ),
                )
                for item in self.analysis["labour"]
            ]
            row = self._rows(self.result_frame, labour_rows, row)
            row = self._rows(
                self.result_frame,
                [("Labour Total", f"PKR {self.analysis['labour_total']:,.2f}")],
                row,
                bold=True,
            )
        else:
            row = self._rows(
                self.result_frame,
                [("Status", "Enter labour rates/productivity to calculate cost.")],
                row,
            )

        self._section(self.result_frame, "Final Cost", row)
        row += 1
        if self.analysis:
            final_rows = [
                ("Quantity", f"{self.analysis['quantity']:,.3f} {self.analysis['unit']}"),
                ("Total Cost", f"PKR {self.analysis['total_cost']:,.2f}"),
                ("Unit Rate", f"PKR {self.analysis['unit_rate']:,.2f} / {self.result.unit}"),
            ]
            row = self._rows(
                self.result_frame,
                final_rows,
                row,
                bold=True,
            )

        ctk.CTkLabel(
            self.result_frame,
            text=(
                "Generate BOQ is always available in the fixed action bar "
                "above. BOQ stores dimensions and physical material/labour "
                "quantities; cost build-up remains in detailed analysis."
            ),
            justify="left",
            anchor="w",
            wraplength=520,
        ).grid(
            row=row,
            column=0,
            columnspan=2,
            padx=14,
            pady=(18, 12),
            sticky="ew",
        )

    def _rows(self, parent, rows, start_row, bold=False):
        row = start_row
        value_font = ctk.CTkFont(weight="bold") if bold else None

        for label, value in rows:
            ctk.CTkLabel(
                parent,
                text=label,
                anchor="w",
                font=value_font,
            ).grid(
                row=row,
                column=0,
                padx=(14, 10),
                pady=5,
                sticky="w",
            )
            ctk.CTkLabel(
                parent,
                text=value,
                anchor="w",
                justify="left",
                font=value_font,
            ).grid(
                row=row,
                column=1,
                padx=(10, 14),
                pady=5,
                sticky="ew",
            )
            row += 1
        return row

    # =========================================================
    # BOQ
    # =========================================================

    def generate_boq(self):
        if self.result is None:
            messagebox.showwarning("PCC → BOQ", "Please calculate PCC first.", parent=self)
            return

        try:
            analysis = self._try_build_analysis()
            if analysis is None:
                raise ValueError("Please enter all material and labour rates/productivity values before adding to BOQ.")

            project = CurrentProject.get()
            if project is None or getattr(project, "id", None) is None:
                raise ValueError("Please select/open a project before generating BOQ.")

            context = self.application_context
            if context is None:
                raise ValueError("Application context is not available.")

            controller = context.boq_controller
            existing = controller.get_by_project(project.id) or []
            highest = 0
            for item in existing:
                value = str(getattr(item, "item_no", "")).upper()
                if value.startswith("PCC-"):
                    try:
                        highest = max(highest, int(value.split("-", 1)[1]))
                    except (ValueError, IndexError):
                        pass

            item_no = f"PCC-{highest + 1:02d}"
            dimensions = analysis["dimensions"]
            remarks = (
                f"Detailed PCC analysis | "
                f"L={dimensions['length']:.3f} {dimensions['dimension_unit']}, "
                f"W={dimensions['width']:.3f} {dimensions['dimension_unit']}, "
                f"T={dimensions['height']:.3f} {dimensions['dimension_unit']} | "
                f"Mix={analysis['mix_ratio']} | "
                f"Material={analysis['material_total']:,.2f} | "
                f"Labour={analysis['labour_total']:,.2f}"
            )

            boq = BOQ(
                project_id=project.id,
                item_no=item_no,
                description=f"PCC ({analysis['mix_ratio']})",
                unit=analysis["unit"],
                quantity=analysis["quantity"],
                rate=analysis["unit_rate"],
                amount=analysis["total_cost"],
                remarks=remarks,
            )

            boq_id = controller.create(boq)
            context.estimate_analysis_service.save(
                project_id=project.id,
                boq_id=int(boq_id),
                calculator_type="PCC",
                analysis=analysis,
            )

            self.analysis = analysis
            self.show_result()
            self.action_status.configure(text=f"BOQ {item_no} added successfully")
            messagebox.showinfo(
                "PCC → BOQ",
                (
                    "Detailed PCC BOQ entry created successfully.\n\n"
                    f"Item: {item_no}\n"
                    f"Dimensions: L {dimensions['length']:.3f} × W {dimensions['width']:.3f} × T {dimensions['height']:.3f} {dimensions['dimension_unit']}\n"
                    f"Quantity: {analysis['quantity']:,.3f} {analysis['unit']}\n"
                    f"Material Cost: PKR {analysis['material_total']:,.2f}\n"
                    f"Labour Cost: PKR {analysis['labour_total']:,.2f}\n"
                    f"Total Cost: PKR {analysis['total_cost']:,.2f}\n"
                    f"Unit Rate: PKR {analysis['unit_rate']:,.2f} / m³"
                ),
                parent=self,
            )
        except Exception as ex:
            messagebox.showerror("PCC → BOQ Error", str(ex), parent=self)

    # =========================================================
    # RESET / EXPORT COMPATIBILITY
    # =========================================================

    def reset_form(self):
        self.vars["length"].set("")
        self.vars["width"].set("")
        self.vars["height"].set("")
        self._last_volume_unit = "m³"
        self.vars["volume_unit"].set("m³")
        self._on_unit_change()
        self.vars["mix_ratio"].set("1:2:4")
        self.vars["cement_bag_rate"].set("0")
        self.vars["sand_rate"].set("0")
        self.vars["aggregate_rate"].set("0")
        self.vars["skilled_productivity"].set("1.00")
        self.vars["skilled_rate"].set("0")
        self.vars["unskilled_productivity"].set("2.00")
        self.vars["unskilled_rate"].set("0")
        self.result = None
        self.analysis = None
        self.action_status.configure(text="Ready")
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        self.after(100, lambda: self.length_entry.focus_set())

    def generate_material(self):
        if self.result is None:
            messagebox.showwarning("PCC Material", "Please calculate pcc first.", parent=self)
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
                "PCC Material",
                "Material quantities added to the project material schedule.\n\n"
                + ("\n".join(lines) if lines else "No material records generated.")
                + "\n\nUse Materials / BOQ → Material Report for the consolidated report.",
                parent=self,
            )
        except Exception as ex:
            messagebox.showerror("PCC Material Error", str(ex), parent=self)
    def export_result(self):
        if self.result is None:
            messagebox.showwarning("Export", "Please calculate PCC first.", parent=self)
            return
        messagebox.showinfo("Export", "Use Reports / BOQ Export for the final Excel and PDF report.", parent=self)

    def has_result(self):
        return self.result is not None
