from core.database import get_connection
from services.website_scanner import ScanResult
from services.issue_service import Issue
from services.link_checker import LinkCheckResult
class ScanRepository:
    def save(
        self,
        scan_result: ScanResult,
        issues: list[Issue],
        link_results: list[LinkCheckResult],
        booking_provider: str | None,
        booking_links: list[str],
        overall_score: int,
    ) -> int:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            website_id = self._get_or_create_website(
                cursor,
                scan_result.url,
                scan_result.page_title,
            )
            broken_links = self._count_broken_links(
                link_results
            )
            cursor.execute(
                """
                INSERT INTO scans (
                    website_id,
                    status_code,
                    response_time,
                    page_title,
                    has_https,
                    has_mobile_viewport,
                    has_google_analytics,
                    ssl_verification_failed,
                    error_message,
                    booking_provider,
                    booking_links_found,
                    internal_links_found,
                    broken_links_found,
                    overall_score,
                    scan_successful,
                    error_message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    website_id,
                    scan_result.status_code,
                    scan_result.response_time,
                    scan_result.page_title,
                    int(scan_result.has_https),
                    int(scan_result.has_mobile_viewport),
                    int(scan_result.has_google_analytics),
                    int(scan_result.ssl_verification_failed),
                    scan_result.ssl_error_message,
                    booking_provider,
                    len(booking_links),
                    len(scan_result.internal_links),
                    broken_links,
                    overall_score,
                    int(scan_result.successful),
                    scan_result.error_message,
                ),
            )
            scan_id = cursor.lastrowid
            for issue in issues:
                cursor.execute(
                    """
                    INSERT INTO issues (
                        scan_id,
                        severity,
                        category,
                        title,
                        issue_code,
                        confidence,
                        requires_review,
                        evidence,
                        commercial_impact,
                        recommended_action
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        scan_id,
                        issue.severity,
                        issue.category,
                        issue.title,
                        issue.issue_code,
                        issue.confidence,
                        int(issue.requires_review),
                        issue.evidence,
                        issue.commercial_impact,
                        issue.recommended_action,
                    ),
                )
            conn.commit()
            return scan_id
        finally:
            conn.close()
    def _get_or_create_website(
        self,
        cursor,
        url: str,
        page_title: str | None,
    ) -> int:
        cursor.execute(
            """
            SELECT id
            FROM websites
            WHERE url = ?
            """,
            (url,),
        )
        row = cursor.fetchone()
        if row:
            return row["id"]
        cursor.execute(
            """
            INSERT INTO websites (
                name,
                url
            )
            VALUES (?, ?)
            """,
            (
                page_title,
                url,
            ),
        )
        return cursor.lastrowid
    def _count_broken_links(
        self,
        link_results: list[LinkCheckResult],
    ) -> int:
        count = 0
        for link in link_results:
            if not link.successful:
                count += 1
                continue
            if (
                link.status_code is not None
                and link.status_code >= 400
            ):
                count += 1
        return count