"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Helpers
Purpose   : Common Utility Functions
Author    : OpenAI + Moula Bakhsh
Version   : 4.0.0
=========================================================
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any


# ==========================================================
# Date & Time
# ==========================================================

def current_datetime() -> str:
    """Return current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def current_date() -> str:
    """Return current date."""
    return datetime.now().strftime("%Y-%m-%d")


def current_time() -> str:
    """Return current time."""
    return datetime.now().strftime("%H:%M:%S")


# ==========================================================
# Directory Helpers
# ==========================================================

def ensure_directory(path: str | Path) -> Path:
    """
    Create directory if it does not exist.
    """
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


# ==========================================================
# String Helpers
# ==========================================================

def clean_text(text: Any) -> str:
    """
    Convert any value into a cleaned string.
    """
    if text is None:
        return ""

    return str(text).strip()


def title_case(text: Any) -> str:
    """
    Convert text into title case.
    """
    return clean_text(text).title()


# ==========================================================
# Number Helpers
# ==========================================================

def to_float(value: Any, default: float = 0.0) -> float:
    """
    Safe float conversion.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def to_int(value: Any, default: int = 0) -> int:
    """
    Safe integer conversion.
    """
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def round2(value: Any) -> float:
    """
    Round value to two decimal places.
    """
    return round(to_float(value), 2)


# ==========================================================
# Currency / Quantity
# ==========================================================

def format_quantity(value: Any) -> str:
    """
    Format quantity with 3 decimal places.
    """
    return f"{to_float(value):,.3f}"


def format_amount(value: Any) -> str:
    """
    Format amount with 2 decimal places.
    """
    return f"{to_float(value):,.2f}"


# ==========================================================
# Validation
# ==========================================================

def is_empty(value: Any) -> bool:
    """
    Check whether value is empty.
    """
    return clean_text(value) == ""


def has_value(value: Any) -> bool:
    """
    Check whether value contains data.
    """
    return not is_empty(value)


# ==========================================================
# File Helpers
# ==========================================================

def file_exists(path: str | Path) -> bool:
    """
    Check if a file exists.
    """
    return Path(path).exists()


def file_size(path: str | Path) -> int:
    """
    Return file size in bytes.
    """
    p = Path(path)

    if not p.exists():
        return 0

    return p.stat().st_size