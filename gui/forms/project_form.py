# project_form.py
from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox


class ProjectForm(ctk.CTkToplevel):
    def __init__(self, parent, project=None):
        super().__init__(parent)

        self.result = None
        self.project = project

        self.title("Project")
        self.geometry("700x600")
        self.resizable(False, False)
        self.grab_set()

        self.vars = {
            "project_code": ctk.StringVar(),
            "project_name": ctk.StringVar(),
            "client_name": ctk.StringVar(),
            "location": ctk.StringVar(),
            "description": ctk.StringVar(),
        }

        self._build_form()

        if project is not None:
            self._load_project(project)
            self.title("Edit Project")
        else:
            self.title("New Project")

    def _build_form(self):
        fields = [
            ("Project Code", "project_code"),
            ("Project Name", "project_name"),
            ("Client Name", "client_name"),
            ("Location", "location"),
            ("Description", "description"),
        ]

        for r, (label, key) in enumerate(fields):
            ctk.CTkLabel(self, text=label).grid(row=r, column=0, padx=15, pady=10, sticky="w")
            ctk.CTkEntry(self, width=420, textvariable=self.vars[key]).grid(
                row=r, column=1, padx=15, pady=10, sticky="ew"
            )

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=len(fields), column=0, columnspan=2, pady=20)

        ctk.CTkButton(btns, text="Save", command=self.save).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="Cancel", command=self.cancel).pack(side="left", padx=5)

    def _load_project(self, project):
        for key in self.vars:
            if hasattr(project, key):
                self.vars[key].set(str(getattr(project, key)))

    def save(self):
        if not self.vars["project_name"].get().strip():
            messagebox.showerror("Validation", "Project Name is required.")
            return

        data = {k: v.get().strip() for k, v in self.vars.items()}

        if self.project is not None and hasattr(self.project, "id"):
            data["id"] = self.project.id

        self.result = type("ProjectData", (), data)()
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()
