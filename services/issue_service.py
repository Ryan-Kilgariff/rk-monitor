from dataclasses import dataclass
from services.website_scanner import ScanResult
from services.crawl_service import CrawledPage
from services.link_checker import LinkCheckResult
@dataclass
class Issue:
    severity: str
    category: str
    title: str
    evidence: str
    commercial_impact: str
    recommended_action: str
class IssueService:
    def analyse(
        self,
        scan_result: ScanResult,
        crawled_pages: list[CrawledPage],
        booking_provider: str | None,
        all_booking_links: list[str],
        link_results: list[LinkCheckResult],
    ) -> list[Issue]:
        issues = []
        issues.extend(
            self._analyse_technical_health(
                scan_result
            )
        )
        issues.extend(
            self._analyse_booking_journey(
                crawled_pages,
                booking_provider,
                all_booking_links,
            )
        )
        issues.extend(
            self._analyse_hospitality_pages(
                crawled_pages
            )
        )
        issues.extend(
            self._analyse_link_health(
                link_results
            )
        )
        return self._sort_issues(issues)
    def _analyse_technical_health(
        self,
        scan_result: ScanResult,
    ) -> list[Issue]:
        issues = []
        if not scan_result.has_https:
            issues.append(
                Issue(
                    severity="HIGH",
                    category="Technical Health",
                    title="HTTPS not detected",
                    evidence=(
                        "The website was not served "
                        "over HTTPS."
                    ),
                    commercial_impact=(
                        "Guests may see security "
                        "warnings or have reduced "
                        "confidence in the website."
                    ),
                    recommended_action=(
                        "Enable HTTPS and redirect "
                        "all HTTP traffic securely."
                    ),
                )
            )
        if (
            scan_result.status_code is not None
            and scan_result.status_code >= 400
        ):
            issues.append(
                Issue(
                    severity="HIGH",
                    category="Technical Health",
                    title="Homepage returned an error",
                    evidence=(
                        f"HTTP status: "
                        f"{scan_result.status_code}"
                    ),
                    commercial_impact=(
                        "Guests may be unable to "
                        "access the website."
                    ),
                    recommended_action=(
                        "Investigate the server or "
                        "hosting issue immediately."
                    ),
                )
            )
        if (
            scan_result.response_time is not None
            and scan_result.response_time > 3
        ):
            issues.append(
                Issue(
                    severity="MEDIUM",
                    category="Technical Health",
                    title="Slow homepage response",
                    evidence=(
                        f"Initial response took "
                        f"{scan_result.response_time:.2f}s."
                    ),
                    commercial_impact=(
                        "Slow-loading pages can create "
                        "friction before guests reach "
                        "room or booking information."
                    ),
                    recommended_action=(
                        "Review hosting, page assets "
                        "and website performance."
                    ),
                )
            )
        if not scan_result.has_mobile_viewport:
            issues.append(
                Issue(
                    severity="HIGH",
                    category="Mobile Experience",
                    title="Mobile viewport not detected",
                    evidence=(
                        "No standard mobile viewport "
                        "meta tag was detected."
                    ),
                    commercial_impact=(
                        "The website may display poorly "
                        "on phones, creating friction "
                        "for mobile guests."
                    ),
                    recommended_action=(
                        "Implement responsive viewport "
                        "configuration and test the "
                        "booking journey on mobile."
                    ),
                )
            )
        if not scan_result.has_google_analytics:
            issues.append(
                Issue(
                    severity="LOW",
                    category="Analytics",
                    title="Google Analytics not detected",
                    evidence=(
                        "RK Monitor did not detect "
                        "common Google Analytics or "
                        "Google Tag Manager markers."
                    ),
                    commercial_impact=(
                        "The property may have limited "
                        "visibility into website and "
                        "booking behaviour."
                    ),
                    recommended_action=(
                        "Confirm whether analytics are "
                        "configured and tracking useful "
                        "conversion events."
                    ),
                )
            )
        return issues
    def _analyse_booking_journey(
        self,
        crawled_pages: list[CrawledPage],
        booking_provider: str | None,
        all_booking_links: list[str],
    ) -> list[Issue]:
        issues = []
        room_pages = [
            page
            for page in crawled_pages
            if page.page_type == "rooms"
        ]
        if not all_booking_links:
            issues.append(
                Issue(
                    severity="HIGH",
                    category="Booking Journey",
                    title="No room booking route detected",
                    evidence=(
                        "No recognised hotel booking "
                        "link was found during the scan."
                    ),
                    commercial_impact=(
                        "Guests may be unable to move "
                        "directly from browsing the "
                        "website into a room booking."
                    ),
                    recommended_action=(
                        "Add a prominent direct-booking "
                        "CTA linked to a working booking "
                        "engine."
                    ),
                )
            )
        if room_pages and not all_booking_links:
            issues.append(
                Issue(
                    severity="HIGH",
                    category="Booking Journey",
                    title="Rooms detected without booking path",
                    evidence=(
                        f"{len(room_pages)} room or "
                        "accommodation page(s) were "
                        "detected, but no recognised "
                        "booking link was found."
                    ),
                    commercial_impact=(
                        "Guests can view accommodation "
                        "but may face unnecessary "
                        "friction when trying to book."
                    ),
                    recommended_action=(
                        "Place prominent booking calls "
                        "to action on accommodation "
                        "pages."
                    ),
                )
            )
        if all_booking_links and booking_provider is None:
            issues.append(
                Issue(
                    severity="LOW",
                    category="Booking Journey",
                    title="Booking provider not recognised",
                    evidence=(
                        "A booking link was detected, "
                        "but RK Monitor could not "
                        "identify the provider."
                    ),
                    commercial_impact=(
                        "The booking journey exists, "
                        "but further review is required "
                        "to understand how guests are "
                        "being routed."
                    ),
                    recommended_action=(
                        "Manually review the booking "
                        "destination and confirm that "
                        "it is appropriate for direct "
                        "reservations."
                    ),
                )
            )
        return issues
    def _analyse_hospitality_pages(
        self,
        crawled_pages: list[CrawledPage],
    ) -> list[Issue]:
        issues = []
        for page in crawled_pages:
            if not page.successful:
                issues.append(
                    Issue(
                        severity="HIGH",
                        category="Website Content",
                        title=(
                            f"{page.page_type.title()} "
                            f"page could not be loaded"
                        ),
                        evidence=page.url,
                        commercial_impact=(
                            "Guests may encounter a "
                            "broken or inaccessible "
                            "important page."
                        ),
                        recommended_action=(
                            "Investigate the page and "
                            "restore access."
                        ),
                    )
                )
                continue
            if (
                page.status_code is not None
                and page.status_code >= 400
            ):
                issues.append(
                    Issue(
                        severity="HIGH",
                        category="Website Content",
                        title=(
                            f"{page.page_type.title()} "
                            f"page returned an error"
                        ),
                        evidence=(
                            f"{page.url} returned "
                            f"HTTP {page.status_code}."
                        ),
                        commercial_impact=(
                            "Guests may be unable to "
                            "access important hospitality "
                            "information."
                        ),
                        recommended_action=(
                            "Repair or redirect the "
                            "affected page."
                        ),
                    )
                )
            if (
                page.page_type == "rooms"
                and page.image_count == 0
            ):
                issues.append(
                    Issue(
                        severity="HIGH",
                        category="Room Presentation",
                        title="Room page has no detected images",
                        evidence=page.url,
                        commercial_impact=(
                            "Guests may struggle to "
                            "evaluate the accommodation "
                            "without visual presentation."
                        ),
                        recommended_action=(
                            "Add high-quality room and "
                            "accommodation photography."
                        ),
                    )
                )
            if (
                page.page_type == "rooms"
                and page.heading_count == 0
            ):
                issues.append(
                    Issue(
                        severity="MEDIUM",
                        category="Room Presentation",
                        title="Room page has weak content structure",
                        evidence=(
                            f"No H1-H3 headings were "
                            f"detected on {page.url}"
                        ),
                        commercial_impact=(
                            "Accommodation information "
                            "may be difficult for guests "
                            "to scan and understand."
                        ),
                        recommended_action=(
                            "Use clear room names, "
                            "descriptive headings and "
                            "structured content."
                        ),
                    )
                )
            if (
                page.page_type == "guest_information"
                and page.heading_count <= 1
            ):
                issues.append(
                    Issue(
                        severity="LOW",
                        category="Guest Information",
                        title="Guest information may be difficult to scan",
                        evidence=(
                            f"{page.url} contains "
                            f"{page.heading_count} "
                            f"detected heading(s)."
                        ),
                        commercial_impact=(
                            "Guests may need more time "
                            "to find important information."
                        ),
                        recommended_action=(
                            "Break information into clear "
                            "sections with descriptive "
                            "headings."
                        ),
                    )
                )
        return issues
    def _sort_issues(
        self,
        issues: list[Issue],
    ) -> list[Issue]:
        severity_order = {
            "HIGH": 0,
            "MEDIUM": 1,
            "LOW": 2,
        }
        return sorted(
            issues,
            key=lambda issue: severity_order.get(
                issue.severity,
                99,
            ),
        )
    def _analyse_link_health(
        self,
        link_results: list[LinkCheckResult],
    ) -> list[Issue]:
        issues = []
        broken_links = []
        for link in link_results:
            if not link.successful:
                broken_links.append(link)
                continue
            if (
                link.status_code is not None
                and link.status_code >= 400
            ):
                broken_links.append(link)
        if len(broken_links) >= 3:
            issues.append(
                Issue(
                    severity="HIGH",
                    category="Technical Health",
                    title="Multiple broken internal links detected",
                    evidence=(
                        f"{len(broken_links)} internal "
                        f"links failed or returned errors."
                    ),
                    commercial_impact=(
                        "Guests may encounter broken "
                        "pages while navigating the site, "
                        "which can reduce trust and disrupt "
                        "the booking journey."
                    ),
                    recommended_action=(
                        "Repair, remove or redirect "
                        "the affected links."
                    ),
                )
            )
        elif len(broken_links) > 0:
            issues.append(
                Issue(
                    severity="MEDIUM",
                    category="Technical Health",
                    title="Broken internal link detected",
                    evidence=(
                        f"{len(broken_links)} internal "
                        f"link(s) failed or returned errors."
                    ),
                    commercial_impact=(
                        "Guests may encounter an "
                        "unexpected dead end while "
                        "browsing the website."
                    ),
                    recommended_action=(
                        "Review and repair the affected "
                        "internal link."
                    ),
                )
            )
        slow_links = [
            link
            for link in link_results
            if (
                link.successful
                and link.response_time is not None
                and link.response_time > 3
            )
        ]
        if len(slow_links) >= 3:
            issues.append(
                Issue(
                    severity="MEDIUM",
                    category="Technical Health",
                    title="Several pages respond slowly",
                    evidence=(
                        f"{len(slow_links)} checked pages "
                        f"took more than 3 seconds "
                        f"to respond."
                    ),
                    commercial_impact=(
                        "Repeated slow page responses "
                        "can create friction during "
                        "guest browsing."
                    ),
                    recommended_action=(
                        "Review hosting performance, "
                        "page weight and server response "
                        "times."
                    ),
                )
            )
        return issues