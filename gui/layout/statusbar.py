
"""
gui/layout/statusbar.py
Professional Status Bar for Civil Estimate Suite Pro v4.0
"""

from __future__ import annotations

import customtkinter as ctk
from datetime import datetime
from typing import Optional


class StatusBar(ctk.CTkFrame):
    def __init__(self, master, context: Optional[object] = None, **kwargs):
        super().__init__(master, height=28, corner_radius=0, **kwargs)

        self.context = context

        self.grid_columnconfigure(0, weight=1)

        self._status = ctk.CTkLabel(self, text="Ready", anchor="w")
        self._status.grid(row=0, column=0, padx=(10, 5), pady=4, sticky="ew")

        self._database = ctk.CTkLabel(self, text="Database: Connected")
        self._database.grid(row=0, column=1, padx=8)

        self._project = ctk.CTkLabel(self, text="Project: None")
        self._project.grid(row=0, column=2, padx=8)

        self._version = ctk.CTkLabel(self, text="Version: 4.0")
        self._version.grid(row=0, column=3, padx=8)

        self._time = ctk.CTkLabel(
            self,
            text=datetime.now().strftime("%d-%m-%Y %H:%M")
        )
        self._time.grid(row=0, column=4, padx=(8, 12))

    def set_status(self, message: str) -> None:
        self._status.configure(text=message)

    def set_database_status(self, connected: bool) -> None:
        self._database.configure(
            text=f"Database: {'Connected' if connected else 'Disconnected'}"
        )

    def set_project(self, project_name: str | None) -> None:
        self._project.configure(
            text=f"Project: {project_name or 'None'}"
        )

    def set_version(self, version: str) -> None:
        self._version.configure(text=f"Version: {version}")

    def refresh_time(self) -> None:
        self._time.configure(
            text=datetime.now().strftime("%d-%m-%Y %H:%M")
        )
