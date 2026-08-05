# project_page.py
from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox

from gui.widgets.project_table import ProjectTable
from gui.forms.project_form import ProjectForm
from core.current_project import CurrentProject

class ProjectPage(ctk.CTkFrame):

    def __init__(self, master, controller,window_manager):
        super().__init__(master)

        self.controller = controller
        self.window_manager = window_manager
        self.search_var = ctk.StringVar()

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_toolbar()
        self._build_table()

        self.refresh()

    def _build_toolbar(self):
        bar = ctk.CTkFrame(self)
        bar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkButton(bar, text="New", command=self.new_project).pack(side="left", padx=4)
        ctk.CTkButton(bar, text="Edit", command=self.edit_project).pack(side="left", padx=4)
        ctk.CTkButton(bar, text="Delete", command=self.delete_project).pack(side="left", padx=4)
        ctk.CTkButton(bar, text="Refresh", command=self.refresh).pack(side="left", padx=4)
        ctk.CTkButton(bar, text="Open BOQ", command=self.open_boq).pack(side="left", padx=4)
        entry = ctk.CTkEntry(
            bar,
            width=250,
            textvariable=self.search_var,
            placeholder_text="Search..."
        )
        entry.pack(side="right", padx=4)
        entry.bind("<KeyRelease>", self.search_projects)

    def _build_table(self):
        self.project_table = ProjectTable(
            self,
            on_double_click=self.edit_project
        )
        self.project_table.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))

    def refresh(self):
        projects = self.controller.get_all()
        self.project_table.load_projects(projects)

    def search_projects(self, event=None):
        keyword = self.search_var.get().strip().lower()
        projects = self.controller.get_all()

        if keyword:
            projects = [
                p for p in projects
                if keyword in p.project_code.lower()
                or keyword in p.project_name.lower()
                or keyword in p.client_name.lower()
                or keyword in p.consultant.lower()
                or keyword in p.contractor.lower()
                or keyword in p.location.lower()
                or keyword in p.status.lower()
                or keyword in p.remarks.lower()
                or keyword in (p.start_date or "").lower()
                or keyword in (p.end_date or "").lower()
                or keyword in (p.created_at or "").lower()
                or keyword in (p.updated_at or "").lower()
                or keyword in str(p.id)
            ]

        self.project_table.load_projects(projects)

    def new_project(self):
        form = ProjectForm(self)
        self.wait_window(form)

        if form.result is None:
            return

        try:
            print("Project:", form.result.to_dict())

            new_id = self.controller.create(form.result)

            print("Created ID:", new_id)

            self.refresh()

            messagebox.showinfo(
                "Success",
                "Project saved successfully."
        )

        except Exception as ex:
         import traceback
         traceback.print_exc()

         messagebox.showerror(
            "Create Error",
            str(ex)
        )
    def edit_project(self, project=None):
        if project is None:
            project = self.project_table.selected_project()

        if project is None:
            messagebox.showwarning("Projects", "Please select a project.")
            return
        CurrentProject.set(project)
        form = ProjectForm(self, project)
        self.wait_window(form)

        if getattr(form, "result", None) is None:
            return

        self.controller.update(project.id, form.result)
        self.refresh()

    def delete_project(self):
        project = self.project_table.selected_project()

        if project is None:
            messagebox.showwarning("Projects", "Please select a project.")
            return

        if not messagebox.askyesno(
            "Delete Project",
            f"Delete '{project.project_name}'?"
        ):
            return

        self.controller.delete(project.id)
        self.refresh()
    def open_boq(self):

         project = self.project_table.selected_project()

         if project is None:
          messagebox.showwarning(
            "Projects",
            "Please select a project."
        )
          return

         CurrentProject.set(project)

         self.window_manager.show_page("boq")
