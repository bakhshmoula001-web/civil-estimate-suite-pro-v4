"""Civil Estimate Suite Pro v4.0 - SQLite Backup Service."""

from __future__ import annotations

import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


class BackupService:
    def __init__(self, database_path, backup_dir):
        self.database_path = Path(database_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self):
        if not self.database_path.exists():
            raise FileNotFoundError(f"Database not found: {self.database_path}")

        target = self.backup_dir / (
            f"civil_estimate_suite_{datetime.now():%Y-%m-%d_%H-%M-%S}.db"
        )
        source = sqlite3.connect(
            f"file:{self.database_path.resolve()}?mode=ro",
            uri=True,
        )
        destination = sqlite3.connect(str(target))
        try:
            with destination:
                source.backup(destination)
        finally:
            destination.close()
            source.close()
        return target

    def list_backups(self):
        return sorted(
            self.backup_dir.glob("civil_estimate_suite_*.db"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

    def delete_backup(self, path):
        target = Path(path).resolve()
        if target.parent != self.backup_dir.resolve():
            raise ValueError("Invalid backup file location.")
        if target.exists():
            target.unlink()

    def restore_backup(self, path):
        source = Path(path).resolve()
        if source.parent != self.backup_dir.resolve():
            raise ValueError("Invalid backup file location.")
        if not source.exists():
            raise FileNotFoundError("Selected backup does not exist.")
        if source.suffix.lower() != ".db":
            raise ValueError("Only SQLite database backups can be restored.")

        if self.database_path.exists():
            safety = self.backup_dir / (
                f"pre_restore_{datetime.now():%Y-%m-%d_%H-%M-%S}.db"
            )
            shutil.copy2(self.database_path, safety)

        shutil.copy2(source, self.database_path)


__all__ = ["BackupService"]
