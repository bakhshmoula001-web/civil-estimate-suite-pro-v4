"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Header
Purpose   : Application Header
Author    : OpenAI + Moula Bakhsh
Version   : 4.0.0
=========================================================
"""

from __future__ import annotations

import customtkinter as ctk

from app.application_context import ApplicationContext


class Header(ctk.CTkFrame):
    """
    Top header of the application.
    """

    HEIGHT = 60

    def __init__(
        self,
        master,
        context: ApplicationContext,
        **kwargs
    ):

        super().__init__(
            master,
            height=self.HEIGHT,
            corner_radius=0,
            **kwargs
        )

        self.context = context

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self._create_widgets()

    # --------------------------------------------------
    # Widgets
    # --------------------------------------------------

    def _create_widgets(self):

        self.title_label = ctk.CTkLabel(
            self,
            text=self.context.application_name,
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )
        )

        self.title_label.grid(
            row=0,
            column=0,
            padx=20,
            pady=15,
            sticky="w"
        )

        self.version_label = ctk.CTkLabel(
            self,
            text=f"Version {self.context.version}",
            font=ctk.CTkFont(size=13)
        )

        self.version_label.grid(
            row=0,
            column=1,
            padx=20,
            pady=15,
            sticky="e"
        )

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def set_title(
        self,
        title: str
    ):

        self.title_label.configure(
            text=title
        )

    def reset_title(self):

        self.title_label.configure(
            text=self.context.application_name
        )