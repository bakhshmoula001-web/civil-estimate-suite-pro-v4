"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Dependency Container
Purpose   : Dependency Injection Container
Author    : OpenAI + Moula Bakhsh
Version   : 4.0.0
=========================================================
"""

from __future__ import annotations

from app.application_context import ApplicationContext

from core.logger import AppLogger
from config.setting import Settings

from database.database_manager import DatabaseManager

from database.repositories.project_repository import (
    ProjectRepository,
)

from database.repositories.boq_repository import (
    BOQRepository,
)

from services.project_service import ProjectService
from services.boq_service import BOQService


class DependencyContainer:
    """
    Creates and wires all application dependencies.
    """

    def __init__(self):

        self.context = ApplicationContext()

    # --------------------------------------------------
    # Initialize
    # --------------------------------------------------

    def initialize(self) -> ApplicationContext:

        # -------------------------------
        # Core
        # -------------------------------

        self.context.logger = AppLogger()

        self.context.settings = Settings()

        # -------------------------------
        # Database
        # -------------------------------

        database = DatabaseManager()

        database.initialize()

        self.context.database = database

        # -------------------------------
        # Repositories
        # -------------------------------

        project_repository = ProjectRepository(database)

        boq_repository = BOQRepository(database)

        # -------------------------------
        # Services
        # -------------------------------

        self.context.project_service = ProjectService(
            project_repository
        )

        self.context.boq_service = BOQService(
            boq_repository,
            project_repository
        )

        self.context.logger.info(
            "Application dependencies initialized."
        )

        return self.context

    # --------------------------------------------------
    # Shutdown
    # --------------------------------------------------

    def shutdown(self):

        if self.context.database:

            self.context.database.close()

        if self.context.logger:

            self.context.logger.info(
                "Application shutdown completed."
            )