from dataclasses import dataclass
from core.database import get_connection
from services.monitoring_service import ScanComparison
@dataclass
class ClientEscalation:
    level: str
    reasons: list[str]
    requires_contact: bool
class ClientEscalationService:
    def assess(
        self,
        comparison: ScanComparison,
    ) -> ClientEscalation:
        reasons: list[str] = []
        if comparison.current_score is None:
            return ClientEscalation(
                level="AMBER",
                reasons=[
                    (
                        "The latest monitoring scan "
                        "could not produce a complete "
                        "commercial assessment."
                    )
                ],
                requires_contact=False,
            )
        new_issue_details = (
            self._get_new_issue_details(
                comparison
            )
        )
        red_issue_titles = []
        amber_issue_titles = []
        for issue in new_issue_details:
            if issue["severity"] == "HIGH":
                red_issue_titles.append(
                    issue["title"]
                )
            elif issue["severity"] == "MEDIUM":
                amber_issue_titles.append(
                    issue["title"]
                )
        if red_issue_titles:
            reasons.extend(
                (
                    f"New HIGH issue: {title}"
                    for title in red_issue_titles
                )
            )
        if (
            comparison.score_change is not None
            and comparison.score_change <= -10
        ):
            reasons.append(
                (
                    "Commercial Website Score "
                    f"dropped by "
                    f"{abs(comparison.score_change)} "
                    "points."
                )
            )
        if reasons:
            return ClientEscalation(
                level="RED",
                reasons=reasons,
                requires_contact=True,
            )
        if amber_issue_titles:
            reasons.extend(
                (
                    f"New MEDIUM issue: {title}"
                    for title in amber_issue_titles
                )
            )
        if (
            comparison.score_change is not None
            and comparison.score_change <= -5
        ):
            reasons.append(
                (
                    "Commercial Website Score "
                    f"dropped by "
                    f"{abs(comparison.score_change)} "
                    "points."
                )
            )
        if reasons:
            return ClientEscalation(
                level="AMBER",
                reasons=reasons,
                requires_contact=False,
            )
        return ClientEscalation(
            level="GREEN",
            reasons=[
                (
                    "No material website changes "
                    "require escalation."
                )
            ],
            requires_contact=False,
        )
    def _get_new_issue_details(
        self,
        comparison: ScanComparison,
    ) -> list:
        if not comparison.new_issues:
            return []
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    title,
                    severity,
                    category,
                    issue_code,
                    confidence,
                    requires_review,
                    review_status
                FROM issues
                WHERE scan_id = ?
                """,
                (
                    comparison.current_scan_id,
                ),
            )
            rows = cursor.fetchall()
            new_titles = set(
                comparison.new_issues
            )
            return [
                row
                for row in rows
                if row["title"] in new_titles
                and (
                    not row["requires_review"]
                    or row["review_status"]
                    == "CONFIRMED"
                )
            ]
        finally:
            conn.close()