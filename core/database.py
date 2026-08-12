from pathlib import Path
import sqlite3
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "rk_monitor.db"
def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn
def initialize_database() -> None:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS websites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                url TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website_id INTEGER NOT NULL,
                status_code INTEGER,
                response_time REAL,
                page_title TEXT,
                has_https INTEGER NOT NULL DEFAULT 0,
                has_mobile_viewport INTEGER NOT NULL DEFAULT 0,
                has_google_analytics INTEGER NOT NULL DEFAULT 0,
                ssl_verification_failed INTEGER NOT NULL DEFAULT 0,
                ssl_error_message TEXT,
                booking_provider TEXT,
                booking_links_found INTEGER NOT NULL DEFAULT 0,
                internal_links_found INTEGER NOT NULL DEFAULT 0,
                broken_links_found INTEGER NOT NULL DEFAULT 0,
                overall_score INTEGER,
                scan_successful INTEGER NOT NULL DEFAULT 0,
                error_message TEXT,
                scanned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (website_id)
                    REFERENCES websites(id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                severity TEXT NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                evidence TEXT,
                commercial_impact TEXT,
                recommended_action TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scan_id)
                    REFERENCES scans(id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()