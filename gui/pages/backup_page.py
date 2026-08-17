"""Civil Estimate Suite Pro v4.0 - Backup & Restore page."""

from __future__ import annotations

from pathlib import Path
from tkinter import messagebox
import customtkinter as ctk

from database.backup import BackupService


class BackupPage(ctk.CTkFrame):
    def __init__(self, master, context, **kwargs):
        super().__init__(master, **kwargs)
        self.context = context
        self.backup_dir = Path(getattr(context, "user_backups_dir", "backup"))
        self.database_path = Path(getattr(
            context, "database_path", "database/civil_estimate_suite.db"
        ))
        self.service = BackupService(self.database_path, self.backup_dir)
        self.selected_backup = None
        self._build()
        self.refresh()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=25, pady=(20, 10), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="Backup & Restore",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Protect project, BOQ, rates and estimation database",
        ).grid(row=1, column=0, pady=(3, 0), sticky="w")

        actions = ctk.CTkFrame(self)
        actions.grid(row=1, column=0, padx=25, pady=8, sticky="ew")

        for text, command in (
            ("Create Backup", self.create_backup),
            ("Refresh", self.refresh),
            ("Restore Selected", self.restore_selected),
            ("Delete Selected", self.delete_selected),
        ):
            ctk.CTkButton(
                actions, text=text, height=42, command=command
            ).pack(side="left", padx=6, pady=10)

        body = ctk.CTkFrame(self)
        body.grid(row=2, column=0, padx=25, pady=(8, 20), sticky="nsew")
        body.grid_rowconfigure(1, weight=1)
        body.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            body, text="Available Backups",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, padx=15, pady=12, sticky="w")

        self.listbox = ctk.CTkTextbox(body)
        self.listbox.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        self.listbox.configure(state="disabled")
        self.listbox.bind("<Button-1>", self._select_backup)

    def _set_text(self, text):
        self.listbox.configure(state="normal")
        self.listbox.delete("1.0", "end")
        self.listbox.insert("1.0", text)
        self.listbox.configure(state="disabled")

    def refresh(self):
        backups = self.service.list_backups()
        if not backups:
            self.selected_backup = None
            self._set_text(
                "No backups available.\n\n"
                "Click Create Backup to create the first backup."
            )
            return
        self.selected_backup = backups[0]
        self._set_text("\n".join(
            f"{i}. {p.name}   ({p.stat().st_size / 1024:,.1f} KB)"
            for i, p in enumerate(backups, 1)
        ))

    def _select_backup(self, _event=None):
        backups = self.service.list_backups()
        if backups:
            self.selected_backup = backups[0]

    def create_backup(self):
        try:
            path = self.service.create_backup()
            self.refresh()
            self.selected_backup = path
            messagebox.showinfo(
                "Backup Created",
                f"Backup created successfully.\n\n{path}",
                parent=self,
            )
        except Exception as exc:
            messagebox.showerror("Backup Error", str(exc), parent=self)

    def restore_selected(self):
        if not self.selected_backup:
            backups = self.service.list_backups()
            self.selected_backup = backups[0] if backups else None
        if not self.selected_backup:
            messagebox.showwarning(
                "Restore Backup", "No backup is available.", parent=self
            )
            return
        if not messagebox.askyesno(
            "Confirm Restore",
            "Restore the selected backup? A safety copy of the current database "
            "will be created first. Restart the application after restore.",
            parent=self,
        ):
            return
        try:
            self.service.restore_backup(self.selected_backup)
            messagebox.showinfo(
                "Restore Complete",
                "Database restored. Please restart the application.",
                parent=self,
            )
        except Exception as exc:
            messagebox.showerror("Restore Error", str(exc), parent=self)

    def delete_selected(self):
        if not self.selected_backup:
            backups = self.service.list_backups()
            self.selected_backup = backups[0] if backups else None
        if not self.selected_backup:
            return
        if not messagebox.askyesno(
            "Delete Backup",
            f"Delete {self.selected_backup.name}?",
            parent=self,
        ):
            return
        try:
            self.service.delete_backup(self.selected_backup)
            self.selected_backup = None
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Delete Backup", str(exc), parent=self)


__all__ = ["BackupPage"]
