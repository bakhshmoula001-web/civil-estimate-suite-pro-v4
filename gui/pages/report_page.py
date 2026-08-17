"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Report Center Page
Purpose   : Central professional report generation
Version   : 4.0.0
=========================================================
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import customtkinter as ctk
from tkinter import messagebox

from core.current_project import CurrentProject
from services.rate_analysis_report_service import RateAnalysisReportService
from services.cost_control_service import CostControlService


class ReportPage(ctk.CTkFrame):
    """Professional central report center for the active project."""

    def __init__(self, master, context):
        super().__init__(master, corner_radius=0)
        self.context = context
        self.export_folder = Path("exports")
        self.rate_analysis_service = RateAnalysisReportService(
    context.export_folder
)
        self.cost_control_service = CostControlService()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        self._create_header()
        self._create_project_card()
        self._create_cost_control_strip()
        self._create_report_cards()
        self._create_action_bar()
        self._create_files_panel()
        self.refresh()

    # =====================================================
    # HEADER
    # =====================================================

    def _create_header(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 6))
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame, text="Report Center",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            frame,
            text="Generate complete BOQ, material, labour and cost reports from the active project.",
            font=ctk.CTkFont(size=13),
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))

    # =====================================================
    # PROJECT SUMMARY
    # =====================================================

    def _create_project_card(self):
        card = ctk.CTkFrame(self)
        card.grid(row=1, column=0, sticky="ew", padx=20, pady=6)
        for col in range(4):
            card.grid_columnconfigure(col, weight=1)

        self.project_code = self._summary_value(card, "Project Code", 0, 0)
        self.project_name = self._summary_value(card, "Project Name", 0, 1)
        self.client_name = self._summary_value(card, "Client Name", 0, 2)
        self.location = self._summary_value(card, "Location", 0, 3)

        self.item_count = self._summary_value(card, "BOQ Items", 1, 0)
        self.material_total = self._summary_value(card, "Material Cost", 1, 1)
        self.labour_total = self._summary_value(card, "Labour Cost", 1, 2)
        self.grand_total = self._summary_value(card, "Grand Total", 1, 3)

    def _summary_value(self, parent, title, row, col):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, sticky="ew", padx=8, pady=7)

        ctk.CTkLabel(
            frame, text=title,
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w",
        ).pack(anchor="w")

        label = ctk.CTkLabel(frame, text="-", anchor="w")
        label.pack(anchor="w", pady=(2, 0))
        return label


    # =====================================================
    # COST CONTROL
    # =====================================================

    def _create_cost_control_strip(self):
        card = ctk.CTkFrame(self)
        card.grid(row=2, column=0, sticky="ew", padx=20, pady=(3, 6))
        for col in range(5):
            card.grid_columnconfigure(col, weight=1)

        ctk.CTkLabel(
            card,
            text="Cost Control",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(
            row=0, column=0, columnspan=5,
            sticky="w", padx=12, pady=(6, 2)
        )

        self.cc_material = self._summary_value(
            card, "Material", 1, 0
        )
        self.cc_skilled = self._summary_value(
            card, "Skilled Labour", 1, 1
        )
        self.cc_unskilled = self._summary_value(
            card, "Unskilled Labour", 1, 2
        )
        self.cc_total = self._summary_value(
            card, "Project Total", 1, 3
        )
        self.cc_status = self._summary_value(
            card, "Analysis Status", 1, 4
        )

    @staticmethod
    def _money(value):
        return f"PKR {float(value or 0):,.2f}"

    # =====================================================
    # REPORT CARDS
    # =====================================================

    def _create_report_cards(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=3, column=0, sticky="ew", padx=20, pady=6)

        for col in range(4):
            container.grid_columnconfigure(col, weight=1)

        cards = [
            (
                "BOQ Report",
                "Physical BOQ with dimensions, quantities, rates and amounts.",
                "Excel",
                self.export_boq_excel,
                "PDF / Print",
                self.export_boq_pdf,
            ),
            (
                "Detailed Estimate",
                "Item-wise material, skilled labour, unskilled labour and total cost analysis.",
                "Excel",
                self.export_detailed_excel,
                "PDF",
                self.export_detailed_pdf,
            ),
            (
                "Material & Labour",
                "Consolidated project-level material and labour requirement schedule.",
                "Excel",
                self.export_material_excel,
                "PDF",
                self.export_material_pdf,
            ),
            (
                "Rate Analysis",
                "Item-wise material, skilled labour, unskilled labour, total cost and unit-rate build-up.",
                "Excel",
                self.export_rate_excel,
                "PDF",
                self.export_rate_pdf,
            ),
        ]

        for col, data in enumerate(cards):
            title, description, b1, c1, b2, c2 = data
            card = ctk.CTkFrame(container)
            card.grid(row=0, column=col, sticky="nsew", padx=6)

            ctk.CTkLabel(
                card, text=title,
                font=ctk.CTkFont(size=16, weight="bold"),
            ).pack(anchor="w", padx=14, pady=(12, 4))

            ctk.CTkLabel(
                card, text=description,
                wraplength=300,
                justify="left",
                anchor="w",
            ).pack(fill="x", padx=14, pady=(0, 10))

            ctk.CTkButton(
                card, text=b1, height=34, command=c1
            ).pack(fill="x", padx=14, pady=4)

            ctk.CTkButton(
                card, text=b2, height=34, command=c2
            ).pack(fill="x", padx=14, pady=(4, 12))

    # =====================================================
    # ACTION BAR
    # =====================================================

    def _create_action_bar(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=4, column=0, sticky="ew", padx=20, pady=6)

        buttons = [
            ("Generate All Reports", self.export_all),
            ("Open Reports Folder", self.open_folder),
            ("Refresh", self.refresh),
        ]

        for i, (text, command) in enumerate(buttons):
            ctk.CTkButton(
                frame, text=text, height=36, command=command
            ).grid(row=0, column=i, padx=7, pady=9)

        self.status = ctk.CTkLabel(frame, text="Ready", anchor="w")
        self.status.grid(row=0, column=3, sticky="ew", padx=15)
        frame.grid_columnconfigure(3, weight=1)

    # =====================================================
    # FILES
    # =====================================================

    def _create_files_panel(self):
        panel = ctk.CTkFrame(self)
        panel.grid(row=5, column=0, sticky="nsew", padx=20, pady=(6, 16))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            panel, text="Generated Reports",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(10, 7))

        self.files_box = ctk.CTkTextbox(panel, wrap="none")
        self.files_box.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 12))
        self.files_box.configure(state="disabled")

    # =====================================================
    # DATA
    # =====================================================

    def _project(self):
        return CurrentProject.get()

    def _items(self):
        project = self._project()
        if project is None or getattr(project, "id", None) is None:
            return []
        return list(self.context.boq_controller.get_by_project(project.id))

    def _analyses(self, items):
        service = getattr(self.context, "estimate_analysis_service", None)
        if service is None:
            return {}

        result = {}
        for item in items:
            item_id = getattr(item, "id", None)
            if item_id is None:
                continue
            try:
                analysis = service.get_by_boq(int(item_id))
            except Exception:
                analysis = None
            if isinstance(analysis, dict):
                result[int(item_id)] = analysis
        return result

    def _load_summary(self):
        project = self._project()
        items = self._items()

        if project is None:
            for label in (
                self.project_code, self.project_name, self.client_name,
                self.location, self.item_count, self.material_total,
                self.labour_total, self.grand_total,
                self.cc_material, self.cc_skilled, self.cc_unskilled,
                self.cc_total, self.cc_status
            ):
                label.configure(text="-")
            return None, [], {}

        analyses = self._analyses(items)

        control = self.cost_control_service.build(items, analyses)

        self.project_code.configure(text=str(getattr(project, "project_code", "")))
        self.project_name.configure(text=str(getattr(project, "project_name", "")))
        self.client_name.configure(text=str(getattr(project, "client_name", "")))
        self.location.configure(text=str(getattr(project, "location", "")))
        self.item_count.configure(text=str(len(items)))

        self.material_total.configure(
            text=self._money(control["material_cost"])
        )
        self.labour_total.configure(
            text=self._money(control["labour_cost"])
        )
        self.grand_total.configure(
            text=self._money(control["grand_total"])
        )

        self.cc_material.configure(
            text=f"{self._money(control['material_cost'])}\n{control['material_percent']:.2f}%"
        )
        self.cc_skilled.configure(
            text=f"{self._money(control['skilled_labour_cost'])}\n{control['skilled_percent']:.2f}%"
        )
        self.cc_unskilled.configure(
            text=f"{self._money(control['unskilled_labour_cost'])}\n{control['unskilled_percent']:.2f}%"
        )
        self.cc_total.configure(
            text=self._money(control["grand_total"])
        )
        self.cc_status.configure(
            text=(
                f"{control['analysed_items']}/{control['boq_items']} analysed\n"
                f"{control['pending_items']} pending"
            )
        )

        return project, items, analyses

    def _get_data(self):
        data = self._load_summary()
        if data[0] is None:
            raise ValueError("Please select/open a project first.")
        if not data[1]:
            raise ValueError("The current project has no BOQ items.")
        return data

    # =====================================================
    # BOQ REPORTS
    # =====================================================

    def export_boq_excel(self):
        try:
            project, items, _ = self._get_data()
            path = self.context.report_service.export_excel(project, items)
            self._done("BOQ Excel generated", path)
        except Exception as exc:
            self._error("BOQ Excel Error", exc)

    def export_boq_pdf(self):
        try:
            project, items, _ = self._get_data()
            path = self.context.report_service.export_pdf(project, items)
            self._done("BOQ PDF generated", path)
        except Exception as exc:
            self._error("BOQ PDF Error", exc)

    # =====================================================
    # DETAILED ESTIMATE
    # =====================================================

    def export_detailed_excel(self):
        try:
            project, items, analyses = self._get_data()
            path = self.context.material_report_service.export_excel(
                project, items, analyses
            )
            self._done("Detailed Estimate Excel generated", path)
        except Exception as exc:
            self._error("Detailed Estimate Excel Error", exc)

    def export_detailed_pdf(self):
        try:
            project, items, analyses = self._get_data()
            path = self.context.material_report_service.export_pdf(
                project, items, analyses
            )
            self._done("Detailed Estimate PDF generated", path)
        except Exception as exc:
            self._error("Detailed Estimate PDF Error", exc)

    # =====================================================
    # MATERIAL / LABOUR
    # =====================================================

    def export_material_excel(self):
        try:
            project, items, analyses = self._get_data()
            path = self.context.material_report_service.export_excel(
                project, items, analyses
            )
            self._done("Material/Labour Excel generated", path)
        except Exception as exc:
            self._error("Material/Labour Excel Error", exc)

    def export_material_pdf(self):
        try:
            project, items, analyses = self._get_data()
            path = self.context.material_report_service.export_pdf(
                project, items, analyses
            )
            self._done("Material/Labour PDF generated", path)
        except Exception as exc:
            self._error("Material/Labour PDF Error", exc)

    # =====================================================
    # RATE ANALYSIS / UNIT RATE
    # =====================================================

    def export_rate_excel(self):
        try:
            project, items, analyses = self._get_data()
            path = self.rate_analysis_service.export_excel(
                project, items, analyses
            )
            self._done("Rate Analysis Excel generated", path)
        except Exception as exc:
            self._error("Rate Analysis Excel Error", exc)

    def export_rate_pdf(self):
        try:
            project, items, analyses = self._get_data()
            path = self.rate_analysis_service.export_pdf(
                project, items, analyses
            )
            self._done("Rate Analysis PDF generated", path)
        except Exception as exc:
            self._error("Rate Analysis PDF Error", exc)

    # =====================================================
    # ALL
    # =====================================================

    def export_all(self):
        try:
            project, items, analyses = self._get_data()

            boq_excel = self.context.report_service.export_excel(project, items)
            boq_pdf = self.context.report_service.export_pdf(project, items)

            detailed_excel = self.context.material_report_service.export_excel(
                project, items, analyses
            )
            detailed_pdf = self.context.material_report_service.export_pdf(
                project, items, analyses
            )

            self._refresh_files()
            self.status.configure(text="All reports generated successfully.")

            messagebox.showinfo(
                "All Reports",
                (
                    "Complete report package generated successfully.\n\n"
                    f"BOQ Excel:\n{boq_excel}\n\n"
                    f"BOQ PDF:\n{boq_pdf}\n\n"
                    f"Detailed Excel:\n{detailed_excel}\n\n"
                    f"Detailed PDF:\n{detailed_pdf}"
                ),
                parent=self,
            )
        except Exception as exc:
            self._error("Report Generation Error", exc)

    # =====================================================
    # HELPERS
    # =====================================================

    def _done(self, text, path):
        self._refresh_files()
        self.status.configure(text=text)
        messagebox.showinfo("Report Center", f"{text}.\n\n{path}", parent=self)

    def _error(self, title, exc):
        self.status.configure(text="Report generation failed.")
        messagebox.showerror(title, str(exc), parent=self)

    def open_folder(self):
        try:
            folder = self.export_folder.resolve()
            folder.mkdir(parents=True, exist_ok=True)
            if os.name == "nt":
                os.startfile(str(folder))
            elif os.name == "posix":
                subprocess.Popen(["xdg-open", str(folder)])
            else:
                raise RuntimeError("Opening the reports folder is not supported.")
        except Exception as exc:
            self._error("Reports Folder Error", exc)

    def _refresh_files(self):
        self.export_folder.mkdir(parents=True, exist_ok=True)
        files = sorted(
            [p for p in self.export_folder.iterdir() if p.is_file()],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        self.files_box.configure(state="normal")
        self.files_box.delete("1.0", "end")

        if not files:
            self.files_box.insert("end", "No reports generated yet.")
        else:
            for path in files:
                size_kb = path.stat().st_size / 1024
                self.files_box.insert(
                    "end",
                    f"{path.name}\t{size_kb:.1f} KB\t{path.resolve()}\n",
                )

        self.files_box.configure(state="disabled")

    def refresh(self):
        try:
            self._load_summary()
            self._refresh_files()
        except Exception as exc:
            if getattr(self.context, "logger", None):
                self.context.logger.warning(
                    f"Report page refresh failed: {exc}"
                )


__all__ = ["ReportPage"]
