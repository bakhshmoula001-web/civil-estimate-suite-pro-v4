"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Window Manager
Purpose   : Page Navigation Manager
=========================================================
"""

from __future__ import annotations

from app.application_context import ApplicationContext

from gui.pages.dashboard_page import DashboardPage
from gui.pages.project_page import ProjectPage
from gui.pages.boq_page import BOQPage


class WindowManager:
    """
    Controls navigation between application pages.
    """

    def __init__(
        self,
        parent,
        context: ApplicationContext,
    ):

        self.parent = parent
        self.context = context

        self.pages = {}
        self.current_page = None

        self._register_pages()

    # --------------------------------------------------
    # Register Pages
    # --------------------------------------------------

    def _register_pages(self):

        self.pages["dashboard"] = DashboardPage(
            self.parent,
            self.context,
        )

        self.pages["projects"] = ProjectPage(
        self.parent,
        self.context.project_controller,
)
        self.pages["boq"] = BOQPage(
        self.parent,
        self.context.boq_controller,
)
    # --------------------------------------------------
    # Show Page
    # --------------------------------------------------

    def show_page(
        self,
        page_name: str,
    ):

        if self.current_page is not None:
            self.current_page.grid_forget()

        page = self.pages.get(page_name)

        if page is None:

            if getattr(self.context, "logger", None):
                self.context.logger.warning(
                    f"Page not registered: {page_name}"
                )
            return

        page.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        self.current_page = page

        if self.context.logger:
            self.context.logger.info(
                f"Page loaded: {page_name}"
            )

    # --------------------------------------------------
    # Refresh Current Page
    # --------------------------------------------------

    def refresh_current(self):

        if (
            self.current_page is not None
            and hasattr(self.current_page, "refresh")
        ):
            self.current_page.refresh()

    # --------------------------------------------------
    # Current Page
    # --------------------------------------------------

    def current(self):

        return self.current_page