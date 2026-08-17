from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox

from core.current_project import CurrentProject
from gui.forms.boq_form import BOQForm
from gui.widgets.boq_table import BOQTable
from gui.widgets.boq_cost_detail import BOQCostDetail
from gui.widgets.boq_toolbar import BOQToolbar
from reports.boq_export_service import BOQExportService
from reports.material_report_service import MaterialReportService


class BOQPage(ctk.CTkFrame):
    """Professional BOQ workspace.

    The page owns only BOQ presentation/layout. Existing controllers,
    calculator analyses and report services remain unchanged.
    """

    def __init__(self, master, controller, project_id=None, context=None):
        super().__init__(master, fg_color="#F5F7FB", corner_radius=0)

        self.controller = controller
        self.project_id = project_id
        self.context = context
        self._analyses = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=5, minsize=240)
        self.grid_rowconfigure(4, weight=3, minsize=190)

        self._build_header()
        self._build_toolbar()
        self._build_summary()
        self._build_table()
        self._build_detail()

        self.refresh()

    def _build_header(self):
        frame = ctk.CTkFrame(self, fg_color="transparent", height=48)
        frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(10, 4))
        frame.grid_propagate(False)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame,
            text="▣  BOQ (Bill of Quantities)",
            text_color="#16233B",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self.project_label = ctk.CTkLabel(
            frame,
            text="No active project",
            text_color="#64748B",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.project_label.grid(row=0, column=1, sticky="e")

    def _build_toolbar(self):
        self.toolbar = BOQToolbar(
            self,
            on_new=self.new_item,
            on_edit=self.edit_item,
            on_delete=self.delete_item,
            on_refresh=self.refresh,
            on_export=self.export_excel,
            on_material_report=self.generate_material_report,
            on_print=self.print_report,
        )
        self.toolbar.configure(
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#D8E1EF",
            corner_radius=10,
            height=56,
        )
        self.toolbar.grid(
            row=1, column=0, sticky="ew",
            padx=16, pady=(0, 8),
        )
        self.toolbar.grid_propagate(False)
        self.toolbar.set_search_callback(self.search)

    def _build_summary(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 8))

        for col in range(4):
            frame.grid_columnconfigure(col, weight=1, uniform="boq_summary")

        self.items_value = self._card(frame, 0, "TOTAL BOQ ITEMS", "0", "#2563EB")
        self.quantity_value = self._card(frame, 1, "TOTAL QUANTITY", "0.000", "#16A34A")
        self.amount_value = self._card(frame, 2, "TOTAL AMOUNT", "PKR 0.00", "#F97316")
        self.updated_value = self._card(frame, 3, "LAST UPDATED", "—", "#7C3AED")

    def _card(self, parent, column, title, value, accent):
        card = ctk.CTkFrame(
            parent, fg_color="#FFFFFF", corner_radius=10,
            border_width=1, border_color="#D8E1EF", height=74,
        )
        card.grid(row=0, column=column, sticky="nsew", padx=4)
        card.grid_propagate(False)
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            card, text="●", width=38, height=38,
            corner_radius=9, fg_color=accent, text_color="#FFFFFF",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, rowspan=2, padx=(10, 8), pady=9)

        ctk.CTkLabel(
            card, text=title, text_color="#64748B",
            font=ctk.CTkFont(size=10, weight="bold"), anchor="w",
        ).grid(row=0, column=1, sticky="sw", padx=(0, 8), pady=(8, 0))

        value_label = ctk.CTkLabel(
            card, text=value, text_color=accent,
            font=ctk.CTkFont(size=18, weight="bold"), anchor="w",
        )
        value_label.grid(row=1, column=1, sticky="nw", padx=(0, 8), pady=(0, 8))
        return value_label

    def _build_table(self):
        frame = ctk.CTkFrame(
            self, fg_color="#FFFFFF", corner_radius=10,
            border_width=1, border_color="#D8E1EF",
        )
        frame.grid(row=3, column=0, sticky="nsew", padx=16, pady=(0, 8))
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.table = BOQTable(
            frame,
            on_double_click=self.edit_item,
            on_selection_changed=self._selection_changed,
            fg_color="transparent",
        )
        self.table.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    def _build_detail(self):
        frame = ctk.CTkFrame(
            self, fg_color="#FFFFFF", corner_radius=10,
            border_width=1, border_color="#D8E1EF",
        )
        frame.grid(row=4, column=0, sticky="nsew", padx=16, pady=(0, 12))
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Use the existing cost-detail widget as-is. Do not pass unsupported
        # constructor options; this keeps the module compatible with v4.0.
        self.detail_panel = BOQCostDetail(frame)
        self.detail_panel.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

    def _project(self):
        return CurrentProject.get()

    def _project_id(self):
        project = self._project()
        if project is not None:
            return getattr(project, "id", None)
        return self.project_id

    def _get_analyses(self, items):
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

    def _update_summary(self, items):
        quantity = sum(float(getattr(i, "quantity", 0) or 0) for i in items)
        amount = sum(float(getattr(i, "amount", 0) or 0) for i in items)

        self.items_value.configure(text=f"{len(items):,}")
        self.quantity_value.configure(text=f"{quantity:,.3f}")
        self.amount_value.configure(text=f"PKR {amount:,.2f}")
        self.updated_value.configure(text="Now" if items else "—")

    def refresh(self):
        try:
            project = self._project()
            project_id = self._project_id()

            if project is not None:
                self.project_label.configure(
                    text=f"{getattr(project, 'project_code', '')}  •  "
                         f"{getattr(project, 'project_name', '')}"
                )
            else:
                self.project_label.configure(text="No active project")

            if project_id is None:
                self._analyses = {}
                self.table.load_items([])
                self.detail_panel.clear()
                self._update_summary([])
                return

            items = self.controller.get_by_project(project_id)
            self._analyses = self._get_analyses(items)
            self.table.load_items(items, self._analyses)
            self.detail_panel.clear()
            self._update_summary(items)

        except Exception as ex:
            messagebox.showerror("BOQ Refresh Error", str(ex), parent=self)

    def search(self, keyword):
        keyword = str(keyword or "").strip()
        if not keyword:
            self.refresh()
            return

        try:
            items = self.controller.search(keyword)
            project_id = self._project_id()
            if project_id is not None:
                items = [
                    item for item in items
                    if getattr(item, "project_id", None) == project_id
                ]

            self._analyses = self._get_analyses(items)
            self.table.load_items(items, self._analyses)
            self.detail_panel.clear()
            self._update_summary(items)
        except Exception as ex:
            messagebox.showerror("BOQ Search Error", str(ex), parent=self)

    def _selection_changed(self, item):
        analysis = self._analyses.get(getattr(item, "id", None), {})
        self.detail_panel.show_item(item, analysis)

    def new_item(self):
        project = self._project()
        if project is None:
            messagebox.showwarning("BOQ", "Please select/open a project first.", parent=self)
            return

        form = BOQForm(self, project=project)
        self.wait_window(form)
        if form.result is None:
            return

        result = form.result
        if getattr(result, "project_id", None) in (None, 0):
            result.project_id = project.id

        try:
            self.controller.create(result)
            self.refresh()
        except Exception as ex:
            messagebox.showerror("BOQ Error", str(ex), parent=self)

    def edit_item(self, item=None):
        item = item or self.table.selected_item()
        if item is None:
            messagebox.showwarning("BOQ", "Please select a BOQ item.", parent=self)
            return

        form = BOQForm(self, item, project=self._project())
        self.wait_window(form)
        if form.result is None:
            return

        try:
            self.controller.update(item.id, form.result)
            self.refresh()
        except Exception as ex:
            messagebox.showerror("BOQ Update Error", str(ex), parent=self)

    def delete_item(self):
        item = self.table.selected_item()
        if item is None:
            messagebox.showwarning("BOQ", "Please select a BOQ item.", parent=self)
            return

        if not messagebox.askyesno(
            "Delete BOQ Item",
            f"Delete {item.item_no} - {item.description}?",
            parent=self,
        ):
            return

        try:
            self.controller.delete(item.id)
            self.refresh()
        except Exception as ex:
            messagebox.showerror("BOQ Delete Error", str(ex), parent=self)

    def _export_data(self):
        project = self._project()
        if project is None or getattr(project, "id", None) is None:
            raise ValueError("Please select/open a project before exporting BOQ.")

        items = self.controller.get_by_project(project.id)
        if not items:
            raise ValueError("The current project has no BOQ items to export.")
        return project, items

    def generate_material_report(self):
        try:
            project, items = self._export_data()
            analyses = self._get_analyses(items)
            if not analyses:
                raise ValueError(
                    "No detailed calculator analysis is available for the current BOQ items."
                )
            excel_path, pdf_path = MaterialReportService().export_both(
                project, items, analyses
            )
            messagebox.showinfo(
                "Material Requirement Report",
                f"Excel:\n{excel_path}\n\nPDF:\n{pdf_path}",
                parent=self,
            )
        except Exception as ex:
            messagebox.showerror("Material Report Error", str(ex), parent=self)

    def export_excel(self):
        try:
            project, items = self._export_data()
            path = BOQExportService().export_excel(project, items)
            messagebox.showinfo("BOQ Excel Export", f"Excel:\n{path}", parent=self)
        except Exception as ex:
            messagebox.showerror("BOQ Excel Export Error", str(ex), parent=self)

    def print_report(self):
        try:
            project, items = self._export_data()
            path = BOQExportService().export_pdf(project, items)
            messagebox.showinfo("BOQ PDF Report", f"PDF:\n{path}", parent=self)
        except Exception as ex:
            messagebox.showerror("BOQ PDF Report Error", str(ex), parent=self)

    def export_both(self):
        try:
            project, items = self._export_data()
            excel_path, pdf_path = BOQExportService().export_both(project, items)
            messagebox.showinfo(
                "BOQ Reports",
                f"Excel:\n{excel_path}\n\nPDF:\n{pdf_path}",
                parent=self,
            )
        except Exception as ex:
            messagebox.showerror("BOQ Report Error", str(ex), parent=self)

    def total_items(self):
        return self.table.item_count()

    def grand_total(self):
        return self.table.project_total()


__all__ = ["BOQPage"]
