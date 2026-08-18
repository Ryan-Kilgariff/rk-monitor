from dataclasses import dataclass
from datetime import datetime, timedelta
from core.database import get_connection
@dataclass
class MonitoredClient:
    website_id: int
    name: str | None
    url: str
    is_active_client: bool
    monitoring_frequency: str | None
@dataclass
class MonitoringHistoryEntry:
    scan_id: int
    commercial_score: int
    scanned_at: str
@dataclass
class MonitoringDueStatus:
    website_id: int
    name: str | None
    url: str
    monitoring_frequency: str
    last_scan_at: str | None
    next_due_at: str | None
    is_due: bool
class ClientMonitoringService:
    VALID_FREQUENCIES = {
        "WEEKLY",
        "FORTNIGHTLY",
        "MONTHLY",
        "QUARTERLY",
    }
    FREQUENCY_DAYS = {
        "WEEKLY": 7,
        "FORTNIGHTLY": 14,
        "MONTHLY": 30,
        "QUARTERLY": 90,
    }
    def activate(
        self,
        website_url: str,
        monitoring_frequency: str,
    ) -> MonitoredClient:
        monitoring_frequency = (
            monitoring_frequency
            .strip()
            .upper()
        )
        if (
            monitoring_frequency
            not in self.VALID_FREQUENCIES
        ):
            raise ValueError(
                "Invalid monitoring frequency."
            )
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    url
                FROM websites
                WHERE url = ?
                """,
                (website_url,),
            )
            website = cursor.fetchone()
            if website is None:
                raise ValueError(
                    "Website not found. "
                    "Run a scan first."
                )
            cursor.execute(
                """
                UPDATE websites
                SET
                    is_active_client = 1,
                    monitoring_frequency = ?
                WHERE id = ?
                """,
                (
                    monitoring_frequency,
                    website["id"],
                ),
            )
            conn.commit()
            return MonitoredClient(
                website_id=website["id"],
                name=website["name"],
                url=website["url"],
                is_active_client=True,
                monitoring_frequency=(
                    monitoring_frequency
                ),
            )
        finally:
            conn.close()
    def list_active(
        self,
    ) -> list[MonitoredClient]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    url,
                    is_active_client,
                    monitoring_frequency
                FROM websites
                WHERE is_active_client = 1
                ORDER BY name, url
                """
            )
            rows = cursor.fetchall()
            return [
                MonitoredClient(
                    website_id=row["id"],
                    name=row["name"],
                    url=row["url"],
                    is_active_client=bool(
                        row["is_active_client"]
                    ),
                    monitoring_frequency=(
                        row["monitoring_frequency"]
                    ),
                )
                for row in rows
            ]
        finally:
            conn.close()
    def get_history(
        self,
        website_url: str,
        limit: int = 10,
    ) -> list[MonitoringHistoryEntry]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id
                FROM websites
                WHERE url = ?
                """,
                (website_url,),
            )
            website = cursor.fetchone()
            if website is None:
                raise ValueError(
                    "Website not found."
                )
            cursor.execute(
                """
                SELECT
                    id,
                    commercial_score,
                    scanned_at
                FROM scans
                WHERE website_id = ?
                AND commercial_score IS NOT NULL
                ORDER BY scanned_at DESC, id DESC
                LIMIT ?
                """,
                (
                    website["id"],
                    limit,
                ),
            )
            rows = cursor.fetchall()
            return [
                MonitoringHistoryEntry(
                    scan_id=row["id"],
                    commercial_score=row[
                        "commercial_score"
                    ],
                    scanned_at=row["scanned_at"],
                )
                for row in rows
            ]
        finally:
            conn.close()
    def get_due_statuses(
        self,
    ) -> list[MonitoringDueStatus]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    websites.id,
                    websites.name,
                    websites.url,
                    websites.monitoring_frequency,
                    (
                        SELECT scans.scanned_at
                        FROM scans
                        WHERE scans.website_id = websites.id
                        AND scans.commercial_score IS NOT NULL
                        ORDER BY
                            scans.scanned_at DESC,
                            scans.id DESC
                        LIMIT 1
                    ) AS last_scan_at
                FROM websites
                WHERE websites.is_active_client = 1
                ORDER BY websites.name, websites.url
                """
            )
            rows = cursor.fetchall()
            now = datetime.now()
            statuses = []
            for row in rows:
                frequency = row[
                    "monitoring_frequency"
                ]
                last_scan_at = row[
                    "last_scan_at"
                ]
                if last_scan_at is None:
                    next_due_at = None
                    is_due = True
                else:
                    last_scan = datetime.strptime(
                        last_scan_at,
                        "%Y-%m-%d %H:%M:%S",
                    )
                    interval_days = (
                        self.FREQUENCY_DAYS[
                            frequency
                        ]
                    )
                    next_due = (
                        last_scan
                        + timedelta(
                            days=interval_days
                        )
                    )
                    next_due_at = (
                        next_due.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    )
                    is_due = now >= next_due
                statuses.append(
                    MonitoringDueStatus(
                        website_id=row["id"],
                        name=row["name"],
                        url=row["url"],
                        monitoring_frequency=frequency,
                        last_scan_at=last_scan_at,
                        next_due_at=next_due_at,
                        is_due=is_due,
                    )
                )
            return statuses
        finally:
            conn.close()
    def deactivate(
        self,
        website_url: str,
    ) -> MonitoredClient:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    url
                FROM websites
                WHERE url = ?
                """,
                (website_url,),
            )
            website = cursor.fetchone()
            if website is None:
                raise ValueError(
                    "Website not found."
                )
            cursor.execute(
                """
                UPDATE websites
                SET
                    is_active_client = 0,
                    monitoring_frequency = NULL
                WHERE id = ?
                """,
                (website["id"],),
            )
            conn.commit()
            return MonitoredClient(
                website_id=website["id"],
                name=website["name"],
                url=website["url"],
                is_active_client=False,
                monitoring_frequency=None,
            )
        finally:
            conn.close()