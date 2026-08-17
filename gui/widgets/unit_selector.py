from __future__ import annotations

import customtkinter as ctk

from services.unit_conversion_service import UnitConversionService


class UnitSelector(ctk.CTkFrame):
    """Reusable read-only engineering unit dropdown."""

    def __init__(self, master, family="volume", default=None, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.family = family
        self.command = command
        self.options = list(UnitConversionService.available_units(family))

        if default not in self.options:
            default = self.options[0] if self.options else ""

        self.variable = ctk.StringVar(value=default)

        ctk.CTkLabel(
            self, text="Unit", anchor="w",
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=0, column=0, padx=(6, 4), pady=5)

        self.combo = ctk.CTkComboBox(
            self, values=self.options, variable=self.variable,
            state="readonly", command=self._changed, width=120
        )
        self.combo.grid(row=0, column=1, padx=(0, 6), pady=5)

    def _changed(self, value):
        if callable(self.command):
            self.command(value)

    def get(self):
        return self.variable.get()

    def set(self, unit):
        if unit in self.options:
            self.variable.set(unit)

    def values(self):
        return tuple(self.options)


__all__ = ["UnitSelector"]
