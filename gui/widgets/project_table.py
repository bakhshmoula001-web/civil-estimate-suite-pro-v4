# project_table.py
from __future__ import annotations

import customtkinter as ctk
from tkinter import ttk


class ProjectTable(ctk.CTkFrame):
    def __init__(self, master, on_double_click=None):
        super().__init__(master)

        self.on_double_click = on_double_click
        self._projects = []

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        columns = (
            "code",
            "name",
            "client",
            "consultant",
            "contractor",
            "location",
            "start_date",
            "end_date",
            "status",
            "remarks",
        )

        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        headings = {
            "code": "Project Code",
            "name": "Project Name",
            "client": "Client",
            "consultant": "Consultant",
            "contractor": "Contractor",
            "location": "Location",
            "start_date": "Start Date",
            "end_date": "End Date",
            "status": "Status",
            "remarks": "Remarks",
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, anchor="w", width=180)

        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.configure(yscrollcommand=scrollbar.set)

        if self.on_double_click:
            self.tree.bind("<Double-1>", self._handle_double_click)

    def load_projects(self, projects):
        self._projects = list(projects)

        for item in self.tree.get_children():
            self.tree.delete(item)

        for index, project in enumerate(self._projects):
            self.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    getattr(project, "project_code", ""),
                    getattr(project, "project_name", ""),
                    getattr(project, "client_name", ""),
                    getattr(project, "consultant", ""),
                    getattr(project, "contractor", ""),
                    getattr(project, "location", ""),
                    getattr(project, "start_date", ""),
                    getattr(project, "end_date", ""),
                    getattr(project, "status", ""),
                    getattr(project, "remarks", ""),
                ),
            )

    def selected_project(self):
        selection = self.tree.selection()
        if not selection:
            return None

        index = int(selection[0])
        if 0 <= index < len(self._projects):
            return self._projects[index]
        return None

    def _handle_double_click(self, event):
        project = self.selected_project()
        if project and self.on_double_click:
            self.on_double_click(project)

    def clear(self):
        self._projects.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
