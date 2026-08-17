"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Settings
Purpose   : Application Configuration Manager
Production-safe settings storage for source and PyInstaller builds.
=========================================================
"""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path

from core.constants import (
    SETTINGS_FILE,
    DEFAULT_THEME,
    DEFAULT_MODE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
)


class Settings:
    """Central, backward-compatible application settings manager.

    Development:
        Uses the existing project settings file when it is writable.

    Production / PyInstaller:
        Stores mutable settings in the user's LocalAppData directory
        instead of attempting to write inside the bundled application.
    """

    DEFAULT_SETTINGS = {
        "application": {
            "theme": DEFAULT_THEME,
            "appearance": DEFAULT_MODE,
            "window_width": WINDOW_WIDTH,
            "window_height": WINDOW_HEIGHT,
            "remember_window_size": True,
        },
        "estimation": {
            "currency": "PKR",
            "decimal_places": 2,
            "length_unit": "m",
            "area_unit": "m²",
            "volume_unit": "m³",
            "steel_unit": "kg",
            "concrete_mix": "1:2:4",
            "cement_rate": 1650.0,
            "sand_rate": 800.0,
            "aggregate_rate": 1000.0,
            "steel_rate": 280.0,
            "skilled_labour_rate": 2500.0,
            "unskilled_labour_rate": 1250.0,

            # Labour productivity norms: quantity completed per labour day.
            "pcc_skilled_productivity": 1.0,
            "pcc_unskilled_productivity": 2.0,
            "rcc_skilled_productivity": 1.0,
            "rcc_unskilled_productivity": 2.0,
            "brickwork_skilled_productivity": 10.0,
            "brickwork_unskilled_productivity": 15.0,
            "plaster_skilled_productivity": 10.0,
            "plaster_unskilled_productivity": 15.0,
            "excavation_skilled_productivity": 8.0,
            "excavation_unskilled_productivity": 6.0,
            "footing_skilled_productivity": 1.0,
            "footing_unskilled_productivity": 2.0,
            "staircase_skilled_productivity": 1.0,
            "staircase_unskilled_productivity": 2.0,
        },
        "reports": {
            "default_export_format": "xlsx",
            "include_material_breakdown": True,
            "include_labour_breakdown": True,
            "default_remarks": "",
        },
        "database": {
            "auto_backup": True,
            "backup_interval_days": 7,
        },
        "logging": {
            "level": "INFO",
        },
    }

    APP_FOLDER_NAME = "Civil Estimate Suite Pro"

    def __init__(self, file=None):
        # An explicitly supplied path remains supported for compatibility.
        if file is not None:
            self.file = Path(file)
            self._seed_file = None
        else:
            self._seed_file = Path(SETTINGS_FILE)
            self.file = self._get_user_settings_path()

        self.settings = {}
        self.load()

    # =====================================================
    # PATH MANAGEMENT
    # =====================================================

    @classmethod
    def _get_user_data_root(cls) -> Path:
        """Return a writable per-user application data directory."""
        local_app_data = os.environ.get("LOCALAPPDATA")

        if local_app_data:
            return (
                Path(local_app_data)
                / cls.APP_FOLDER_NAME
            )

        user_profile = os.environ.get("USERPROFILE")
        if user_profile:
            return (
                Path(user_profile)
                / "AppData"
                / "Local"
                / cls.APP_FOLDER_NAME
            )

        # Cross-platform fallback for development/testing.
        return (
            Path.home()
            / ".local"
            / cls.APP_FOLDER_NAME
        )

    @classmethod
    def _get_user_settings_path(cls) -> Path:
        return cls._get_user_data_root() / "config" / "settings.json"

    def get_user_data_root(self) -> Path:
        """Return the writable application data root."""
        return self._get_user_data_root()

    # =====================================================
    # DEFAULTS / MERGE
    # =====================================================

    def _defaults(self):
        return copy.deepcopy(self.DEFAULT_SETTINGS)

    def _merge_defaults(self, current):
        defaults = self._defaults()

        if not isinstance(current, dict):
            return defaults

        def merge(dst, src):
            for key, value in src.items():
                if key not in dst:
                    dst[key] = copy.deepcopy(value)
                elif isinstance(value, dict) and isinstance(dst[key], dict):
                    merge(dst[key], value)

        merge(current, defaults)
        return current

    # =====================================================
    # LOAD / SAVE
    # =====================================================

    def _load_json(self, path: Path):
        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (
            OSError,
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ):
            return None

    def load(self):
        # First preference: the writable user settings file.
        loaded = self._load_json(self.file)

        # If no user settings exist, use the bundled/project settings
        # as a read-only seed. Never write back to that bundled file.
        if loaded is None and self._seed_file is not None:
            seed = self._seed_file.resolve()
            if seed != self.file.resolve():
                loaded = self._load_json(seed)

        if loaded is None:
            self.settings = self._defaults()
        else:
            self.settings = self._merge_defaults(loaded)

        # Always save to self.file, which is writable user storage unless
        # an explicit file path was deliberately supplied by the caller.
        self.save()

    def save(self):
        self.file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp_file = self.file.with_suffix(
            self.file.suffix + ".tmp"
        )

        with temp_file.open(
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                self.settings,
                f,
                indent=4,
                ensure_ascii=False,
            )
            f.flush()
            os.fsync(f.fileno())

        # Atomic replacement avoids leaving a half-written settings file.
        temp_file.replace(self.file)

    def reset(self):
        self.settings = self._defaults()
        self.save()

    # =====================================================
    # ACCESS
    # =====================================================

    def get(self, section, key=None, default=None):
        """
        Read a setting.

        Supported forms:
            get("application")
            get("application", "theme")
            get("application", "theme", "blue")

        Backward compatibility:
            get("application", {})
        is treated as:
            get("application", key=None, default={})
        """
        if isinstance(key, dict) and default is None:
            default = key
            key = None

        if key is None:
            value = self.settings.get(section, default)
            return copy.deepcopy(value)

        section_data = self.settings.get(section, {})

        if not isinstance(section_data, dict):
            return default

        return copy.deepcopy(
            section_data.get(key, default)
        )

    def set(self, section, key, value):
        if (
            section not in self.settings
            or not isinstance(
                self.settings[section],
                dict,
            )
        ):
            self.settings[section] = {}

        self.settings[section][key] = value

    def update(self, section, values: dict):
        if not isinstance(values, dict):
            raise TypeError(
                "Settings update values must be a dictionary."
            )

        if (
            section not in self.settings
            or not isinstance(
                self.settings[section],
                dict,
            )
        ):
            self.settings[section] = {}

        self.settings[section].update(values)

    def save_setting(self, section, key, value):
        self.set(section, key, value)
        self.save()


__all__ = ["Settings"]
