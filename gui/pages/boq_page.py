from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox

from gui.widgets.boq_toolbar import BOQToolbar
from gui.widgets.boq_table import BOQTable
from gui.forms.boq_form import BOQForm


class BOQPage(ctk.CTkFrame):
    """
    BOQ Management Page

    Coordinates:
        • Toolbar
        • Table
        • Form
        • Controller
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

    # =========================================================
    def search(self, keyword):
    
            keyword = keyword.strip()
    
            if keyword == "":
    
                self.refresh()
    
                return
    
            items = self.controller.search(keyword)
    
            if self.project_id is not None:
    
                items = [
                    i
                    for i in items
                    if i.project_id == self.project_id
                ]
    
            self.table.load_items(items)
    
    def new_item(self):

            form = BOQForm(self)
            if self.project_id is not None:
             form.project_id.set(self.project_id)

            self.wait_window(form)

            if form.result is None:
             return

            try:

             self.controller.create(form.result)

             self.refresh()

             messagebox.showinfo(
            "BOQ",
            "BOQ Item Saved Successfully."
        )

            except Exception as ex:

              messagebox.showerror(
             "BOQ Error",
             str(ex)
        )

    def _create_toolbar(self):

        self.toolbar = BOQToolbar(
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
            self.search
        )

    # =========================================================

    def _create_table(self):

        self.table = BOQTable(
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

    # =========================================================

    def refresh(self):

        if self.project_id is None:

            items = self.controller.get_all()

        else:

            items = self.controller.get_by_project(
                self.project_id
            )

        self.table.load_items(items)

    # =========================================================

    def search(self, keyword):

        keyword = keyword.strip()

        if keyword == "":

            self.refresh()

            return

        items = self.controller.search(keyword)

        if self.project_id is not None:

            items = [
                i
                for i in items
                if i.project_id == self.project_id
            ]

        self.table.load_items(items)

   
    def edit_item(self, item=None):

        if item is None:

            item = self.table.selected_item()

        if item is None:

            messagebox.showwarning(
                "BOQ",
                "Please select a BOQ item.",
            )

            return

        form = BOQForm(
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

    # =========================================================

    def delete_item(self):

        item = self.table.selected_item()

        if item is None:

            messagebox.showwarning(
                "BOQ",
                "Please select a BOQ item.",
            )

            return

        if not messagebox.askyesno(
            "Delete BOQ Item",
            f"Delete '{item.description}' ?",
        ):
            return

        self.controller.delete(item.id)

        self.refresh()

    # =========================================================

    def export_excel(self):

        messagebox.showinfo(
            "BOQ",
            "Excel export will be implemented in Reports Module.",
        )

    # =========================================================

    def print_report(self):

        messagebox.showinfo(
            "BOQ",
            "Printing will be implemented in Reports Module.",
        )

    # =========================================================

    def total_items(self):

        return self.table.item_count()

    # =========================================================

    def grand_total(self):

        return self.table.project_total()