from core.database import initialize_database
from services.scan_service import ScanService
from services.report_service import ReportService
from services.batch_scan_service import BatchScanService
from services.batch_report_service import BatchReportService
from datetime import datetime
from services.csv_service import CsvService
from services.issue_review_service import IssueReviewService
from services.pdf_report_service import PdfReportService
from services.client_monitoring_service import (
    ClientMonitoringService,
)
from services.monitoring_service import MonitoringService
from services.client_monitoring_report_service import (
    ClientMonitoringReportService,
)
from services.client_escalation_service import (
    ClientEscalationService,
)
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
def run_client_report() -> None:
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
        result,
        client_mode=True,
    )
    pending_review_issues = [
    issue
        for issue in result.issues
        if (
            issue.requires_review
            and issue.review_status not in (
                "CONFIRMED",
                "FALSE_POSITIVE",
                "IGNORED",
            )
        )
    ]
    if pending_review_issues:
        print()
        print(
            "Client report is not ready for export."
        )
        print(
            f"{len(pending_review_issues)} finding(s) "
            "still require manual review."
        )
        print(
            "Use option 4 to review them, then "
            "rerun the client website report."
        )
        return
    export_choice = input(
        "\nExport client report to PDF? "
        "(y/n): "
    ).strip().lower()
    if export_choice != "y":
        return
    timestamp = datetime.now().strftime(
        "%Y%m%d-%H%M%S"
    )
    output_path = (
        f"exports/"
        f"rk-monitor-client-report-"
        f"{timestamp}.pdf"
    )
    pdf_service = PdfReportService()
    saved_path = (
        pdf_service.export_client_report(
            result,
            output_path,
        )
    )
    print()
    print(
        f"PDF saved: {saved_path}"
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
def run_client_monitoring() -> None:
    service = ClientMonitoringService()
    print()
    print("CLIENT MONITORING")
    print("-" * 60)
    print("1. View Active Clients")
    print("2. Activate Existing Website")
    print("3. Deactivate Client")
    print("4. Run Monitoring Scan")
    print("5. View Client History")
    print("6. View Due Monitoring")
    print("7. Back")
    choice = input(
        "\nSelect option: "
    ).strip()
    if choice == "1":
        clients = service.list_active()
        if not clients:
            print()
            print(
                "No active monitored clients."
            )
            return
        print()
        print("ACTIVE CLIENTS")
        print("-" * 60)
        for client in clients:
            print()
            print(
                f"Website ID: "
                f"{client.website_id}"
            )
            print(
                f"Name: "
                f"{client.name or 'Unknown'}"
            )
            print(
                f"URL: {client.url}"
            )
            print(
                f"Frequency: "
                f"{client.monitoring_frequency}"
            )
    elif choice == "2":
        url = input(
            "\nWebsite URL: "
        ).strip()
        print()
        print(
            "Monitoring frequency:"
        )
        print("1. Weekly")
        print("2. Fortnightly")
        print("3. Monthly")
        print("4. Quarterly")
        frequency_choice = input(
            "\nSelect frequency: "
        ).strip()
        frequency_map = {
            "1": "WEEKLY",
            "2": "FORTNIGHTLY",
            "3": "MONTHLY",
            "4": "QUARTERLY",
        }
        frequency = frequency_map.get(
            frequency_choice
        )
        if frequency is None:
            print()
            print(
                "Invalid monitoring frequency."
            )
            return
        try:
            client = service.activate(
                url,
                frequency,
            )
        except ValueError as exc:
            print()
            print(
                f"CLIENT ERROR: {exc}"
            )
            return
        print()
        print(
            "Client monitoring activated."
        )
        print(
            f"Website: {client.url}"
        )
        print(
            f"Frequency: "
            f"{client.monitoring_frequency}"
        )
    elif choice == "3":
        url = input(
            "\nWebsite URL: "
        ).strip()
        try:
            client = service.deactivate(
                url
            )
        except ValueError as exc:
            print()
            print(
                f"CLIENT ERROR: {exc}"
            )
            return
        print()
        print(
            "Client monitoring deactivated."
        )
        print(
            f"Website: {client.url}"
        )
    elif choice == "4":
        url = input(
            "\nClient Website URL: "
        ).strip()
        active_clients = service.list_active()
        active_urls = {
            client.url
            for client in active_clients
        }
        if url not in active_urls:
            print()
            print(
                "Website is not an active "
                "monitored client."
            )
            return
        print()
        print(
            "Running monitoring scan...\n"
        )
        scan_service = ScanService()
        try:
            scan_service.run(
                url
            )
        except RuntimeError as exc:
            print(
                f"SCAN FAILED: {exc}"
            )
            return
        monitoring_service = (
            MonitoringService()
        )
        comparison = (
            monitoring_service
            .compare_latest_to_previous_complete(
                url
            )
        )
        report_service = (
            ClientMonitoringReportService()
        )
        report_service.print_summary(
            comparison
        )
        escalation_service = (
            ClientEscalationService()
        )
        escalation = (
            escalation_service.assess(
                comparison
            )
        )
        print()
        print("ESCALATION STATUS")
        print("-" * 60)
        print(
            f"Level: {escalation.level}"
        )
        print(
            "Client Contact Required: "
            f"{'Yes' if escalation.requires_contact else 'No'}"
        )
        print()
        for reason in escalation.reasons:
            print(
                f"- {reason}"
            )
        export_choice = input(
            "\nExport monitoring update to PDF? "
            "(y/n): "
        ).strip().lower()
        if export_choice != "y":
            return
        timestamp = datetime.now().strftime(
            "%Y%m%d-%H%M%S"
        )
        output_path = (
            f"exports/"
            f"rk-monitor-monitoring-update-"
            f"{timestamp}.pdf"
        )
        pdf_service = PdfReportService()
        saved_path = (
            pdf_service.export_monitoring_update(
                website_url=url,
                comparison=comparison,
                escalation=escalation,
                output_path=output_path,
            )
        )
        print()
        print(
            f"PDF saved: {saved_path}"
        )
    elif choice == "5":
        url = input(
            "\nClient Website URL: "
        ).strip()
        try:
            history = service.get_history(
                url
            )
        except ValueError as exc:
            print()
            print(
                f"CLIENT ERROR: {exc}"
            )
            return
        print()
        print("MONITORING HISTORY")
        print("-" * 60)
        if not history:
            print(
                "No commercial monitoring "
                "history available."
            )
            return
        for entry in history:
            print(
                f"{entry.scanned_at}  "
                f"Score: {entry.commercial_score}  "
                f"Scan ID: {entry.scan_id}"
            )
    elif choice == "6":
        statuses = service.get_due_statuses()
        print()
        print("CLIENTS DUE FOR MONITORING")
        print("-" * 60)
        if not statuses:
            print(
                "No active monitored clients."
            )
            return
        for status in statuses:
            print()
            print(
                f"Name: "
                f"{status.name or 'Unknown'}"
            )
            print(
                f"URL: {status.url}"
            )
            print(
                f"Frequency: "
                f"{status.monitoring_frequency}"
            )
            print(
                f"Last Scan: "
                f"{status.last_scan_at or 'None'}"
            )
            print(
                f"Next Due: "
                f"{status.next_due_at or 'Now'}"
            )
            print(
                "Status: "
                f"{'DUE' if status.is_due else 'Not Due'}"
            )
    elif choice == "7":
        return
    else:
        print()
        print(
            "Invalid option."
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
    print("5. Client Website Report")
    print("6. Client Monitoring")
    print("7. Exit")
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
        run_client_report()
    elif choice == "6":
        run_client_monitoring()
    elif choice == "7":
        print(
            "\nGoodbye."
        )
    else:
        print(
            "\nInvalid option."
        )
if __name__ == "__main__":
    main()