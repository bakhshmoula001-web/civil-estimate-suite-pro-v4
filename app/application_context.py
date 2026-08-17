"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Application Dependency Container
=========================================================
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from database.database_manager import DatabaseManager
from database.database_initializer import DatabaseInitializer

from database.repositories.project_repository import (
    ProjectRepository,
)

from database.repositories.boq_repository import (
    BOQRepository,
)

from database.repositories.material_repository import (
    MaterialRepository,
)

from database.repositories.rate_repository import (
    RateRepository,
)

from services.project_service import ProjectService
from services.boq_service import BOQService
from services.material_service import MaterialService
from services.rate_service import RateService
from services.report_service import ReportService
from services.estimate_analysis_service import EstimateAnalysisService
from reports.material_report_service import MaterialReportService

from controllers.project_controller import (
    ProjectController,
)

from controllers.boq_controller import (
    BOQController,
)

from controllers.material_controller import (
    MaterialController,
)

from controllers.rate_controller import (
    RateController,
)

from services.calculation_integration_service import (
    CalculationIntegrationService,
)

from controllers.calculation_controller import (
    CalculationController,
)

from core.logger import AppLogger
from config.setting import Settings


class ApplicationContext:
    """
    Central Dependency Container.

    Application Architecture
    ------------------------

        Database
            ↓
        Repositories
            ↓
        Services
            ↓
        Controllers
            ↓
        GUI

    Calculation Architecture
    -------------------------

        Calculator
            ↓
        CalculationResult
            ↓
        CalculationController
            ↓
        CalculationIntegrationService
            ↓
        BOQ / Material
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        database_path: str = (
            "database/civil_estimate_suite.db"
        ),
        application_name: str = (
            "Civil Estimate Suite Pro"
        ),
        version: str = "4.0",
        logger=None,
    ):

        # -------------------------------------------------
        # Application paths
        # -------------------------------------------------
        # Source mode keeps the existing project-relative structure.
        # PyInstaller mode moves all writable application data to
        # the user's LocalAppData directory. This prevents permission
        # errors when the EXE is installed under Program Files or a
        # read-only bundle directory.

        self.application_name = application_name
        self.version = version

        self.is_frozen = bool(
            getattr(sys, "frozen", False)
        )

        self.application_root = self._get_application_root()
        self.user_data_root = self._get_user_data_root()

        self.user_database_dir = (
            self.user_data_root / "database"
        )
        self.user_exports_dir = (
            self.user_data_root / "exports"
        )
        self.user_backups_dir = (
            self.user_data_root / "backups"
        )
        self.user_logs_dir = (
            self.user_data_root / "logs"
        )

        if self.is_frozen:
            self._ensure_user_directories()
            self.database_path = str(
                self._prepare_user_database(
                    database_path
                )
            )
            self.export_folder = str(
                self.user_exports_dir
            )
        else:
            self.database_path = database_path
            self.export_folder = "exports"

        self.settings = Settings()

        self.logger = (
            logger
            or AppLogger().logger
        )

        # -------------------------------------------------
        # Database
        # -------------------------------------------------

        self.database = DatabaseManager(
            self.database_path
        )

        self.database.connect()

        DatabaseInitializer(
            self.database
        ).initialize()

        # -------------------------------------------------
        # Project Module
        # -------------------------------------------------

        self.project_repository = (
            ProjectRepository(
                self.database
            )
        )

        self.project_service = (
            ProjectService(
                self.project_repository
            )
        )

        self.project_controller = (
            ProjectController(
                self.project_service
            )
        )

        # -------------------------------------------------
        # BOQ Module
        # -------------------------------------------------

        self.boq_repository = (
            BOQRepository(
                self.database
            )
        )

        self.boq_service = (
            BOQService(
                self.boq_repository
            )
        )

        self.boq_controller = (
            BOQController(
                self.boq_service
            )
        )

        # -------------------------------------------------
        # Estimate Analysis Module
        # -------------------------------------------------
        # Detailed calculator analysis is stored separately from
        # the primary BOQ row. This service is shared by calculators,
        # BOQ review, and reporting.

        self.estimate_analysis_service = (
            EstimateAnalysisService(
                self.database
            )
        )

        # -------------------------------------------------
        # Report Module
        # -------------------------------------------------

        self.report_service = ReportService(
            boq_service=self.boq_service,
            project_service=self.project_service,
            export_folder=self.export_folder,
        )
        self.material_report_service = MaterialReportService(self.export_folder)

        # -------------------------------------------------
        # Material Module
        # -------------------------------------------------

        self.material_repository = (
            MaterialRepository(
                self.database
            )
        )

        self.material_service = (
            MaterialService(
                self.material_repository
            )
        )

        self.material_controller = (
            MaterialController(
                self.material_service
            )
        )

        # -------------------------------------------------
        # Project Rate Database
        # -------------------------------------------------

        self.rate_repository = (
            RateRepository(
                self.database
            )
        )

        self.rate_service = (
            RateService(
                self.rate_repository
            )
        )

        self.rate_controller = (
            RateController(
                self.rate_service
            )
        )

        # -------------------------------------------------
        # Calculation Integration
        # -------------------------------------------------

        self.calculation_integration_service = (
            CalculationIntegrationService(
                boq_controller=self.boq_controller,
                material_controller=(
                    self.material_controller
                ),
            )
        )

        # -------------------------------------------------
        # Calculation Controller
        # -------------------------------------------------

        self.calculation_controller = (
            CalculationController(
                boq_controller=self.boq_controller,
                material_controller=(
                    self.material_controller
                ),
                integration_service=(
                    self.calculation_integration_service
                ),
                rate_controller=self.rate_controller,
            )
        )

        # -------------------------------------------------
        # Startup Log
        # -------------------------------------------------

        if self.logger:

            self.logger.info(
                "Application context initialized."
            )

    # =====================================================
    # PRODUCTION PATH HELPERS
    # =====================================================

    @staticmethod
    def _get_application_root() -> Path:
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent
        return Path.cwd().resolve()

    @staticmethod
    def _get_user_data_root() -> Path:
        local_app_data = os.environ.get("LOCALAPPDATA")

        if local_app_data:
            return (
                Path(local_app_data)
                / "Civil Estimate Suite Pro"
            )

        user_profile = os.environ.get("USERPROFILE")
        if user_profile:
            return (
                Path(user_profile)
                / "AppData"
                / "Local"
                / "Civil Estimate Suite Pro"
            )

        return (
            Path.home()
            / ".civil_estimate_suite_pro"
        )

    def _ensure_user_directories(self):
        for directory in (
            self.user_database_dir,
            self.user_exports_dir,
            self.user_backups_dir,
            self.user_logs_dir,
        ):
            directory.mkdir(
                parents=True,
                exist_ok=True,
            )

    def _prepare_user_database(
        self,
        database_path: str,
    ) -> Path:
        target = (
            self.user_database_dir
            / Path(database_path).name
        )

        if target.exists():
            return target

        # In a PyInstaller ONEDIR build the bundled database is normally
        # available beside the executable or inside _internal.
        candidates = [
            self.application_root / database_path,
            self.application_root / "_internal" / database_path,
            Path(getattr(sys, "_MEIPASS", self.application_root))
            / database_path,
        ]

        for source in candidates:
            if source.exists() and source.is_file():
                shutil.copy2(source, target)
                return target

        # If there is no bundled database, create the target path.
        # DatabaseInitializer will create the schema.
        return target

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self):

        if self.logger:

            self.logger.info(
                "Closing database connection."
            )

        self.database.close()