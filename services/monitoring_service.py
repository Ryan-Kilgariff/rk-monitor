from dataclasses import dataclass
from core.database import get_connection
@dataclass
@dataclass
class ScanComparison:
    current_scan_id: int
    previous_scan_id: int | None
    current_score: int | None
    previous_score: int | None
    score_change: int | None
    current_detected_score: int | None
    previous_detected_score: int | None
    detected_score_change: int | None
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
                    detected_score,
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
                    current_detected_score=current_scan[
                        "detected_score"
                    ],
                    previous_detected_score=None,
                    detected_score_change=None,
                    new_issues=[],
                    resolved_issues=[],
                    has_previous_scan=False,
                )
            previous_scan = scans[1]
            current_issues = (
                self._get_issue_map(
                    cursor,
                    current_scan["id"],
                )
            )
            previous_issues = (
                self._get_issue_map(
                    cursor,
                    previous_scan["id"],
                )
            )
            current_keys = set(
                current_issues.keys()
            )
            previous_keys = set(
                previous_issues.keys()
            )
            new_issues = sorted(
                current_issues[key]
                for key in (
                    current_keys
                    - previous_keys
                )
            )
            resolved_issues = sorted(
                previous_issues[key]
                for key in (
                    previous_keys
                    - current_keys
                )
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
            current_detected_score = current_scan[
                "detected_score"
            ]
            previous_detected_score = previous_scan[
                "detected_score"
            ]
            detected_score_change = None
            if (
                current_detected_score is not None
                and previous_detected_score is not None
            ):
                detected_score_change = (
                    current_detected_score
                    - previous_detected_score
                )
            return ScanComparison(
                current_scan_id=current_scan["id"],
                previous_scan_id=previous_scan["id"],
                current_score=current_score,
                previous_score=previous_score,
                score_change=score_change,
                current_detected_score=(
                    current_detected_score
                ),
                previous_detected_score=(
                    previous_detected_score
                ),
                detected_score_change=(
                    detected_score_change
                ),
                new_issues=new_issues,
                resolved_issues=resolved_issues,
                has_previous_scan=True,
            )
        finally:
            conn.close()
    def _get_issue_map(
        self,
        cursor,
        scan_id: int,
    ) -> dict[str, str]:
        cursor.execute(
            """
            SELECT title, issue_code
            FROM issues
            WHERE scan_id = ?
            """,
            (scan_id,),
        )
        rows = cursor.fetchall()
        issue_map: dict[str, str] = {}
        for row in rows:
            issue_code = row["issue_code"]
            title = row["title"]
            identity = (
                issue_code
                if issue_code
                else f"title:{title}"
            )
            issue_map[identity] = title
        return issue_map