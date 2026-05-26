"""
AutoTrack — Database initialization and connection management.
SQLite database with automatic schema creation and migrations.
"""

import os
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path

import sys

def get_db_path():
    """Return the path to the SQLite database file."""
    # If compiled with PyInstaller, use user's AppData to avoid permission errors in Program Files
    if getattr(sys, 'frozen', False):
        if sys.platform == "win32":
            base_dir = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "AutoTrack"
        elif sys.platform == "darwin":
            base_dir = Path.home() / "Library" / "Application Support" / "AutoTrack"
        else:
            base_dir = Path.home() / ".autotrack"
    else:
        # During development, store locally
        base_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent

    data_dir = base_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return str(data_dir / "autotrack.db")


def get_connection(db_path=None):
    """Create and return a database connection."""
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def close_all_connections():
    """Force-close any cached SQLite connections.
    This is needed on Windows before overwriting the DB file."""
    import gc
    gc.collect()  # Force garbage collection to release any lingering connections


def init_db(db_path=None):
    """Initialize database schema (create tables if they don't exist)."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            display_name TEXT DEFAULT '',
            role TEXT NOT NULL DEFAULT 'viewer'
                CHECK(role IN ('admin', 'operator', 'viewer')),
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            plate TEXT NOT NULL,
            vin TEXT DEFAULT '',
            year INTEGER NOT NULL,
            mileage INTEGER DEFAULT 0,
            note TEXT DEFAULT '',
            photo_path TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS repair_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS repairs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER NOT NULL,
            repair_type TEXT NOT NULL,
            category TEXT DEFAULT '',
            date DATE NOT NULL,
            mileage_at_repair INTEGER DEFAULT 0,
            cost REAL DEFAULT 0.0,
            description TEXT DEFAULT '',
            responsible TEXT DEFAULT '',
            next_date DATE,
            next_mileage INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS action_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT DEFAULT '',
            action TEXT NOT NULL,
            details TEXT DEFAULT '',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT DEFAULT ''
        );

        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_cars_brand ON cars(brand);
        CREATE INDEX IF NOT EXISTS idx_cars_plate ON cars(plate);
        CREATE INDEX IF NOT EXISTS idx_cars_vin ON cars(vin);
        CREATE INDEX IF NOT EXISTS idx_repairs_car_id ON repairs(car_id);
        CREATE INDEX IF NOT EXISTS idx_repairs_date ON repairs(date);
        CREATE INDEX IF NOT EXISTS idx_repairs_next_date ON repairs(next_date);
        CREATE INDEX IF NOT EXISTS idx_action_log_timestamp ON action_log(timestamp);
    """)

    # Seed default repair types
    default_types = [
        "Замена масла", "Ходовая часть", "Двигатель",
        "Тормозная система", "Электрика", "Диагностика",
        "Шиномонтаж", "Кузов", "ТО (плановое)", "Другое"
    ]
    for t in default_types:
        cursor.execute(
            "INSERT OR IGNORE INTO repair_types (name) VALUES (?)", (t,)
        )

    # Create default admin user if no users exist
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        password_hash = hash_password("admin")
        cursor.execute(
            """INSERT INTO users (username, password_hash, display_name, role)
               VALUES (?, ?, ?, ?)""",
            ("admin", password_hash, "Администратор", "admin")
        )

    # Default settings
    defaults = {
        "theme": "light",
        "auto_backup": "1",
        "backup_dir": str(Path.home() / "Desktop" / "AutoTrack_Backups"),
        "reminder_days_warning": "30",
        "reminder_days_critical": "7",
    }
    for key, value in defaults.items():
        cursor.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )

    # Migrate old backup_dir (data/backups) → Desktop/AutoTrack_Backups
    old_backup_dir = str(Path(get_db_path()).parent / "backups")
    row = cursor.execute(
        "SELECT value FROM settings WHERE key = 'backup_dir'"
    ).fetchone()
    if row and row[0] == old_backup_dir:
        cursor.execute(
            "UPDATE settings SET value = ? WHERE key = 'backup_dir'",
            (defaults["backup_dir"],)
        )

    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a salt."""
    import hashlib
    import secrets
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    try:
        salt, hashed = password_hash.split(":")
        return hashlib.sha256((salt + password).encode()).hexdigest() == hashed
    except (ValueError, AttributeError):
        return False


def migrate_from_django(django_db_path: str, new_db_path: str = None):
    """Migrate data from the existing Django SQLite database."""
    if new_db_path is None:
        new_db_path = get_db_path()

    init_db(new_db_path)

    django_conn = sqlite3.connect(django_db_path)
    django_conn.row_factory = sqlite3.Row

    new_conn = get_connection(new_db_path)
    cursor = new_conn.cursor()

    # Migrate cars
    try:
        django_cars = django_conn.execute(
            "SELECT id, marka, model, gos_munber, year, note FROM cars_car"
        ).fetchall()
        for car in django_cars:
            cursor.execute(
                """INSERT OR REPLACE INTO cars (id, brand, model, plate, year, note)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (car["id"], car["marka"], car["model"],
                 car["gos_munber"], car["year"], car["note"] or "")
            )
    except sqlite3.OperationalError:
        pass  # Table doesn't exist in Django DB

    # Migrate repairs
    try:
        django_fixes = django_conn.execute(
            """SELECT id, car_id, repair_type, date, next_date, description
               FROM cars_fix"""
        ).fetchall()
        for fix in django_fixes:
            cursor.execute(
                """INSERT OR REPLACE INTO repairs
                   (id, car_id, repair_type, date, next_date, description)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (fix["id"], fix["car_id"], fix["repair_type"],
                 fix["date"], fix["next_date"], fix["description"] or "")
            )
    except sqlite3.OperationalError:
        pass

    new_conn.commit()
    django_conn.close()
    new_conn.close()
