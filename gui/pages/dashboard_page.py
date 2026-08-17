"""
Civil Estimate Suite Pro v4.0
Dashboard - Engineer Project Summary
"""
from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox

from app.application_context import ApplicationContext
from core.current_project import CurrentProject
from gui.widgets.stat_card import StatCard
from reports.material_report_service import MaterialReportService


class DashboardPage(ctk.CTkFrame):
    """Engineer-focused project dashboard with material requirements."""

    def __init__(self, master, context: ApplicationContext, **kwargs):
        super().__init__(master, **kwargs)
        self.context = context

        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._create_header()
        self._create_summary_cards()
        self._create_material_panel()
        self._create_recent_projects()
        self.refresh()

    def _create_header(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=0, columnspan=3, padx=20, pady=(18, 8), sticky="ew")
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame, text="Engineer Dashboard",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        self.project_label = ctk.CTkLabel(frame, text="No active project", anchor="e")
        self.project_label.grid(row=0, column=1, padx=10, sticky="e")

    def _create_summary_cards(self):
        self.project_card = StatCard(self, title="Projects", value="0")
        self.project_card.grid(row=1, column=0, padx=(15, 7), pady=8, sticky="nsew")

        self.boq_card = StatCard(self, title="BOQ Items", value="0")
        self.boq_card.grid(row=1, column=1, padx=7, pady=8, sticky="nsew")

        self.cost_card = StatCard(self, title="Estimated Cost", value="PKR 0")
        self.cost_card.grid(row=1, column=2, padx=(7, 15), pady=8, sticky="nsew")

    def _create_material_panel(self):
        panel = ctk.CTkFrame(self, corner_radius=10)
        panel.grid(row=2, column=0, columnspan=3, padx=15, pady=8, sticky="ew")
        panel.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(panel, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 4))
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top, text="Current Project Material Requirement",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            top, text="Generate Material Report", width=190,
            command=self.generate_material_report,
        ).grid(row=0, column=1, padx=5)

        self.material_text = ctk.CTkTextbox(panel, height=150)
        self.material_text.grid(row=1, column=0, padx=14, pady=(4, 12), sticky="ew")
        self.material_text.configure(state="disabled")

    def _create_recent_projects(self):
        frame = ctk.CTkFrame(self, corner_radius=10)
        frame.grid(row=3, column=0, columnspan=3, padx=15, pady=(8, 15), sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame, text="Recent Projects",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(12, 8), sticky="w")

        self.project_list = ctk.CTkTextbox(frame)
        self.project_list.grid(row=1, column=0, padx=20, pady=(0, 18), sticky="nsew")

    def _active_data(self):
        project = CurrentProject.get()
        if project is None:
            return None, [], []

        project_id = getattr(project, "id", None)
        if project_id is None:
            return project, [], []

        items = self.context.boq_service.get_by_project(project_id)
        analyses = self.context.estimate_analysis_service.get_by_project(project_id)
        return project, items, analyses

    def refresh(self):
        try:
            self.project_card.value_label.configure(
                text=str(self.context.project_service.total_projects())
            )
            project, items, analyses = self._active_data()

            if project is None:
                self.project_label.configure(text="No active project")
                self.boq_card.value_label.configure(text="0")
                self.cost_card.value_label.configure(text="PKR 0")
                self._set_material_text("Open a project to see material requirements.")
            else:
                code = str(getattr(project, "project_code", "") or "")
                name = str(getattr(project, "project_name", "") or "")
                self.project_label.configure(text=f"{code} - {name}".strip(" -"))
                self.boq_card.value_label.configure(text=str(len(items)))

                total_cost = 0.0
                if analyses:
                    total_cost = sum(float(a.get("total_cost", 0) or 0) for a in analyses)
                else:
                    total_cost = sum(float(getattr(i, "amount", 0) or 0) for i in items)
                self.cost_card.value_label.configure(text=f"PKR {total_cost:,.2f}")

                material_rows, _labour_rows = MaterialReportService.consolidate(
                    items,
                    analyses,
                )
                if material_rows:
                    lines = [
                        f"{m['name']:<24} {m['quantity']:>14,.3f} {m['unit']}"
                        for m in material_rows
                    ]
                    self._set_material_text("\n".join(lines))
                else:
                    self._set_material_text("No calculator-based material analysis available yet.")

            recent = self.context.project_service.get_recent(10)
            lines = []
            for p in recent:
                code = str(getattr(p, "project_code", "") or "")
                name = str(getattr(p, "project_name", "") or "")
                location = str(getattr(p, "location", "") or "")
                lines.append(f"{code} | {name} | {location}")
            self._set_projects_text("\n".join(lines) if lines else "No projects available.")

        except Exception as ex:
            if self.context.logger:
                self.context.logger.exception(ex)
            self._set_material_text(f"Unable to load material summary: {ex}")

    def _set_material_text(self, text):
        self.material_text.configure(state="normal")
        self.material_text.delete("1.0", "end")
        self.material_text.insert("1.0", text)
        self.material_text.configure(state="disabled")

    def _set_projects_text(self, text):
        self.project_list.configure(state="normal")
        self.project_list.delete("1.0", "end")
        self.project_list.insert("1.0", text)
        self.project_list.configure(state="disabled")

    def generate_material_report(self):
        try:
            project, items, analyses = self._active_data()
            if project is None:
                raise ValueError("Please select/open a project first.")
            if not analyses:
                raise ValueError("No detailed calculator analysis is available for this project.")
            service = MaterialReportService(
                self.context.export_folder
            )
            excel = service.export_excel(
                project,
                items,
                analyses,
            )
            pdf = service.export_pdf(
                project,
                items,
                analyses,
            )
            messagebox.showinfo(
                "Material Requirement Report",
                f"Material report generated successfully.\\n\\nExcel:\\n{excel}\\n\\nPDF:\\n{pdf}",
                parent=self,
            )
        except Exception as ex:
            messagebox.showerror("Material Report Error", str(ex), parent=self)
