"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Report Page
Purpose   : Central BOQ report management and file access
Version   : 4.0.1
=========================================================
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

from core.current_project import CurrentProject


class ReportPage(ctk.CTkFrame):
    """Professional report centre for the active project."""

    EXPORT_FOLDER = Path("exports")

    def __init__(self, master, context):
        super().__init__(master, corner_radius=0)
        self.context = context

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.project_label = None
        self.summary_label = None
        self.files_frame = None

        self._build_header()
        self._build_actions()
        self._build_files_panel()
        self.refresh()

    # =====================================================
    # UI
    # =====================================================

    def _build_header(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame,
            text="Reports",
            font=ctk.CTkFont(size=26, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(14, 2))

        self.project_label = ctk.CTkLabel(
            frame,
            text="No project selected",
            anchor="w",
            font=ctk.CTkFont(size=14),
        )
        self.project_label.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 14))

    def _build_actions(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        buttons = [
            ("Export Excel", self.export_excel),
            ("Print / PDF", self.export_pdf),
            ("Export Both", self.export_both),
            ("Refresh", self.refresh),
        ]

        for column, (text, command) in enumerate(buttons):
            button = ctk.CTkButton(
                frame,
                text=text,
                height=40,
                command=command,
            )
            button.grid(row=0, column=column, padx=8, pady=12, sticky="ew")
            frame.grid_columnconfigure(column, weight=1)

    def _build_files_panel(self):
        summary = ctk.CTkFrame(self)
        summary.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        summary.grid_columnconfigure(0, weight=1)

        self.summary_label = ctk.CTkLabel(
            summary,
            text="",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.summary_label.grid(row=0, column=0, sticky="ew", padx=15, pady=10)

        outer = ctk.CTkFrame(self)
        outer.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 20))
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            outer,
            text="Generated Reports",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(12, 8))

        self.files_frame = ctk.CTkScrollableFrame(outer)
        self.files_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.files_frame.grid_columnconfigure(0, weight=1)

    # =====================================================
    # DATA
    # =====================================================

    def _get_project(self):
        project = CurrentProject.get()
        if project is None:
            raise ValueError("Please select/open a project first.")

        if getattr(project, "id", None) is None:
            raise ValueError("The active project has no valid ID.")

        return project

    def _get_data(self):
        project = self._get_project()
        items = self.context.boq_controller.get_by_project(project.id)

        if not items:
            raise ValueError("The current project has no BOQ items.")

        return project, items

    # =====================================================
    # REPORT GENERATION
    # =====================================================

    def export_excel(self):
        self._generate("excel")

    def export_pdf(self):
        self._generate("pdf")

    def export_both(self):
        self._generate("both")

    def _generate(self, report_type: str):
        try:
            project, items = self._get_data()
            service = self.context.report_service

            if report_type == "excel":
                path = service.generate_excel(project, items)
                message = f"Excel report generated successfully.\n\n{path}"
            elif report_type == "pdf":
                path = service.generate_pdf(project, items)
                message = f"PDF report generated successfully.\n\n{path}"
            else:
                excel_path, pdf_path = service.generate_both(project, items)
                message = (
                    "Excel and PDF reports generated successfully.\n\n"
                    f"Excel:\n{excel_path}\n\nPDF:\n{pdf_path}"
                )

            self.refresh()
            messagebox.showinfo("Reports", message, parent=self)

        except Exception as ex:
            messagebox.showerror("Report Error", str(ex), parent=self)

    # =====================================================
    # FILE LIST
    # =====================================================

    def refresh(self):
        project = CurrentProject.get()

        if project is None:
            self.project_label.configure(text="No project selected")
            self.summary_label.configure(text="Select a project to generate reports.")
        else:
            project_name = getattr(project, "project_name", "") or "Unnamed Project"
            project_code = getattr(project, "project_code", "") or "-"
            self.project_label.configure(
                text=f"Active Project: {project_code} - {project_name}"
            )

            project_id = getattr(project, "id", None)
            try:
                items = (
                    self.context.boq_controller.get_by_project(project_id)
                    if project_id is not None
                    else []
                )
                total = round(sum(float(getattr(i, "amount", 0) or 0) for i in items), 2)
                self.summary_label.configure(
                    text=f"BOQ Items: {len(items)}    |    Grand Total: PKR {total:,.2f}"
                )
            except Exception as ex:
                self.summary_label.configure(text=f"Unable to load BOQ summary: {ex}")

        self._refresh_file_list()

    def _refresh_file_list(self):
        for child in self.files_frame.winfo_children():
            child.destroy()

        self.EXPORT_FOLDER.mkdir(parents=True, exist_ok=True)
        files = sorted(
            [p for p in self.EXPORT_FOLDER.iterdir() if p.is_file()],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        if not files:
            ctk.CTkLabel(
                self.files_frame,
                text="No reports have been generated yet.",
            ).grid(row=0, column=0, padx=15, pady=20, sticky="w")
            return

        for row, path in enumerate(files):
            size_kb = path.stat().st_size / 1024
            row_frame = ctk.CTkFrame(self.files_frame)
            row_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=4)
            row_frame.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                row_frame,
                text=f"{path.name}  ({size_kb:.1f} KB)",
                anchor="w",
            ).grid(row=0, column=0, sticky="ew", padx=12, pady=8)

            ctk.CTkButton(
                row_frame,
                text="Open",
                width=80,
                command=lambda p=path: self._open_file(p),
            ).grid(row=0, column=1, padx=(5, 10), pady=6)

    @staticmethod
    def _open_file(path: Path):
        try:
            path = path.resolve()
            if not path.exists():
                raise FileNotFoundError(path)

            if sys.platform.startswith("win"):
                os.startfile(str(path))
            elif sys.platform == "darwin":
                os.system(f'open "{path}"')
            else:
                os.system(f'xdg-open "{path}"')
        except Exception as ex:
            messagebox.showerror("Open Report", str(ex))


__all__ = ["ReportPage"]
