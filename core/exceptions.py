"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Exceptions
Purpose   : Custom Application Exceptions
Author    : OpenAI + Moula Bakhsh
Version   : 4.0.0
=========================================================
"""

from __future__ import annotations


class CivilEstimateSuiteError(Exception):
    """
    Base exception for the application.

    All custom exceptions must inherit from this class.
    """

    def __init__(self, message: str = "Application Error") -> None:
        super().__init__(message)


# ==========================================================
# Configuration
# ==========================================================

class ConfigurationError(CivilEstimateSuiteError):
    """Raised when configuration loading fails."""
    pass


# ==========================================================
# Database
# ==========================================================

class DatabaseError(CivilEstimateSuiteError):
    """Base database exception."""
    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""
    pass


class DatabaseInitializationError(DatabaseError):
    """Raised when database initialization fails."""
    pass


class DatabaseTransactionError(DatabaseError):
    """Raised when transaction fails."""
    pass


# ==========================================================
# Validation
# ==========================================================

class ValidationError(CivilEstimateSuiteError):
    """Raised when validation fails."""
    pass


# ==========================================================
# Project
# ==========================================================

class ProjectError(CivilEstimateSuiteError):
    """Base project exception."""
    pass


class ProjectNotFoundError(ProjectError):
    """Raised when a project cannot be found."""
    pass


class DuplicateProjectError(ProjectError):
    """Raised when duplicate project code exists."""
    pass


# ==========================================================
# BOQ
# ==========================================================

class BOQError(CivilEstimateSuiteError):
    """Base BOQ exception."""
    pass


class BOQItemNotFoundError(BOQError):
    """Raised when BOQ item is missing."""
    pass


class InvalidBOQDataError(BOQError):
    """Raised when BOQ data is invalid."""
    pass


# ==========================================================
# Reports
# ==========================================================

class ReportGenerationError(CivilEstimateSuiteError):
    """Raised when report generation fails."""
    pass


# ==========================================================
# File System
# ==========================================================

class FileOperationError(CivilEstimateSuiteError):
    """Raised for file read/write errors."""
    pass


class BackupError(CivilEstimateSuiteError):
    """Raised during backup/restore."""
    pass


# ==========================================================
# Authentication / License
# ==========================================================

class LicenseError(CivilEstimateSuiteError):
    """Raised when license validation fails."""
    pass


# ==========================================================
# Calculator
# ==========================================================

class CalculationError(CivilEstimateSuiteError):
    """Raised when calculation fails."""
    pass


# ==========================================================
# Export
# ==========================================================

class ExportError(CivilEstimateSuiteError):
    """Raised during Excel/PDF export."""
    pass