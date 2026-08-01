"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Statistic Card Widget
Purpose   : Reusable Dashboard Statistic Card
Author    : OpenAI + Moula Bakhsh
Version   : 4.0.0
=========================================================
"""

from __future__ import annotations

import customtkinter as ctk


class StatCard(ctk.CTkFrame):
    """
    Reusable statistic card widget.
    """

    def __init__(
        self,
        master,
        title: str,
        value: str = "0",
        width: int = 250,
        height: int = 130,
        **kwargs
    ):

        super().__init__(
            master,
            width=width,
            height=height,
            corner_radius=12,
            **kwargs
        )

        self.grid_propagate(False)

        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            )
        )

        self.title_label.grid(
            row=0,
            column=0,
            padx=20,
            pady=(18, 5),
            sticky="w"
        )

        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            )
        )

        self.value_label.grid(
            row=1,
            column=0,
            padx=20,
            pady=(0, 18),
            sticky="w"
        )

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def set_value(self, value):

        self.value_label.configure(
            text=str(value)
        )

    def get_value(self):

        return self.value_label.cget("text")

    def set_title(self, title):

        self.title_label.configure(
            text=title
        )

    def clear(self):

        self.set_value("0")