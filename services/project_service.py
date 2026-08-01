from __future__ import annotations

from models.project import Project


class ProjectService:
    """
    Business Logic Layer

    Controller
        │
        ▼
    ProjectService
        │
        ▼
    Repository
    """

    def __init__(self, repository):
        self.repository = repository

    # ---------------------------------------------------------
    # READ
    # ---------------------------------------------------------

    def get(self, project_id: int):
        return self.repository.get(project_id)

    def get_all(self):
        return self.repository.get_all()

    def get_recent(self, limit: int = 10):
        return self.repository.get_recent(limit)

    def total_projects(self):
        return self.repository.count()

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------

    def create(self, project: Project):

        self._validate(project)

        if self.exists(project.project_code):
            raise ValueError(
                f"Project Code '{project.project_code}' already exists."
            )

        return self.repository.create(project)

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------

    def update(self, project_id: int, project: Project):

        self._validate(project)

        existing = self.repository.get(project_id)

        if existing is None:
            raise ValueError("Project not found.")

        duplicate = self.repository.find_by_code(
            project.project_code
        )

        if duplicate and duplicate.id != project_id:
            raise ValueError(
                f"Project Code '{project.project_code}' already exists."
            )

        return self.repository.update(project_id, project)

    # ---------------------------------------------------------
    # DELETE
    # ---------------------------------------------------------

    def delete(self, project_id: int):

        existing = self.repository.get(project_id)

        if existing is None:
            raise ValueError("Project not found.")

        return self.repository.delete(project_id)

    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------

    def search(self, keyword: str):

        keyword = keyword.strip()

        if keyword == "":
            return self.get_all()

        return self.repository.search(keyword)

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    def _validate(self, project: Project):

        if project is None:
            raise ValueError("Project cannot be None.")

        project.validate()

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    def exists(self, project_code: str):

        return self.repository.find_by_code(project_code) is not None