"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Dashboard Page
Purpose   : Main Dashboard
Author    : OpenAI + Moula Bakhsh
Version   : 4.0.0
=========================================================
"""

from __future__ import annotations

import customtkinter as ctk

from app.application_context import ApplicationContext
from gui.widgets.stat_card import StatCard


class DashboardPage(ctk.CTkFrame):
    """
    Main Dashboard Page.
    """

    def __init__(
        self,
        master,
        context: ApplicationContext,
        **kwargs
    ):

        super().__init__(master, **kwargs)

        self.context = context

        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._create_header()
        self._create_summary_cards()
        self._create_recent_projects()

    # --------------------------------------------------
    # Header
    # --------------------------------------------------

    def _create_header(self):

        title = ctk.CTkLabel(
            self,
            text="Dashboard",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        )

        title.grid(
            row=0,
            column=0,
            columnspan=3,
            padx=20,
            pady=(20, 10),
            sticky="w"
        )

    # --------------------------------------------------
    # Summary Cards
    # --------------------------------------------------

    def _create_summary_cards(self):

        self.project_card = StatCard(
        self,
        title="Projects",
        value="0"
    )

        self.project_card.grid(
        row=1,
        column=0,
        padx=15,
        pady=10,
        sticky="nsew"
    )

        self.boq_card = StatCard(
        self,
        title="BOQ Items",
        value="0"
    )

        self.boq_card.grid(
        row=1,
        column=1,
        padx=15,
        pady=10,
        sticky="nsew"
    )

        self.cost_card = StatCard(
        self,
        title="Estimated Cost",
        value="PKR 0"
    )

        self.cost_card.grid(
        row=1,
        column=2,
        padx=15,
        pady=10,
        sticky="nsew"
    )

    # --------------------------------------------------
    # Recent Projects
    # --------------------------------------------------

    def _create_recent_projects(self):

        frame = ctk.CTkFrame(self)

        frame.grid(
            row=2,
            column=0,
            columnspan=3,
            padx=15,
            pady=15,
            sticky="nsew"
        )

        title = ctk.CTkLabel(
            frame,
            text="Recent Projects",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        )

        title.pack(
            anchor="w",
            padx=20,
            pady=(15, 10)
        )

        self.project_list = ctk.CTkTextbox(
            frame,
            height=250
        )

        self.project_list.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        self.project_list.insert(
            "end",
            "No projects available."
        )

        self.project_list.configure(
            state="disabled"
        )

    # --------------------------------------------------
    # Refresh
    # --------------------------------------------------

    def refresh(self):

        try:

            project_count = self.context.project_service.total_projects()

            self.project_card.value_label.configure(
                text=str(project_count)
            )

        except Exception as ex:

            if self.context.logger:

                self.context.logger.exception(ex)