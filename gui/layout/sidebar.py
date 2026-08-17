"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Sidebar
Purpose   : Application Navigation Sidebar
Author    : OpenAI + Moula Bakhsh
Version   : 4.0.0
=========================================================
"""

from __future__ import annotations

import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    """
    Main application navigation sidebar.

    The MainWindow passes its navigation handler through
    ``on_navigate``. Each button calls the instance method
    ``navigate()``, which forwards the selected page to the
    parent application and updates the active button.
    """

    WIDTH = 220

    MENU_ITEMS = [
        ("Dashboard", "dashboard"),
        ("Projects", "projects"),
        ("BOQ", "boq"),
        ("Materials", "materials"),
        ("Rates", "rates"),
        ("Calculators", "calculators"),
        ("Reports", "reports"),
        ("Settings", "settings"),
        ("Backup", "backup"),
    ]

    def __init__(
        self,
        master,
        on_navigate=None,
        **kwargs,
    ):
        super().__init__(
            master,
            width=self.WIDTH,
            corner_radius=0,
            **kwargs,
        )

        self.on_navigate = on_navigate
        self.buttons: dict[str, ctk.CTkButton] = {}

        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        self._create_widgets()

        # Dashboard is the initial page.
        self.select("dashboard")

    # =====================================================
    # Widgets
    # =====================================================

    def _create_widgets(self) -> None:
        row = 0

        for text, page in self.MENU_ITEMS:
            button = ctk.CTkButton(
                self,
                text=text,
                height=40,
                corner_radius=8,
                anchor="w",
                fg_color="transparent",
                hover_color=("gray80", "gray25"),
                command=lambda p=page: self.navigate(p),
            )

            button.grid(
                row=row,
                column=0,
                padx=10,
                pady=5,
                sticky="ew",
            )

            self.buttons[page] = button
            row += 1

        # Spacer
        self.grid_rowconfigure(row, weight=1)
        row += 1

        close_command = getattr(
            self.master,
            "on_close",
            None,
        )

        if not callable(close_command):
            close_command = self.master.winfo_toplevel().destroy

        self.exit_button = ctk.CTkButton(
            self,
            text="Exit",
            height=40,
            corner_radius=8,
            fg_color="#B22222",
            hover_color="#8B0000",
            command=close_command,
        )

        self.exit_button.grid(
            row=row,
            column=0,
            padx=10,
            pady=20,
            sticky="ew",
        )

    # =====================================================
    # Navigation
    # =====================================================

    def navigate(self, page_name: str) -> None:
        """
        Navigate to a page through the callback supplied by
        MainWindow.
        """
        page_name = str(page_name).strip().lower()

        if page_name not in self.buttons:
            return

        self.select(page_name)

        if callable(self.on_navigate):
            self.on_navigate(page_name)

    # =====================================================
    # Selection
    # =====================================================

    def select(self, page_name: str) -> None:
        """
        Highlight the active navigation button.
        """
        page_name = str(page_name).strip().lower()

        for key, button in self.buttons.items():
            if key == page_name:
                button.configure(
                    fg_color=("gray70", "gray30"),
                    text_color=("black", "white"),
                )
            else:
                button.configure(
                    fg_color="transparent",
                    text_color=("black", "white"),
                )
