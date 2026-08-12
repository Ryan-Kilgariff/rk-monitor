from core.database import initialize_database
from services.scan_service import ScanService
from services.report_service import ReportService
def main() -> None:
    initialize_database()
    print()
    print("=" * 60)
    print("RK MONITOR")
    print("Hospitality Website Monitoring")
    print("=" * 60)
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
if __name__ == "__main__":
    main()