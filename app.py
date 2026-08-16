from core.database import initialize_database
from services.scan_service import ScanService
from services.report_service import ReportService
from services.batch_scan_service import BatchScanService
from services.batch_report_service import BatchReportService
from datetime import datetime
from services.csv_service import CsvService
from services.issue_review_service import IssueReviewService
def run_single_scan() -> None:
    url = input(
        "\nWebsite URL: "
    ).strip()
    print(
        "\nScanning website...\n"
    )
    scan_service = ScanService()
    try:
        result = scan_service.run(
            url
        )
    except RuntimeError as exc:
        print(
            f"SCAN FAILED: "
            f"{exc}"
        )
        return
    report_service = ReportService()
    report_service.print_report(
        result
    )
def run_batch_scan() -> None:
    print()
    print(
        "Enter one website URL per line."
    )
    print(
        "Press ENTER on a blank line "
        "when finished."
    )
    urls = []
    while True:
        url = input(
            "> "
        ).strip()
        if not url:
            break
        urls.append(url)
    if not urls:
        print(
            "No URLs entered."
        )
        return
    print()
    print(
        f"Scanning "
        f"{len(urls)} website(s)..."
    )
    batch_service = (
        BatchScanService()
    )
    batch = batch_service.run(
        urls
    )
    report_service = (
        BatchReportService()
    )
    report_service.print_report(
        batch
    )
def run_csv_scan() -> None:
    print()
    print("CSV Prospect Scan")
    print("-" * 60)
    file_path = input(
        "CSV file path: "
    ).strip().strip('"')
    csv_service = CsvService()
    try:
        urls = csv_service.load_urls(
            file_path
        )
    except (
        FileNotFoundError,
        ValueError,
    ) as exc:
        print(
            f"\nCSV ERROR: {exc}"
        )
        return
    if not urls:
        print(
            "\nNo website URLs found."
        )
        return
    print()
    print(
        f"{len(urls)} prospect(s) loaded."
    )
    print(
        "Starting RK Monitor batch scan..."
    )
    batch_service = BatchScanService()
    batch = batch_service.run(
        urls
    )
    batch_report = BatchReportService()
    batch_report.print_report(
        batch
    )
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )
    output_path = (
        f"exports/"
        f"rk_prospects_{timestamp}.csv"
    )
    csv_service.export_results(
        batch,
        output_path,
    )
    print()
    print(
        f"Results exported to: "
        f"{output_path}"
    )
def run_issue_review() -> None:
    review_service = IssueReviewService()
    pending = review_service.get_pending_reviews()
    if not pending:
        print()
        print("No pending issues to review.")
        return
    print()
    print("PENDING ISSUE REVIEWS")
    print("-" * 60)
    for issue in pending:
        print()
        print(
            f"Issue ID: {issue.issue_id}"
        )
        print(
            f"Website: {issue.website_url}"
        )
        print(
            f"[{issue.severity}] {issue.title}"
        )
        print(
            f"Category: {issue.category}"
        )
        print(
            f"Confidence: {issue.confidence}"
        )
        if issue.evidence:
            print(
                f"Evidence: {issue.evidence}"
            )
        print()
        print("1. Confirm")
        print("2. False Positive")
        print("3. Ignore")
        print("4. Skip")
        choice = input(
            "\nReview action: "
        ).strip()
        if choice == "4":
            continue
        status_map = {
            "1": "CONFIRMED",
            "2": "FALSE_POSITIVE",
            "3": "IGNORED",
        }
        status = status_map.get(choice)
        if status is None:
            print(
                "Invalid option - issue skipped."
            )
            continue
        note = input(
            "Review note (optional): "
        ).strip()
        review_service.update_review(
            issue.issue_id,
            status,
            note or None,
        )
        print(
            f"Issue marked as {status}."
        )
def main() -> None:
    initialize_database()
    print()
    print("=" * 60)
    print("RK MONITOR")
    print("Hospitality Website Monitoring")
    print("=" * 60)
    print()
    print("1. Single Website Scan")
    print("2. Batch Prospect Scan")
    print("3. Scan Prospects From CSV")
    print("4. Review Pending Issues")
    print("5. Exit")
    choice = input(
        "\nSelect option: "
    ).strip()
    if choice == "1":
        run_single_scan()
    elif choice == "2":
        run_batch_scan()
    elif choice == "3":
        run_csv_scan()
    elif choice == "4":
        run_issue_review()
    elif choice == "5":
        print(
            "\nGoodbye."
        )
    else:
        print(
            "\nInvalid option."
        )
if __name__ == "__main__":
    main()