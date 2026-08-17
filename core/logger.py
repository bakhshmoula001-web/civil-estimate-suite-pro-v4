"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Logger
Purpose   : Centralized Application Logging
Author    : OpenAI + Moula Bakhsh
Version   : 4.0.0
=========================================================
"""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


class AppLogger:
    """Central application logger with production-safe writable paths."""

    _logger = None

    def __init__(
        self,
        log_directory: str | Path = "logs",
        log_filename: str = "application.log",
        level: int = logging.INFO,
    ) -> None:

        if AppLogger._logger is None:
            self._create_logger(
                log_directory,
                log_filename,
                level,
            )

    @staticmethod
    def _resolve_log_directory(
        log_directory: str | Path,
    ) -> Path:

        requested = Path(log_directory)

        # --------------------------------------------------
        # Production / PyInstaller
        # --------------------------------------------------
        # Never create writable files beside the EXE when
        # the EXE is installed under Program Files.
        # --------------------------------------------------

        if getattr(sys, "frozen", False):

            if not requested.is_absolute():

                local_app_data = os.environ.get(
                    "LOCALAPPDATA"
                )

                if local_app_data:
                    return (
                        Path(local_app_data)
                        / "Civil Estimate Suite Pro"
                        / "logs"
                    )

                user_profile = os.environ.get(
                    "USERPROFILE"
                )

                if user_profile:
                    return (
                        Path(user_profile)
                        / "AppData"
                        / "Local"
                        / "Civil Estimate Suite Pro"
                        / "logs"
                    )

                return (
                    Path.home()
                    / ".civil_estimate_suite_pro"
                    / "logs"
                )

        # --------------------------------------------------
        # Development / source mode
        # --------------------------------------------------

        return requested

    # --------------------------------------------------
    # Create Logger
    # --------------------------------------------------

    def _create_logger(
        self,
        log_directory: str | Path,
        log_filename: str,
        level: int,
    ) -> None:

        log_path = self._resolve_log_directory(
            log_directory
        )

        log_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        logger = logging.getLogger(
            "CivilEstimateSuite"
        )

        logger.setLevel(level)

        logger.propagate = False

        # Prevent duplicate handlers if the logger is
        # initialized more than once.
        if logger.handlers:
            AppLogger._logger = logger
            return

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )

        # --------------------------------------------------
        # File Handler
        # --------------------------------------------------

        file_handler = RotatingFileHandler(
            filename=log_path / log_filename,
            maxBytes=2 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )

        file_handler.setFormatter(
            formatter
        )

        # --------------------------------------------------
        # Console Handler
        # --------------------------------------------------

        console_handler = logging.StreamHandler()

        console_handler.setFormatter(
            formatter
        )

        logger.addHandler(
            file_handler
        )

        logger.addHandler(
            console_handler
        )

        AppLogger._logger = logger

    # --------------------------------------------------
    # Logging Methods
    # --------------------------------------------------

    @property
    def logger(self):

        return AppLogger._logger

    def debug(
        self,
        message: str,
    ) -> None:

        self.logger.debug(message)

    def info(
        self,
        message: str,
    ) -> None:

        self.logger.info(message)

    def warning(
        self,
        message: str,
    ) -> None:

        self.logger.warning(message)

    def error(
        self,
        message: str,
    ) -> None:

        self.logger.error(message)

    def critical(
        self,
        message: str,
    ) -> None:

        self.logger.critical(message)

    def exception(
        self,
        message: str,
    ) -> None:

        self.logger.exception(message)


__all__ = ["AppLogger"]