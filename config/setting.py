"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Settings
Purpose   : Application Configuration Manager
Author    : OpenAI + Moula Bakhsh
Version   : 4.0.0
=========================================================
"""

from __future__ import annotations

import json
from pathlib import Path

from core.constants import (
    SETTINGS_FILE,
    DEFAULT_THEME,
    DEFAULT_MODE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
)


class Settings:
    """
    Central Settings Manager

    Responsibilities
    ----------------
    ✔ Load settings
    ✔ Save settings
    ✔ Reset defaults
    ✔ Get values
    ✔ Set values
    """

    DEFAULT_SETTINGS = {

        "application": {

            "theme": DEFAULT_THEME,
            "appearance": DEFAULT_MODE,

            "window_width": WINDOW_WIDTH,
            "window_height": WINDOW_HEIGHT,

            "remember_window_size": True
        },

        "database": {

            "auto_backup": True,
            "backup_interval_days": 7

        },

        "reports": {

            "default_export_format": "xlsx"

        },

        "logging": {

            "level": "INFO"

        }

    }

    # --------------------------------------------------

    def __init__(self):

        self.file = Path(SETTINGS_FILE)

        self.settings = {}

        self.load()

    # --------------------------------------------------

    def load(self):

        if self.file.exists():

            with open(
                self.file,
                "r",
                encoding="utf-8"
            ) as f:

                self.settings = json.load(f)

        else:

            self.settings = self.DEFAULT_SETTINGS.copy()

            self.save()

    # --------------------------------------------------

    def save(self):

        self.file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            self.file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.settings,
                f,
                indent=4
            )

    # --------------------------------------------------

    def reset(self):

        self.settings = self.DEFAULT_SETTINGS.copy()

        self.save()

    # --------------------------------------------------

    def get(self, section, key=None, default=None):

        if key is None:

            return self.settings.get(
                section,
                default
            )

        return self.settings.get(
            section,
            {}
        ).get(
            key,
            default
        )

    # --------------------------------------------------

    def set(self, section, key, value):

        if section not in self.settings:

            self.settings[section] = {}

        self.settings[section][key] = value

    # --------------------------------------------------

    def update(self, section, values: dict):

        if section not in self.settings:

            self.settings[section] = {}

        self.settings[section].update(values)

    # --------------------------------------------------

    def save_setting(
        self,
        section,
        key,
        value
    ):

        self.set(
            section,
            key,
            value
        )

        self.save()