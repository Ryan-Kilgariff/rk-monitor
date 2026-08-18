from core.database import get_connection
conn = get_connection()
try:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            issues.id,
            issues.scan_id,
            issues.title,
            issues.issue_code,
            issues.review_status
        FROM issues
        JOIN scans
            ON issues.scan_id = scans.id
        JOIN websites
            ON scans.website_id = websites.id
        WHERE websites.url = ?
          AND issues.title = ?
        ORDER BY issues.id DESC
        LIMIT 10
        """,
        (
            "https://www.juddsfollyhotel.co.uk/",
            "Booking provider not recognised",
        ),
    )
    rows = cursor.fetchall()
    for row in rows:
        print(
            {
                "id": row["id"],
                "scan_id": row["scan_id"],
                "title": row["title"],
                "issue_code": row["issue_code"],
                "review_status": row["review_status"],
            }
        )
finally:
    conn.close()