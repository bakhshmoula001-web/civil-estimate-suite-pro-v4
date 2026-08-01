"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Application
Purpose   : Application Lifecycle
Author     : OpenAI + Moula Bakhsh
Version    : 4.0.0
=========================================================
"""

from __future__ import annotations

import customtkinter as ctk

from app.application_context import ApplicationContext

from gui.main_window import MainWindow


class Application:
    """
    Main Application Lifecycle.
    """

    def __init__(
        self,
        context: ApplicationContext
    ):

        self.context = context

        self.window: MainWindow | None = None

    # --------------------------------------------------
    # Configure Theme
    # --------------------------------------------------

    def configure_theme(self):

        ctk.set_appearance_mode("System")

        ctk.set_default_color_theme("blue")

    # --------------------------------------------------
    # Create Window
    # --------------------------------------------------

    def create_window(self):

        self.window = MainWindow(
            self.context
        )

    # --------------------------------------------------
    # Run
    # --------------------------------------------------

    def run(self):

        self.configure_theme()

        self.create_window()

        if self.context.logger:
         self.context.logger.info(
        "Application Started."
    )

        self.window.mainloop()

    # --------------------------------------------------
    # Shutdown
    # --------------------------------------------------

    def shutdown(self):

        if self.context.logger:
         self.context.logger.info(
        "Application Closed."
    )