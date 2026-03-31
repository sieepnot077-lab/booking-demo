import os
import sqlite3
import tempfile
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_DIR = Path(tempfile.gettempdir()) / "booking_demo"
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "booking.db"
SHARED_MEMORY_URI = "file:booking_demo?mode=memory&cache=shared"
HISTORY_STATUSES = ("completed", "cancelled")
_use_memory_db = False
_keeper_connection = None


def get_connection():
    global _keeper_connection

    if _use_memory_db:
        if _keeper_connection is None:
            _keeper_connection = sqlite3.connect(SHARED_MEMORY_URI, uri=True)
            _keeper_connection.row_factory = sqlite3.Row
        connection = sqlite3.connect(SHARED_MEMORY_URI, uri=True)
    else:
        db_path = os.environ.get("BOOKING_DB_PATH", str(DEFAULT_DB_PATH))
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(db_path)

    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    global _use_memory_db

    try:
        _create_tables()
    except sqlite3.OperationalError:
        _use_memory_db = True
        _create_tables()


def _create_tables():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                booking_time TEXT NOT NULL,
                note TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


def create_appointment(customer_name, phone, booking_date, booking_time, note=""):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO appointments (
                customer_name,
                phone,
                booking_date,
                booking_time,
                note,
                status
            )
            VALUES (?, ?, ?, ?, ?, 'pending')
            """,
            (customer_name, phone, booking_date, booking_time, note),
        )
        connection.commit()
        return cursor.lastrowid


def get_appointment(appointment_id):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM appointments WHERE id = ?",
            (appointment_id,),
        ).fetchone()
        return dict(row) if row else None


def get_appointments(status=None, booking_date=None, include_history=False):
    query = "SELECT * FROM appointments WHERE 1 = 1"
    params = []

    if include_history:
        query += " AND status IN (?, ?)"
        params.extend(HISTORY_STATUSES)
    else:
        query += " AND status NOT IN (?, ?)"
        params.extend(HISTORY_STATUSES)

    if status:
        query += " AND status = ?"
        params.append(status)

    if booking_date:
        query += " AND booking_date = ?"
        params.append(booking_date)

    query += " ORDER BY booking_date ASC, booking_time ASC, id DESC"

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def update_appointment_status(appointment_id, status):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE appointments
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, appointment_id),
        )
        connection.commit()
        return cursor.rowcount > 0
