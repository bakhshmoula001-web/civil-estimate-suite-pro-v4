from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox

from gui.widgets.project_toolbar import ProjectToolbar
from gui.widgets.project_table import ProjectTable
from gui.forms.project_form import ProjectForm


class ProjectPage(ctk.CTkFrame):
    """Coordinates Project Module UI."""

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.toolbar = ProjectToolbar(
            self,
            on_new=self.new_project,
            on_edit=self.edit_project,
            on_delete=self.delete_project,
            on_refresh=self.refresh,
            on_search=self.search_projects,
        )
        self.toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,5))

        self.project_table = ProjectTable(
            self,
            on_double_click=self.edit_project,
        )
        self.project_table.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))

        self.refresh()

    def refresh(self):
        self.project_table.load_projects(self.controller.get_all())

    def search_projects(self, text=""):
        text=text.strip().lower()
        projects=self.controller.get_all()
        if text:
            projects=[
                p for p in projects
                if text in getattr(p,"project_code","").lower()
                or text in getattr(p,"project_name","").lower()
                or text in getattr(p,"client_name","").lower()
                or text in getattr(p,"location","").lower()
            ]
        self.project_table.load_projects(projects)

    def new_project(self):
        form=ProjectForm(self)
        self.wait_window(form)
        if getattr(form,"result",None):
            self.controller.create(form.result)
            self.refresh()

    def edit_project(self, project=None):
        project=project or self.project_table.selected_project()
        if not project:
            messagebox.showwarning("Projects","Please select a project.")
            return
        form=ProjectForm(self, project)
        self.wait_window(form)
        if getattr(form,"result",None):
            self.controller.update(project.id, form.result)
            self.refresh()

    def delete_project(self):
        project=self.project_table.selected_project()
        if not project:
            messagebox.showwarning("Projects","Please select a project.")
            return
        if messagebox.askyesno("Delete Project",f"Delete '{project.project_name}'?"):
            self.controller.delete(project.id)
            self.refresh()
