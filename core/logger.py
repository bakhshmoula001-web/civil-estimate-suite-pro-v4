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
from logging.handlers import RotatingFileHandler
from pathlib import Path


class AppLogger:
    """
    Central logger for the entire application.

    Features
    --------
    ✔ Console Logging
    ✔ File Logging
    ✔ Automatic Log Folder Creation
    ✔ Log Rotation
    ✔ Reusable Singleton Logger
    """

    _logger = None

    def __init__(
        self,
        log_directory: str = "logs",
        log_filename: str = "application.log",
        level: int = logging.INFO
    ) -> None:

        if AppLogger._logger is None:

            self._create_logger(
                log_directory,
                log_filename,
                level
            )

    # --------------------------------------------------
    # Create Logger
    # --------------------------------------------------

    def _create_logger(
        self,
        log_directory: str,
        log_filename: str,
        level: int
    ) -> None:

        log_path = Path(log_directory)
        log_path.mkdir(
            parents=True,
            exist_ok=True
        )

        logger = logging.getLogger(
            "CivilEstimateSuite"
        )

        logger.setLevel(level)

        if logger.handlers:
            AppLogger._logger = logger
            return

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )

        # File Handler

        file_handler = RotatingFileHandler(
            filename=log_path / log_filename,
            maxBytes=2 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )

        file_handler.setFormatter(formatter)

        # Console Handler

        console_handler = logging.StreamHandler()

        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        AppLogger._logger = logger

    # --------------------------------------------------
    # Logging Methods
    # --------------------------------------------------

    @property
    def logger(self):

        return AppLogger._logger

    def debug(self, message: str) -> None:

        self.logger.debug(message)

    def info(self, message: str) -> None:

        self.logger.info(message)

    def warning(self, message: str) -> None:

        self.logger.warning(message)

    def error(self, message: str) -> None:

        self.logger.error(message)

    def critical(self, message: str) -> None:

        self.logger.critical(message)

    def exception(self, message: str) -> None:

        self.logger.exception(message)