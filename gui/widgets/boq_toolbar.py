from __future__ import annotations

import customtkinter as ctk
from typing import Callable, Optional


class BOQToolbar(ctk.CTkFrame):
    """
    Professional reusable toolbar for BOQ Module.
    """

    def __init__(
        self,
        master,
        on_new: Optional[Callable] = None,
        on_edit: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        on_refresh: Optional[Callable] = None,
        on_export: Optional[Callable] = None,
        on_print: Optional[Callable] = None,
        on_search: Optional[Callable[[str], None]] = None,
        **kwargs,
    ):
        super().__init__(master, corner_radius=8, **kwargs)

        self.grid_columnconfigure(6, weight=1)

        self.search_var = ctk.StringVar()

        buttons = [
            ("➕ New", on_new),
            ("✏ Edit", on_edit),
            ("🗑 Delete", on_delete),
            ("🔄 Refresh", on_refresh),
            ("📤 Export", on_export),
            ("🖨 Print", on_print),
        ]

        for column, (text, command) in enumerate(buttons):

            btn = ctk.CTkButton(
                self,
                text=text,
                width=110,
                height=36,
                command=command,
            )

            btn.grid(
                row=0,
                column=column,
                padx=(6, 4),
                pady=8,
            )

        self.search_entry = ctk.CTkEntry(
            self,
            width=300,
            textvariable=self.search_var,
            placeholder_text="Search BOQ Item...",
        )

        self.search_entry.grid(
            row=0,
            column=7,
            padx=(15, 10),
            pady=8,
            sticky="e",
        )

        self.search_var.trace_add(
            "write",
            self._search_changed,
        )

    # --------------------------------------------------

    def _search_changed(self, *_):

        if self.search_var is None:
            return

        if hasattr(self, "_callback"):

            self._callback(
                self.search_var.get().strip()
            )

    # --------------------------------------------------

    def clear_search(self):

        self.search_var.set("")

    # --------------------------------------------------

    def focus_search(self):

        self.search_entry.focus()

    # --------------------------------------------------

    def get_search_text(self):

        return self.search_var.get().strip()

    # --------------------------------------------------

    def set_search_callback(
        self,
        callback,
    ):

        self._callback = callback

        return self