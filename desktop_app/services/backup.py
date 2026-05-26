"""
AutoTrack — Backup service.
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
from desktop_app.database.db import get_db_path
from desktop_app.database.models import get_setting


def get_default_backup_dir() -> str:
    """Desktop/AutoTrack_Backups — so the user immediately sees the file."""
    return str(Path.home() / "Desktop" / "AutoTrack_Backups")


def get_backup_dir():
    backup_dir = get_setting("backup_dir", "")
    if not backup_dir:
        backup_dir = get_default_backup_dir()
    Path(backup_dir).mkdir(parents=True, exist_ok=True)
    return backup_dir


def create_backup() -> str:
    db_path = get_db_path()
    backup_dir = get_backup_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"autotrack_backup_{timestamp}.db")
    shutil.copy2(db_path, backup_path)
    # Keep only last 10 backups
    backups = sorted(Path(backup_dir).glob("autotrack_backup_*.db"), reverse=True)
    for old in backups[10:]:
        old.unlink()
    return backup_path


def restore_backup(backup_path: str):
    db_path = get_db_path()
    # Create safety backup first
    safety = db_path + ".safety_backup"
    shutil.copy2(db_path, safety)
    try:
        shutil.copy2(backup_path, db_path)
    except Exception:
        shutil.copy2(safety, db_path)
        raise
    finally:
        if os.path.exists(safety):
            os.remove(safety)


def list_backups() -> list:
    backup_dir = get_backup_dir()
    backups = sorted(Path(backup_dir).glob("autotrack_backup_*.db"), reverse=True)
    return [{"path": str(b), "name": b.name, "size": b.stat().st_size,
             "date": datetime.fromtimestamp(b.stat().st_mtime)} for b in backups]
