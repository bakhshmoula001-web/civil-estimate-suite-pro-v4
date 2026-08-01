from app.application_context import ApplicationContext

from database.database_manager import DatabaseManager

from database.repositories.project_repository import ProjectRepository
from services.project_service import ProjectService
from controllers.project_controller import ProjectController


class Bootstrap:

    def __init__(self):
        self.context = None

    def initialize(self):

        self.context = ApplicationContext(
            database_path="database/civil_estimate_suite.db",
            application_name="Civil Estimate Suite Pro",
            version="4.0",
        )

        # Database
        db = DatabaseManager(self.context.database_path)

        # Repository
        project_repository = ProjectRepository(db)

        # Service
        project_service = ProjectService(project_repository)

        # Controller
        project_controller = ProjectController(project_service)

        # Register in Context
        self.context.database = db
        self.context.project_repository = project_repository
        self.context.project_service = project_service
        self.context.project_controller = project_controller

        return self.context

    def shutdown(self):

        if getattr(self.context, "database", None):
            self.context.database.close()

        if self.context:
            self.context.shutdown()