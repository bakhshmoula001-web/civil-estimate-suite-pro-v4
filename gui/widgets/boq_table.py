from __future__ import annotations

import customtkinter as ctk
from tkinter import ttk


class BOQTable(ctk.CTkFrame):
    """Engineer-focused BOQ table.

    The primary BOQ view records quantities and calculation inputs, not
    monetary totals. Material and labour columns show physical quantities
    only. Detailed rates/costs remain in the saved estimate analysis and are
    used by the final cost/report modules.
    """

    def __init__(self, master, on_double_click=None, on_selection_changed=None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_double_click = on_double_click
        self.on_selection_changed = on_selection_changed
        self._items = []
        self._analyses = {}
        self._reverse = False

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        columns = ("item_no", "description", "dimensions", "unit", "quantity", "material", "labour")
        style = ttk.Style()
        try:
            style.configure("BOQ.Treeview", rowheight=48, font=("Segoe UI", 9))
            style.configure("BOQ.Treeview.Heading", font=("Segoe UI", 9, "bold"))
            self.tree_style = "BOQ.Treeview"
        except Exception:
            self.tree_style = "Treeview"
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse", height=14, style=self.tree_style)

        headings = {
            "item_no": "Item No",
            "description": "Work Item",
            "dimensions": "Dimensions",
            "unit": "Unit",
            "quantity": "Qty",
            "material": "Material Quantity",
            "labour": "Labour Quantity",
        }
        widths = {
            "item_no": 82,
            "description": 180,
            "dimensions": 210,
            "unit": 58,
            "quantity": 88,
            "material": 260,
            "labour": 230,
        }

        for column in columns:
            self.tree.heading(column, text=headings[column], command=lambda c=column: self.sort(c))
            self.tree.column(column, width=widths[column], anchor="center")

        y_scroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.tree.configure(height=14)
        self.tree.tag_configure("odd", background="#F7FAFC")
        self.tree.tag_configure("even", background="#FFFFFF")
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        self.tree.bind("<Double-1>", self._double_click)
        self.tree.bind("<<TreeviewSelect>>", self._selection_changed)

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.summary_label = ctk.CTkLabel(
            footer,
            text="BOQ Items: 0",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.summary_label.pack(side="right", padx=10, pady=6)

    @staticmethod
    def _parse_analysis(item):
        """Read detailed analysis saved by the PCC workflow.

        The BOQ model keeps the monetary rate/amount internally for reports,
        but this table deliberately exposes physical material/labour quantities
        only.
        """
        analysis = getattr(item, "_estimate_analysis", None)
        if isinstance(analysis, dict):
            return analysis
        return {}

    @staticmethod
    def _dimensions(item, analysis):
        dimensions = analysis.get("dimensions") if isinstance(analysis, dict) else None
        if isinstance(dimensions, dict):
            length = dimensions.get("length")
            width = dimensions.get("width")
            height = dimensions.get("height")
            unit = dimensions.get("dimension_unit", "m")
            if length is not None and width is not None and height is not None:
                return f"L={float(length):,.3f} {unit} × W={float(width):,.3f} {unit} × T={float(height):,.3f} {unit}"
        return "—"

    @staticmethod
    def _material_quantities(analysis):
        materials = analysis.get("materials", []) if isinstance(analysis, dict) else []
        if not materials:
            return "—"
        return "\n".join(
            f"{m.get('name', 'Material')}: {float(m.get('quantity', 0)):,.3f} {m.get('unit', '')}"
            for m in materials
        )

    @staticmethod
    def _labour_quantities(analysis):
        labour = analysis.get("labour", []) if isinstance(analysis, dict) else []
        if not labour:
            return "—"
        return "\n".join(
            f"{m.get('name', 'Labour')}: {float(m.get('quantity', 0)):,.2f} {m.get('unit', '')}"
            for m in labour
        )

    def load_items(self, items, analyses=None):
        self.clear()
        self._items = list(items)
        self._analyses = dict(analyses or {})
        for index, item in enumerate(self._items):
            analysis = self._analyses.get(getattr(item, "id", None), {})
            if not analysis:
                analysis = self._parse_analysis(item)
            self.tree.insert(
                "", "end", iid=str(index),
                values=(
                    item.item_no,
                    item.description,
                    self._dimensions(item, analysis),
                    item.unit,
                    f"{float(item.quantity):,.3f}",
                    self._material_quantities(analysis),
                    self._labour_quantities(analysis),
                ),
                tags=("odd" if index % 2 else "even",),
            )
        self.summary_label.configure(text=f"BOQ Items: {len(self._items)}")

    def clear(self):
        self.tree.delete(*self.tree.get_children())
        self._items.clear()
        self._analyses.clear()
        self.summary_label.configure(text="BOQ Items: 0")

    def refresh(self, items):
        self.load_items(items)

    def selected_item(self):
        selected = self.tree.selection()
        if not selected:
            return None
        index = int(selected[0])
        if index >= len(self._items):
            return None
        return self._items[index]

    def project_total(self):
        # Kept for controller compatibility. Cost remains an internal model/report value.
        return sum(float(getattr(item, "amount", 0) or 0) for item in self._items)

    def item_count(self):
        return len(self._items)

    def focus_first(self):
        rows = self.tree.get_children()
        if rows:
            self.tree.selection_set(rows[0])
            self.tree.focus(rows[0])

    def sort(self, column):
        rows = [(self.tree.set(item, column), item) for item in self.tree.get_children("")]
        rows.sort(reverse=self._reverse)
        for index, (_, item) in enumerate(rows):
            self.tree.move(item, "", index)
        self._reverse = not self._reverse

    def _double_click(self, _event):
        if self.on_double_click:
            item = self.selected_item()
            if item:
                self.on_double_click(item)

    def _selection_changed(self, _event):
        if self.on_selection_changed:
            item = self.selected_item()
            if item:
                self.on_selection_changed(item)
