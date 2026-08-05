"""
Current Project Manager

Maintains the currently selected project across the application.
"""

from __future__ import annotations

from typing import Optional

from models.project import Project


class CurrentProject:

    _project: Optional[Project] = None

    @classmethod
    def set(cls, project: Project):

        cls._project = project

    @classmethod
    def get(cls) -> Optional[Project]:

        return cls._project

    @classmethod
    def id(cls) -> Optional[int]:

        if cls._project is None:
            return None

        return cls._project.id

    @classmethod
    def code(cls) -> str:

        if cls._project is None:
            return ""

        return cls._project.project_code

    @classmethod
    def name(cls) -> str:

        if cls._project is None:
            return ""

        return cls._project.project_name

    @classmethod
    def clear(cls):

        cls._project = None

    @classmethod
    def is_selected(cls) -> bool:

        return cls._project is not None