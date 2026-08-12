from core.database import initialize_database
from services.website_scanner import WebsiteScanner
from services.crawl_service import CrawlService
from services.issue_service import IssueService
from services.scoring_service import ScoringService
from services.link_checker import LinkChecker
def main() -> None:
    initialize_database()
    print()
    print("=" * 60)
    print("RK MONITOR")
    print("Hospitality Website Monitoring")
    print("=" * 60)
    url = input("\nWebsite URL: ").strip()
    scanner = WebsiteScanner()
    print("\nScanning website...\n")
    result = scanner.scan(url)
    if not result.successful:
        print("SCAN FAILED")
        print(result.error_message)
        return
    print(f"Website: {result.url}")
    print(f"HTTP Status: {result.status_code}")
    if result.response_time is not None:
        print(
            f"Response Time: "
            f"{result.response_time:.2f}s"
        )
    print(
        f"HTTPS: "
        f"{'Yes' if result.has_https else 'No'}"
    )
    print(
        f"Mobile Viewport: "
        f"{'Yes' if result.has_mobile_viewport else 'No'}"
    )
    print(
        f"Google Analytics: "
        f"{'Detected' if result.has_google_analytics else 'Not detected'}"
    )
    print(f"Page Title: {result.page_title}")
    print(
        f"Internal Links Found: "
        f"{len(result.internal_links)}"
    )
    crawler = CrawlService()
    important_pages = crawler.find_important_pages(
        result.internal_links
    )
    crawled_pages = crawler.crawl(
        important_pages
    )
    all_booking_links = set(
    result.booking_links
    )
    for page in crawled_pages:
        if page.booking_links:
            all_booking_links.update(
                page.booking_links
            )
    all_booking_links = sorted(
        all_booking_links
    )
    booking_provider = scanner.detect_booking_provider(
        all_booking_links
    )
    link_checker = LinkChecker()
    link_results = link_checker.check_many(
        result.internal_links
    )
    issue_service = IssueService()
    issues = issue_service.analyse(
        scan_result=result,
        crawled_pages=crawled_pages,
        booking_provider=booking_provider,
        all_booking_links=all_booking_links,
        link_results=link_results,
    )
    scoring_service = ScoringService()
    score = scoring_service.calculate(
        issues
    )
    print("\nROOM BOOKING")
    print("-" * 60)
    if all_booking_links:
        print("Direct Booking: Yes")
        if booking_provider:
            print(
                f"Booking Provider: "
                f"{booking_provider}"
            )
        else:
            print(
                "Booking Provider: "
                "Unknown"
            )
        print(
            f"Booking Links Found: "
            f"{len(all_booking_links)}"
        )
        for link in all_booking_links:
            print(
                f" - {link}"
            )
    else:
        print(
            "Direct Booking: "
            "Not detected"
        )
    print("\nIMPORTANT PAGES")
    print("-" * 60)
    if not crawled_pages:
        print(
            "No important hospitality "
            "pages detected."
        )
    for page in crawled_pages:
        status = (
            page.status_code
            if page.successful
            else "FAILED"
        )
        print()
        print(
            f"{page.page_type.upper()}"
        )
        print(
            f"Status: {status}"
        )
        print(
            f"URL: {page.url}"
        )
        if page.successful:
            print(
                f"Images: "
                f"{page.image_count}"
            )
            print(
                f"Headings: "
                f"{page.heading_count}"
            )
            print(
                f"Links: "
                f"{page.link_count}"
            )
            print(
                f"Booking Links: "
                f"{len(page.booking_links or [])}"
            )
    print("\nISSUES")
    print("-" * 60)
    if not issues:
        print(
            "No significant issues detected "
            "by the current rule set."
        )
    for issue in issues:
        print()
        print(
            f"[{issue.severity}] "
            f"{issue.title}"
        )
        print(
            f"Category: "
            f"{issue.category}"
        )
        print(
            f"Evidence: "
            f"{issue.evidence}"
        )
        print(
            f"Commercial Impact: "
            f"{issue.commercial_impact}"
        )
        print(
            f"Recommended Action: "
            f"{issue.recommended_action}"
        )
    print("\nRK MONITOR SCORE")
    print("-" * 60)
    print(
        f"Technical Health:      "
        f"{score.technical_health} / 100"
    )
    print(
        f"Booking Journey:       "
        f"{score.booking_journey} / 100"
    )
    print(
        f"Mobile Experience:     "
        f"{score.mobile_experience} / 100"
    )
    print(
        f"Room Presentation:     "
        f"{score.room_presentation} / 100"
    )
    print(
        f"Guest Information:     "
        f"{score.guest_information} / 100"
    )
    print(
        f"Analytics:             "
        f"{score.analytics} / 100"
    )
    print("-" * 60)
    print(
        f"OVERALL:               "
        f"{score.overall} / 100"
    )
    print()
    print(
        f"High Issues:   "
        f"{score.high_issues}"
    )
    print(
        f"Medium Issues: "
        f"{score.medium_issues}"
    )
    print(
        f"Low Issues:    "
        f"{score.low_issues}"
    )
    print("\nLINK HEALTH")
    print("-" * 60)
    broken_links = []
    redirected_links = []
    slow_links = []
    for link in link_results:
        if not link.successful:
            broken_links.append(link)
            continue
        if (
            link.status_code is not None
            and link.status_code >= 400
        ):
            broken_links.append(link)
        if link.redirected:
            redirected_links.append(link)
        if (
            link.response_time is not None
            and link.response_time > 3
        ):
            slow_links.append(link)
    print(
        f"Links Checked: "
        f"{len(link_results)}"
    )
    print(
        f"Broken Links: "
        f"{len(broken_links)}"
    )
    print(
        f"Redirected Links: "
        f"{len(redirected_links)}"
    )
    print(
        f"Slow Links: "
        f"{len(slow_links)}"
    )
    if broken_links:
        print("\nBroken links:")
        for link in broken_links:
            status = (
                link.status_code
                if link.status_code is not None
                else "FAILED"
            )
            print(
                f" - [{status}] {link.url}"
            )
if __name__ == "__main__":
    main()