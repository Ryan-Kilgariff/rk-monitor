from dataclasses import dataclass
from core.database import get_connection
@dataclass
class ScanComparison:
    current_scan_id: int
    previous_scan_id: int | None
    current_score: int | None
    previous_score: int | None
    score_change: int | None
    new_issues: list[str]
    resolved_issues: list[str]
    has_previous_scan: bool
class MonitoringService:
    def compare_latest(
        self,
        website_url: str,
    ) -> ScanComparison:
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
            website_id = website["id"]
            cursor.execute(
                """
                SELECT
                    id,
                    overall_score
                FROM scans
                WHERE website_id = ?
                ORDER BY scanned_at DESC, id DESC
                LIMIT 2
                """,
                (website_id,),
            )
            scans = cursor.fetchall()
            if not scans:
                raise ValueError(
                    "No scans found."
                )
            current_scan = scans[0]
            if len(scans) == 1:
                return ScanComparison(
                    current_scan_id=current_scan["id"],
                    previous_scan_id=None,
                    current_score=current_scan[
                        "overall_score"
                    ],
                    previous_score=None,
                    score_change=None,
                    new_issues=[],
                    resolved_issues=[],
                    has_previous_scan=False,
                )
            previous_scan = scans[1]
            current_issues = (
                self._get_issue_titles(
                    cursor,
                    current_scan["id"],
                )
            )
            previous_issues = (
                self._get_issue_titles(
                    cursor,
                    previous_scan["id"],
                )
            )
            new_issues = sorted(
                current_issues
                - previous_issues
            )
            resolved_issues = sorted(
                previous_issues
                - current_issues
            )
            current_score = current_scan[
                "overall_score"
            ]
            previous_score = previous_scan[
                "overall_score"
            ]
            score_change = None
            if (
                current_score is not None
                and previous_score is not None
            ):
                score_change = (
                    current_score
                    - previous_score
                )
            return ScanComparison(
                current_scan_id=current_scan["id"],
                previous_scan_id=previous_scan["id"],
                current_score=current_score,
                previous_score=previous_score,
                score_change=score_change,
                new_issues=new_issues,
                resolved_issues=resolved_issues,
                has_previous_scan=True,
            )
        finally:
            conn.close()
    def _get_issue_titles(
        self,
        cursor,
        scan_id: int,
    ) -> set[str]:
        cursor.execute(
            """
            SELECT title
            FROM issues
            WHERE scan_id = ?
            """,
            (scan_id,),
        )
        rows = cursor.fetchall()
        return {
            row["title"]
            for row in rows
        }