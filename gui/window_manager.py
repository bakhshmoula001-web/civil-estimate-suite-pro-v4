from __future__ import annotations

from app.application_context import ApplicationContext
from gui.pages.dashboard_page import DashboardPage
from gui.pages.project_page import ProjectPage
from gui.pages.boq_page import BOQPage
from gui.pages.material_page import MaterialPage
from gui.pages.calculator_page import CalculatorPage
from gui.pages.report_page import ReportPage
from gui.pages.settings_page import SettingsPage
from gui.pages.rates_page import RatesPage
from gui.pages.backup_page import BackupPage


class WindowManager:
    def __init__(self, parent, context: ApplicationContext):
        self.parent = parent
        self.context = context
        self.pages = {}
        self.current_page = None
        self._register_pages()

    def _register_pages(self):
        self.pages["dashboard"] = DashboardPage(self.parent, self.context)
        self.pages["projects"] = ProjectPage(
            self.parent, self.context.project_controller, self
        )
        self.pages["boq"] = BOQPage(
            self.parent, self.context.boq_controller, context=self.context
        )
        self.pages["materials"] = MaterialPage(
            self.parent, self.context.material_controller
        )
        self.pages["calculators"] = CalculatorPage(
            self.parent, self.context, self
        )
        self.pages["reports"] = ReportPage(self.parent, self.context)
        self.pages["settings"] = SettingsPage(self.parent, self.context)
        self.pages["rates"] = RatesPage(self.parent, self.context)
        self.pages["backup"] = BackupPage(self.parent, self.context)

    def show_page(self, page_name: str):
        page_name = self._normalize_page_name(page_name)
        if self.current_page is not None:
            try:
                self.current_page.grid_forget()
            except Exception:
                pass

        page = self.pages.get(page_name)
        if page is None:
            if getattr(self.context, "logger", None):
                self.context.logger.warning(f"Page not registered: {page_name}")
            return False

        page.grid(row=0, column=0, sticky="nsew")
        self.current_page = page

        if hasattr(page, "refresh"):
            try:
                page.refresh()
            except TypeError:
                pass
            except Exception as error:
                if getattr(self.context, "logger", None):
                    self.context.logger.warning(
                        f"Page refresh failed: {page_name}: {error}"
                    )

        if getattr(self.context, "logger", None):
            self.context.logger.info(f"Page loaded: {page_name}")
            self.context.logger.info(f"Navigate -> {page_name}")
        return True

    def navigate(self, page_name: str) -> bool:
        return self.show_page(page_name)

    def refresh_current(self):
        if self.current_page is None:
            return
        refresh = getattr(self.current_page, "refresh", None)
        if callable(refresh):
            try:
                refresh()
            except TypeError:
                pass

    def current(self):
        return self.current_page

    def current_page_name(self):
        for name, page in self.pages.items():
            if page is self.current_page:
                return name
        return None

    def has_page(self, page_name: str) -> bool:
        return self._normalize_page_name(page_name) in self.pages

    def get_page(self, page_name: str):
        return self.pages.get(self._normalize_page_name(page_name))

    def page_names(self) -> list[str]:
        return list(self.pages.keys())

    @staticmethod
    def _normalize_page_name(page_name: str) -> str:
        if page_name is None:
            return ""
        value = (
            str(page_name).strip().lower()
            .replace("-", "_")
            .replace(" ", "_")
        )
        aliases = {
            "dashboard": "dashboard", "home": "dashboard",
            "home_page": "dashboard",
            "project": "projects", "projects": "projects",
            "project_page": "projects",
            "boq": "boq", "boq_page": "boq",
            "material": "materials", "materials": "materials",
            "material_page": "materials",
            "calculator": "calculators", "calculators": "calculators",
            "calculator_page": "calculators",
            "report": "reports", "reports": "reports",
            "report_page": "reports",
            "setting": "settings", "settings": "settings",
            "settings_page": "settings",
            "rate": "rates", "rates": "rates", "project_rates": "rates",
            "backup": "backup", "backups": "backup",
            "backup_page": "backup",
        }
        return aliases.get(value, value)

    def close_current(self):
        if self.current_page is not None:
            try:
                self.current_page.grid_forget()
            except Exception:
                pass
            self.current_page = None

    def refresh_page(self, page_name: str):
        page = self.get_page(page_name)
        if page is None:
            return False
        refresh = getattr(page, "refresh", None)
        if callable(refresh):
            try:
                refresh()
            except TypeError:
                pass
        return True
