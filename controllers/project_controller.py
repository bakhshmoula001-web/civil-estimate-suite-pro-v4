from __future__ import annotations

from models.project import Project


class ProjectController:
    """
    Project Controller

    GUI  ---> Controller ---> Service ---> Repository ---> Database
    """

    def __init__(self, service):
        self.service = service

    # ---------------------------------------------------------
    # READ
    # ---------------------------------------------------------

    def get(self, project_id: int):
        return self.service.get(project_id)

    def get_all(self):
        return self.service.get_all()

    def get_recent(self, limit: int = 10):
        return self.service.get_recent(limit)

    def total_projects(self):
        return self.service.total_projects()

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------

    def create(self, project: Project):

        if project is None:
            raise ValueError("Project cannot be None.")

        project.validate()

        return self.service.create(project)

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------

    def update(self, project_id: int, project: Project):

        if project is None:
            raise ValueError("Project cannot be None.")

        project.validate()

        return self.service.update(project_id, project)

    # ---------------------------------------------------------
    # DELETE
    # ---------------------------------------------------------

    def delete(self, project_id: int):
        return self.service.delete(project_id)

    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------

    def search(self, keyword: str):

        keyword = keyword.strip()

        if keyword == "":
            return self.get_all()

        return self.service.search(keyword)

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    def exists(self, project_code: str):
        return self.service.exists(project_code)

    def count(self):
        return self.service.total_projects()