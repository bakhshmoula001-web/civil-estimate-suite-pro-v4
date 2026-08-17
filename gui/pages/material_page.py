from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox

from core.current_project import CurrentProject

from gui.widgets.material_toolbar import MaterialToolbar
from gui.widgets.material_table import MaterialTable
from gui.forms.material_form import MaterialForm


class MaterialPage(ctk.CTkFrame):
    """
    Material Management Page
    """

    def __init__(
        self,
        master,
        controller,
        project_id: int | None = None,
    ):
        super().__init__(master)

        self.controller = controller
        self.project_id = project_id

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._create_table()
        self._create_toolbar()

        self.refresh()

    # =====================================================
    # SEARCH
    # =====================================================

    def search(self, keyword):

        keyword = keyword.strip()

        if keyword == "":
            self.refresh()
            return

        items = self.controller.search(keyword)

        if self.project_id is not None:

            items = [
                item
                for item in items
                if item.project_id == self.project_id
            ]

        self.table.load_items(items)

    # =====================================================
    # NEW
    # =====================================================

    def new_item(self):

        project = CurrentProject.get()

        if project is None:

            messagebox.showwarning(
                "Material",
                "Please select a project first.",
            )

            return

        form = MaterialForm(self)

        self.wait_window(form)

        if form.result is None:
            return

        try:

            self.controller.create(form.result)

            self.refresh()

            messagebox.showinfo(
                "Material",
                "Material saved successfully.",
            )

        except Exception as ex:

            messagebox.showerror(
                "Material Error",
                str(ex),
            )
        # =====================================================
    # TOOLBAR
    # =====================================================

    def _create_toolbar(self):

        self.toolbar = MaterialToolbar(
            self,
            on_new=self.new_item,
            on_edit=self.edit_item,
            on_delete=self.delete_item,
            on_refresh=self.refresh,
            on_export=self.export_excel,
            on_print=self.print_report,
        )

        self.toolbar.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=(10, 5),
        )

        self.toolbar.set_search_callback(
            self.search,
        )

    # =====================================================
    # TABLE
    # =====================================================

    def _create_table(self):

        self.table = MaterialTable(
            self,
            on_double_click=self.edit_item,
        )

        self.table.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10),
        )

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(self):

        project = CurrentProject.get()

        if project is None:

            self.table.load_items([])
            return

        items = self.controller.get_by_project(
            project.id
        )

        self.table.load_items(items)
        # =====================================================
    # EDIT
    # =====================================================

    def edit_item(self, item=None):

        if item is None:
            item = self.table.selected_item()

        if item is None:

            messagebox.showwarning(
                "Material",
                "Please select a material.",
            )

            return

        form = MaterialForm(
            self,
            item,
        )

        self.wait_window(form)

        if form.result is None:
            return

        self.controller.update(
            item.id,
            form.result,
        )

        self.refresh()

    # =====================================================
    # DELETE
    # =====================================================

    def delete_item(self):

        item = self.table.selected_item()

        if item is None:

            messagebox.showwarning(
                "Material",
                "Please select a material.",
            )

            return

        if not messagebox.askyesno(

            "Delete Material",

            f"Delete '{item.material_name}' ?",
        ):
            return

        self.controller.delete(item.id)

        self.refresh()

    # =====================================================
    # PLACEHOLDERS
    # =====================================================

    def export_excel(self):

        messagebox.showinfo(
            "Material",
            "Excel export will be implemented in Reports Module.",
        )

    def print_report(self):

        messagebox.showinfo(
            "Material",
            "Printing will be implemented in Reports Module.",
        )

    def total_items(self):

        return self.table.item_count()

    def grand_total(self):

        return self.table.project_total()