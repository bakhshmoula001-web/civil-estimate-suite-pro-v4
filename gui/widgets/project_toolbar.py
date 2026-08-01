from __future__ import annotations

import customtkinter as ctk
from typing import Callable, Optional


class ProjectToolbar(ctk.CTkFrame):
    """
    Professional Toolbar for Project Module
    """

    def __init__(
        self,
        master,
        on_new: Optional[Callable] = None,
        on_edit: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        on_refresh: Optional[Callable] = None,
        on_open_boq: Optional[Callable] = None,
        on_search: Optional[Callable[[str], None]] = None,
        **kwargs,
    ):
        super().__init__(master, corner_radius=8, **kwargs)

        self._search_callback = on_search

        self.grid_columnconfigure(6, weight=1)

        self.search_var = ctk.StringVar()

        self._create_buttons(
            on_new,
            on_edit,
            on_delete,
            on_refresh,
            on_open_boq,
        )

        self._create_search()

    # ---------------------------------------------------------

    def _create_buttons(
        self,
        on_new,
        on_edit,
        on_delete,
        on_refresh,
        on_open_boq,
    ):

        buttons = [

            ("➕ New", on_new),

            ("✏ Edit", on_edit),

            ("🗑 Delete", on_delete),

            ("🔄 Refresh", on_refresh),

            ("📋 Open BOQ", on_open_boq),

        ]

        for column, (text, command) in enumerate(buttons):

            btn = ctk.CTkButton(
                self,
                text=text,
                width=120,
                height=36,
                command=command,
            )

            btn.grid(
                row=0,
                column=column,
                padx=(6, 4),
                pady=8,
            )

    # ---------------------------------------------------------

    def _create_search(self):

        self.search_entry = ctk.CTkEntry(
            self,
            width=300,
            textvariable=self.search_var,
            placeholder_text="Search Project...",
        )

        self.search_entry.grid(
            row=0,
            column=6,
            padx=(15, 10),
            pady=8,
            sticky="e",
        )

        self.search_var.trace_add(
            "write",
            self._search_changed,
        )

    # ---------------------------------------------------------

    def _search_changed(self, *_):

        if self._search_callback is None:
            return

        self._search_callback(
            self.search_var.get().strip()
        )

    # ---------------------------------------------------------

    def clear_search(self):

        self.search_var.set("")

    # ---------------------------------------------------------

    def focus_search(self):

        self.search_entry.focus()

    # ---------------------------------------------------------

    def get_search_text(self):

        return self.search_var.get().strip()

    # ---------------------------------------------------------

    def set_search_callback(
        self,
        callback,
    ):

        self._search_callback = callback

        return self