from dataclasses import dataclass
from core.database import get_connection
@dataclass
class PendingIssueReview:
    issue_id: int
    website_url: str
    title: str
    severity: str
    category: str
    confidence: str
    evidence: str | None
class IssueReviewService:
    VALID_STATUSES = {
        "PENDING",
        "CONFIRMED",
        "FALSE_POSITIVE",
        "IGNORED",
        "NOT_REQUIRED",
    }
    def get_pending_reviews(
        self,
    ) -> list[PendingIssueReview]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    issues.id AS issue_id,
                    websites.url AS website_url,
                    issues.title,
                    issues.severity,
                    issues.category,
                    issues.confidence,
                    issues.evidence
                FROM issues
                JOIN scans
                    ON issues.scan_id = scans.id
                JOIN websites
                    ON scans.website_id = websites.id
                WHERE issues.review_status = 'PENDING'
                ORDER BY issues.id DESC
                """
            )
            rows = cursor.fetchall()
            return [
                PendingIssueReview(
                    issue_id=row["issue_id"],
                    website_url=row["website_url"],
                    title=row["title"],
                    severity=row["severity"],
                    category=row["category"],
                    confidence=(
                        row["confidence"]
                        or "UNKNOWN"
                    ),
                    evidence=row["evidence"],
                )
                for row in rows
            ]
        finally:
            conn.close()
    def get_latest_review_statuses(
        self,
        website_url: str,
    ) -> dict[str, str]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    issues.issue_code,
                    issues.review_status
                FROM issues
                JOIN scans
                    ON issues.scan_id = scans.id
                JOIN websites
                    ON scans.website_id = websites.id
                WHERE websites.url = ?
                  AND issues.issue_code IS NOT NULL
                  AND issues.review_status IN (
                      'CONFIRMED',
                      'FALSE_POSITIVE',
                      'IGNORED'
                  )
                ORDER BY issues.id DESC
                """,
                (website_url,),
            )
            rows = cursor.fetchall()
            statuses: dict[str, str] = {}
            for row in rows:
                issue_code = row["issue_code"]
                if issue_code in statuses:
                    continue
                statuses[issue_code] = (
                    row["review_status"]
                )
            return statuses
        finally:
            conn.close()
    def update_review(
        self,
        issue_id: int,
        status: str,
        note: str | None = None,
    ) -> None:
        if issue_id <= 0:
            raise ValueError(
                "Issue ID must be greater than zero."
            )
        status = status.strip().upper()
        if status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid review status: {status}"
            )
        note = note.strip() if note else None
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id
                FROM issues
                WHERE id = ?
                """,
                (issue_id,),
            )
            if cursor.fetchone() is None:
                raise ValueError(
                    "Issue not found."
                )
            cursor.execute(
                """
                UPDATE issues
                SET review_status = ?,
                    review_note = ?
                WHERE id = ?
                """,
                (
                    status,
                    note,
                    issue_id,
                ),
            )
            conn.commit()
        finally:
            conn.close()