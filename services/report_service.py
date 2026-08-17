"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Report Service
Purpose   : Application-level reporting facade
Version   : 4.0.1
=========================================================
"""

from __future__ import annotations

from pathlib import Path

from reports.boq_export_service import BOQExportService


class ReportService:
    """
    Central reporting service.

    Backward compatible with both supported construction styles:

        ReportService("exports")

    and:

        ReportService(
            boq_service=...,
            project_service=...,
            export_folder="exports",
        )

    The BOQ/project services are retained as references for the
    application dependency container, while actual Excel/PDF
    generation remains delegated to BOQExportService.
    """

    def __init__(
        self,
        boq_service=None,
        project_service=None,
        export_folder: str | Path = "exports",
    ):
        # Backward compatibility:
        # ReportService("exports") from the earlier Report Center
        # implementation passes the folder as the first positional arg.
        if isinstance(boq_service, (str, Path)):
            if project_service is None and export_folder == "exports":
                export_folder = boq_service
                boq_service = None

        self.boq_service = boq_service
        self.project_service = project_service
        self.exporter = BOQExportService(export_folder)

    @property
    def export_folder(self) -> Path:
        return self.exporter.export_folder

    def export_excel(self, project, items, file_path=None):
        return self.exporter.export_excel(
            project,
            items,
            file_path,
        )

    def export_pdf(self, project, items, file_path=None):
        return self.exporter.export_pdf(
            project,
            items,
            file_path,
        )

    def export_both(self, project, items, folder=None):
        return self.exporter.export_both(
            project,
            items,
            folder,
        )


__all__ = ["ReportService"]
