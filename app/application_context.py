from __future__ import annotations

from database.database_manager import DatabaseManager
from database.database_initializer import DatabaseInitializer

from database.repositories.project_repository import ProjectRepository
from database.repositories.boq_repository import BOQRepository

from services.project_service import ProjectService
from services.boq_service import BOQService

from controllers.project_controller import ProjectController
from controllers.boq_controller import BOQController

from core.logger import AppLogger


class ApplicationContext:
    """
    Central Dependency Container
    """

    def __init__(
        self,
        database_path: str = "database/civil_estimate_suite.db",
        application_name: str = "Civil Estimate Suite Pro",
        version: str = "4.0",
        logger=None,
    ):

        # -------------------------------------------------
        # Application
        # -------------------------------------------------

        self.database_path = database_path
        self.application_name = application_name
        self.version = version

        self.logger = logger or AppLogger().logger

        # -------------------------------------------------
        # Database
        # -------------------------------------------------

        self.database = DatabaseManager(self.database_path)

        self.database.connect()

        DatabaseInitializer(
            self.database
        ).initialize()

        # -------------------------------------------------
        # Project Module
        # -------------------------------------------------

        self.project_repository = ProjectRepository(
            self.database
        )

        self.project_service = ProjectService(
            self.project_repository
        )

        self.project_controller = ProjectController(
            self.project_service
        )

        # -------------------------------------------------
        # BOQ Module
        # -------------------------------------------------

        self.boq_repository = BOQRepository(
            self.database
        )

        self.boq_service = BOQService(
            self.boq_repository
        )

        self.boq_controller = BOQController(
            self.boq_service
        )

    # -------------------------------------------------

    def shutdown(self):

        if self.logger:
            self.logger.info(
                "Closing database connection."
            )

        self.database.close()