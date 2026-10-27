
import os
import sqlite3

DATABASE = os.environ.get("CLINIC_DATABASE", "clinic.db")


def get_db_connection():
    connection = sqlite3.connect(DATABASE, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    connection = get_db_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clinic_id TEXT NOT NULL,
                starts_at TEXT NOT NULL,
                ends_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'available'
                    CHECK(status IN ('available', 'booked', 'cancelled')),
                CHECK(ends_at > starts_at)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slot_id INTEGER NOT NULL,
                patient_name TEXT NOT NULL,
                patient_email TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'confirmed'
                    CHECK(status IN ('confirmed', 'cancelled')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (slot_id) REFERENCES slots(id)
            )
        """)

        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            one_confirmed_booking_per_slot
            ON bookings (slot_id)
            WHERE status = 'confirmed'
        """)

        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
