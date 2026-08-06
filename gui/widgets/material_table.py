from __future__ import annotations

import customtkinter as ctk
from tkinter import ttk


class MaterialTable(ctk.CTkFrame):
    """
    Professional Material Table Widget
    """

    def __init__(
        self,
        master,
        on_double_click=None,
        on_selection_changed=None,
        **kwargs,
    ):

        super().__init__(master, **kwargs)

        self.on_double_click = on_double_click
        self.on_selection_changed = on_selection_changed

        self._items = []
        self._reverse = False

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        columns = (
            "material_name",
            "unit",
            "quantity",
            "rate",
            "amount",
        )

        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        headings = {

            "material_name": "Material",

            "unit": "Unit",

            "quantity": "Qty",

            "rate": "Rate",

            "amount": "Amount",
        }

        widths = {

            "material_name": 320,

            "unit": 90,

            "quantity": 110,

            "rate": 120,

            "amount": 140,
        }

        for column in columns:

            self.tree.heading(
                column,
                text=headings[column],
                command=lambda c=column: self.sort(c),
            )

            self.tree.column(
                column,
                width=widths[column],
                anchor="center",
            )

        y_scroll = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview,
        )

        x_scroll = ttk.Scrollbar(
            self,
            orient="horizontal",
            command=self.tree.xview,
        )

        self.tree.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
        )

        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        y_scroll.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        x_scroll.grid(
            row=1,
            column=0,
            sticky="ew",
        )

        self.tree.bind(
            "<Double-1>",
            self._double_click,
        )

        self.tree.bind(
            "<<TreeviewSelect>>",
            self._selection_changed,
        )

        footer = ctk.CTkFrame(self)

        footer.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(8, 0),
        )

        self.total_label = ctk.CTkLabel(
            footer,
            text="Grand Total : 0.00",
            font=ctk.CTkFont(
                size=15,
                weight="bold",
            ),
        )

        self.total_label.pack(
            side="right",
            padx=10,
            pady=6,
        )

    # =====================================================

    def load_items(self, items):

        self.clear()

        self._items = list(items)

        total = 0.0

        for index, item in enumerate(self._items):

            self.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(

                    item.material_name,

                    item.unit,

                    f"{item.quantity:,.2f}",

                    f"{item.rate:,.2f}",

                    f"{item.amount:,.2f}",
                ),
            )

            total += item.amount

        self.total_label.configure(
            text=f"Grand Total : {total:,.2f}"
        )

    # =====================================================

    def clear(self):

        self.tree.delete(
            *self.tree.get_children()
        )

        self._items.clear()

        self.total_label.configure(
            text="Grand Total : 0.00"
        )

    # =====================================================

    def refresh(self, items):

        self.load_items(items)

    # =====================================================

    def selected_item(self):

        selected = self.tree.selection()

        if not selected:
            return None

        index = int(selected[0])

        if index >= len(self._items):
            return None

        return self._items[index]

    # =====================================================

    def project_total(self):

        return sum(
            item.amount
            for item in self._items
        )

    # =====================================================

    def item_count(self):

        return len(self._items)

    # =====================================================

    def focus_first(self):

        rows = self.tree.get_children()

        if rows:

            self.tree.selection_set(rows[0])

            self.tree.focus(rows[0])

    # =====================================================

    def sort(self, column):

        rows = [
            (
                self.tree.set(item, column),
                item,
            )
            for item in self.tree.get_children("")
        ]

        rows.sort(
            reverse=self._reverse,
        )

        for index, (_, item) in enumerate(rows):

            self.tree.move(
                item,
                "",
                index,
            )

        self._reverse = not self._reverse

    # =====================================================

    def _double_click(self, _):

        if self.on_double_click:

            item = self.selected_item()

            if item:

                self.on_double_click(item)

    # =====================================================

    def _selection_changed(self, _):

        if self.on_selection_changed:

            item = self.selected_item()

            if item:

                self.on_selection_changed(item)