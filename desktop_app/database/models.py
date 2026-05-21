"""
AutoTrack — Data access layer.
All database CRUD operations for cars, repairs, users, etc.
"""

import sqlite3
from datetime import date, datetime
from typing import Optional
from desktop_app.database.db import get_connection, hash_password, verify_password


# ═══════════════════════════════════════════════════════════════
# USERS
# ═══════════════════════════════════════════════════════════════

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user, return user dict or None."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? AND is_active = 1",
        (username,)
    ).fetchone()
    conn.close()
    if row and verify_password(password, row["password_hash"]):
        return dict(row)
    return None


def get_all_users() -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, username, display_name, role, is_active, created_at FROM users ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_user(username: str, password: str, display_name: str, role: str) -> int:
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO users (username, password_hash, display_name, role)
           VALUES (?, ?, ?, ?)""",
        (username, hash_password(password), display_name, role)
    )
    conn.commit()
    uid = cursor.lastrowid
    conn.close()
    return uid


def update_user(user_id: int, **kwargs):
    conn = get_connection()
    if "password" in kwargs:
        kwargs["password_hash"] = hash_password(kwargs.pop("password"))
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [user_id]
    conn.execute(f"UPDATE users SET {sets} WHERE id = ?", vals)
    conn.commit()
    conn.close()


def delete_user(user_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════
# CARS
# ═══════════════════════════════════════════════════════════════

def get_all_cars(search: str = "", order_by: str = "brand") -> list:
    conn = get_connection()
    query = "SELECT * FROM cars"
    params = []
    if search:
        query += """ WHERE brand LIKE ? OR model LIKE ? OR plate LIKE ?
                     OR vin LIKE ? OR note LIKE ?"""
        s = f"%{search}%"
        params = [s, s, s, s, s]
    query += f" ORDER BY {order_by}"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_car(car_id: int) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM cars WHERE id = ?", (car_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_car(brand: str, model: str, plate: str, year: int,
               vin: str = "", mileage: int = 0, note: str = "",
               photo_path: str = "") -> int:
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO cars (brand, model, plate, vin, year, mileage, note, photo_path)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (brand, model, plate, vin, year, mileage, note, photo_path)
    )
    conn.commit()
    cid = cursor.lastrowid
    conn.close()
    return cid


def update_car(car_id: int, **kwargs) -> bool:
    conn = get_connection()
    kwargs["updated_at"] = datetime.now().isoformat()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [car_id]
    conn.execute(f"UPDATE cars SET {sets} WHERE id = ?", vals)
    conn.commit()
    conn.close()
    return True


def delete_car(car_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM cars WHERE id = ?", (car_id,))
    conn.commit()
    conn.close()


def get_car_count() -> int:
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM cars").fetchone()[0]
    conn.close()
    return count


# ═══════════════════════════════════════════════════════════════
# REPAIRS
# ═══════════════════════════════════════════════════════════════

def get_all_repairs(search: str = "", car_id: int = None,
                    date_from: str = None, date_to: str = None) -> list:
    conn = get_connection()
    query = """
        SELECT r.*, c.brand, c.model, c.plate
        FROM repairs r
        JOIN cars c ON r.car_id = c.id
        WHERE 1=1
    """
    params = []
    if search:
        s = f"%{search}%"
        query += """ AND (r.repair_type LIKE ? OR r.description LIKE ?
                     OR r.responsible LIKE ? OR c.brand LIKE ?
                     OR c.model LIKE ? OR c.plate LIKE ?)"""
        params.extend([s, s, s, s, s, s])
    if car_id:
        query += " AND r.car_id = ?"
        params.append(car_id)
    if date_from:
        query += " AND r.date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND r.date <= ?"
        params.append(date_to)
    query += " ORDER BY r.date DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_repairs_for_car(car_id: int) -> list:
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM repairs WHERE car_id = ? ORDER BY date DESC""",
        (car_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_repair(repair_id: int) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute(
        """SELECT r.*, c.brand, c.model, c.plate
           FROM repairs r JOIN cars c ON r.car_id = c.id
           WHERE r.id = ?""",
        (repair_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def create_repair(car_id: int, repair_type: str, repair_date: str,
                  category: str = "", mileage_at_repair: int = 0,
                  cost: float = 0.0, description: str = "",
                  responsible: str = "", next_date: str = None,
                  next_mileage: int = 0) -> int:
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO repairs
           (car_id, repair_type, category, date, mileage_at_repair,
            cost, description, responsible, next_date, next_mileage)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (car_id, repair_type, category, repair_date, mileage_at_repair,
         cost, description, responsible, next_date, next_mileage)
    )
    conn.commit()
    rid = cursor.lastrowid
    conn.close()
    return rid


def update_repair(repair_id: int, **kwargs) -> bool:
    conn = get_connection()
    kwargs["updated_at"] = datetime.now().isoformat()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [repair_id]
    conn.execute(f"UPDATE repairs SET {sets} WHERE id = ?", vals)
    conn.commit()
    conn.close()
    return True


def delete_repair(repair_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM repairs WHERE id = ?", (repair_id,))
    conn.commit()
    conn.close()


def get_repair_count() -> int:
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM repairs").fetchone()[0]
    conn.close()
    return count


def get_total_cost(car_id: int = None) -> float:
    conn = get_connection()
    if car_id:
        row = conn.execute(
            "SELECT COALESCE(SUM(cost), 0) FROM repairs WHERE car_id = ?",
            (car_id,)
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT COALESCE(SUM(cost), 0) FROM repairs"
        ).fetchone()
    conn.close()
    return row[0]


# ═══════════════════════════════════════════════════════════════
# REMINDERS
# ═══════════════════════════════════════════════════════════════

def get_upcoming_repairs(days_ahead: int = 30) -> list:
    """Get repairs with next_date within the given days."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT r.*, c.brand, c.model, c.plate,
                  julianday(r.next_date) - julianday('now') as days_left
           FROM repairs r
           JOIN cars c ON r.car_id = c.id
           WHERE r.next_date IS NOT NULL
             AND r.next_date != ''
             AND julianday(r.next_date) - julianday('now') <= ?
           ORDER BY r.next_date ASC""",
        (days_ahead,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_overdue_repairs() -> list:
    """Get repairs that are past their next_date."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT r.*, c.brand, c.model, c.plate,
                  julianday('now') - julianday(r.next_date) as days_overdue
           FROM repairs r
           JOIN cars c ON r.car_id = c.id
           WHERE r.next_date IS NOT NULL
             AND r.next_date != ''
             AND r.next_date < date('now')
           ORDER BY r.next_date ASC"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_overdue_count() -> int:
    conn = get_connection()
    count = conn.execute(
        """SELECT COUNT(*) FROM repairs
           WHERE next_date IS NOT NULL AND next_date != ''
             AND next_date < date('now')"""
    ).fetchone()[0]
    conn.close()
    return count


def get_soon_count(days: int = 31) -> int:
    conn = get_connection()
    count = conn.execute(
        """SELECT COUNT(*) FROM repairs
           WHERE next_date IS NOT NULL AND next_date != ''
             AND next_date >= date('now')
             AND julianday(next_date) - julianday('now') <= ?""",
        (days,)
    ).fetchone()[0]
    conn.close()
    return count


# ═══════════════════════════════════════════════════════════════
# REPAIR TYPES
# ═══════════════════════════════════════════════════════════════

def get_repair_types() -> list:
    conn = get_connection()
    rows = conn.execute("SELECT name FROM repair_types ORDER BY name").fetchall()
    conn.close()
    return [r["name"] for r in rows]


def add_repair_type(name: str):
    conn = get_connection()
    conn.execute("INSERT OR IGNORE INTO repair_types (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════
# ACTION LOG
# ═══════════════════════════════════════════════════════════════

def log_action(user_id: int, username: str, action: str, details: str = ""):
    conn = get_connection()
    conn.execute(
        """INSERT INTO action_log (user_id, username, action, details)
           VALUES (?, ?, ?, ?)""",
        (user_id, username, action, details)
    )
    conn.commit()
    conn.close()


def get_action_log(limit: int = 100) -> list:
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM action_log ORDER BY timestamp DESC LIMIT ?""",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════════
# SETTINGS
# ═══════════════════════════════════════════════════════════════

def get_setting(key: str, default: str = "") -> str:
    conn = get_connection()
    row = conn.execute(
        "SELECT value FROM settings WHERE key = ?", (key,)
    ).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key: str, value: str):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        (key, value)
    )
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════
# DASHBOARD STATS
# ═══════════════════════════════════════════════════════════════

def get_dashboard_stats() -> dict:
    """Return all dashboard statistics."""
    return {
        "total_cars": get_car_count(),
        "total_repairs": get_repair_count(),
        "overdue_count": get_overdue_count(),
        "soon_count": get_soon_count(),
        "total_cost": get_total_cost(),
    }
