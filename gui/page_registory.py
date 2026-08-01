"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Page Registry
Purpose   : Register Application Pages
Author    : OpenAI + Moula Bakhsh
Version   : 4.0.0
=========================================================
"""

from __future__ import annotations

from typing import Dict, Type

from gui.pages.dashboard_page import DashboardPage
from gui.pages.project_page import ProjectPage



class PageRegistry:
    """
    Registry for all application pages.
    """

    def __init__(self):

        self._pages: Dict[str, Type] = {}

        self.register_defaults()

    # --------------------------------------------------
    # Default Pages
    # --------------------------------------------------

    def register_defaults(self):

        self.register(
            "dashboard",
            DashboardPage
        )

        self.register(
            "projects",
            ProjectPage
        )

        self.register(
            "boq",
            BOQPage
        )

    # --------------------------------------------------
    # Register
    # --------------------------------------------------

    def register(
        self,
        name: str,
        page_class: Type
    ):

        self._pages[name] = page_class

    # --------------------------------------------------
    # Get
    # --------------------------------------------------

    def get(
        self,
        name: str
    ):

        return self._pages.get(name)

    # --------------------------------------------------
    # Exists
    # --------------------------------------------------

    def exists(
        self,
        name: str
    ) -> bool:

        return name in self._pages

    # --------------------------------------------------
    # All
    # --------------------------------------------------

    def all(self):

        return self._pages.copy()