from dataclasses import dataclass
from services.website_scanner import ScanResult
from services.crawl_service import CrawledPage
from services.link_checker import LinkCheckResult
from services.visual_scan_service import VisualScanResult
@dataclass
@dataclass
class Issue:
    severity: str
    category: str
    title: str
    evidence: str
    commercial_impact: str
    recommended_action: str
    issue_code: str | None = None
    confidence: str = "HIGH"
    requires_review: bool = False
class IssueService:
    def analyse(
        self,
        scan_result: ScanResult,
        crawled_pages: list[CrawledPage],
        booking_provider: str | None,
        all_booking_links: list[str],
        link_results: list[LinkCheckResult],
        visual_result: VisualScanResult | None = None,
        homepage_visual_result: VisualScanResult | None = None,
        mobile_homepage_visual_result: VisualScanResult | None = None,
        domain_identity=None,
    ) -> list[Issue]:
        issues = []
        content_mismatch = (
            domain_identity is not None
            and domain_identity.mismatch_detected
        )
        # ----------------------------------------------
        # DOMAIN / WEBSITE IDENTITY
        # ----------------------------------------------
        if content_mismatch:
            issues.append(
                Issue(
                    severity="HIGH",
                    category="Technical Health",
                    title=(
                        "Website content appears "
                        "unrelated to the hospitality business"
                    ),
                    evidence=(
                        " | ".join(
                            domain_identity.evidence
                        )
                    ),
                    commercial_impact=(
                        "Guests may be reaching unrelated "
                        "content instead of the property's "
                        "website, which can cause confusion "
                        "and lost bookings."
                    ),
                    recommended_action=(
                        "Review domain routing, hosting, "
                        "redirects and virtual-host "
                        "configuration."
                    ),
                )
            )
        # ----------------------------------------------
        # TECHNICAL HEALTH
        # ----------------------------------------------
        issues.extend(
            self._analyse_technical_health(
                scan_result
            )
        )
        # ----------------------------------------------
        # HOSPITALITY-SPECIFIC ANALYSIS
        # Only run when the returned website appears
        # to belong to the hospitality business.
        # ----------------------------------------------
        if not content_mismatch:
            issues.extend(
                self._analyse_booking_journey(
                    scan_result,
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
            if visual_result is not None:
                issues.extend(
                    self._analyse_visual_room_presentation(
                        visual_result
                    )
                )
            if homepage_visual_result is not None:
                issues.extend(
                    self._analyse_visual_navigation(
                        homepage_visual_result
                    )
                )
            if mobile_homepage_visual_result is not None:
                issues.extend(
                    self._analyse_mobile_layout(
                        mobile_homepage_visual_result
                    )
                )
            issues.extend(
                self._analyse_link_health(
                    link_results
                )
            )
        return self._sort_issues(
            issues
        )
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
        if scan_result.successful:
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
        if (
            scan_result.ssl_verification_failed
            and not scan_result.connection_failed
        ):
            issues.append(
                Issue(
                    severity="HIGH",
                    category="Technical Health",
                    title="SSL certificate verification problem",
                    evidence=(
                        scan_result.ssl_error_message
                        or "SSL verification failed."
                    ),
                    commercial_impact=(
                        "Some browsers, integrations or "
                        "automated services may have difficulty "
                        "establishing a trusted HTTPS connection."
                    ),
                    recommended_action=(
                        "Review the SSL certificate chain, "
                        "intermediate certificates and hosting "
                        "configuration."
                    ),
                )
            )
        if scan_result.dns_resolution_failed:
            issues.append(
                Issue(
                    severity="HIGH",
                    category="Technical Health",
                    title="Website domain could not be resolved",
                    evidence=(
                        scan_result.error_message
                        or "DNS resolution failed."
                    ),
                    commercial_impact=(
                        "Guests may be unable to access "
                        "the property website at all."
                    ),
                    recommended_action=(
                        "Review the domain DNS configuration, "
                        "nameservers and hosting records."
                    ),
                )
            )
        if scan_result.timeout_occurred:
            issues.append(
                Issue(
                    severity="MEDIUM",
                    category="Technical Health",
                    title="Homepage request timed out",
                    evidence=(
                        scan_result.error_message
                        or "The homepage request exceeded the timeout."
                    ),
                    commercial_impact=(
                        "Guests may experience delays or difficulty "
                        "reaching the website when the server responds slowly."
                    ),
                    recommended_action=(
                        "Review server response times, hosting performance "
                        "and application load."
                    ),
                )
            )
        if (
            scan_result.connection_failed
            and not scan_result.ssl_verification_failed
        ):
            issues.append(
                Issue(
                    severity="HIGH",
                    category="Technical Health",
                    title="Website connection failed",
                    evidence=(
                        scan_result.error_message
                        or "Connection failed."
                    ),
                    commercial_impact=(
                        "Guests may be unable to reliably "
                        "access the property website."
                    ),
                    recommended_action=(
                        "Review hosting availability, "
                        "server configuration and network connectivity."
                    ),
                )
            )
        if (
            scan_result.ssl_verification_failed
            and scan_result.connection_failed
        ):
            issues.append(
                Issue(
                    severity="HIGH",
                    category="Technical Health",
                    title=(
                        "Secure website connection failed"
                    ),
                    evidence=(
                        scan_result.ssl_error_message
                        or (
                            "The HTTPS connection could not "
                            "be established."
                        )
                    ),
                    commercial_impact=(
                        "Visitors may be unable to access "
                        "the website securely."
                    ),
                    recommended_action=(
                        "Investigate the website's SSL/TLS "
                        "configuration and hosting setup."
                    ),
                )
            )
        return issues
    def _analyse_booking_journey(
        self,
        scan_result: ScanResult,
        crawled_pages: list[CrawledPage],
        booking_provider: str | None,
        all_booking_links: list[str],
    ) -> list[Issue]:
        issues = []
        if (
            scan_result.dns_resolution_failed
            or scan_result.connection_failed
            or scan_result.timeout_occurred
        ):
            return []
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
        page_errors = {}
        for page in crawled_pages:
            if not page.successful:
                page_errors.setdefault(
                    page.page_type,
                    [],
                ).append(
                    f"{page.url} could not be loaded"
                )
                continue
            if (
                page.status_code is not None
                and page.status_code >= 400
            ):
                page_errors.setdefault(
                    page.page_type,
                    [],
                ).append(
                    f"{page.url} returned "
                    f"HTTP {page.status_code}"
                )
                continue
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
        for page_type, errors in page_errors.items():
            page_name = (
                page_type
                .replace("_", " ")
                .title()
            )
            error_count = len(errors)
            if error_count == 1:
                title = (
                    f"{page_name} page returned an error"
                )
                evidence = errors[0]
            else:
                title = (
                    f"Multiple {page_name.lower()} "
                    f"pages returned errors"
                )
                evidence = (
                    f"{error_count} {page_name.lower()} "
                    f"pages failed. Examples: "
                    + " | ".join(
                        errors[:3]
                    )
                )
            issues.append(
                Issue(
                    severity="HIGH",
                    category="Website Content",
                    title=title,
                    evidence=evidence,
                    commercial_impact=(
                        "Guests may be unable to access "
                        "important hospitality information."
                    ),
                    recommended_action=(
                        "Repair, remove or redirect the "
                        "affected pages."
                    ),
                )
            )
        return issues
    def _analyse_visual_room_presentation(
        self,
        visual_result: VisualScanResult,
    ) -> list[Issue]:
        issues = []
        if not visual_result.successful:
            return issues
        if visual_result.room_presentation_issue:
            issues.append(
                Issue(
                    severity="MEDIUM",
                    category="Room Presentation",
                    title=(
                        "Limited room visual presentation"
                    ),
                    issue_code="visual.room_presentation",
                    evidence=(
                        f"{visual_result.room_offering_count} "
                        f"room offering(s) were detected, "
                        f"with "
                        f"{visual_result.substantial_visual_image_count} "
                        f"substantial visual image(s). "
                        f"Coverage: "
                        f"{visual_result.images_per_room_offering:.2f} "
                        f"images per offering."
                    ),
                    commercial_impact=(
                        "Guests may have limited visual "
                        "information when comparing room "
                        "or accommodation options."
                    ),
                    recommended_action=(
                        "Provide clear, substantial room "
                        "photography for each accommodation "
                        "type or room offering."
                    ),
                    confidence="MEDIUM",
                    requires_review=True,
                )
            )
        return issues
    def _analyse_visual_navigation(
        self,
        visual_result: VisualScanResult,
    ) -> list[Issue]:
        issues = []
        if not visual_result.successful:
            return issues
        if visual_result.navigation_issue:
            issues.append(
                Issue(
                    severity="MEDIUM",
                    category="Mobile Experience",
                    title=(
                        "Navigation layout contains "
                        "overflow"
                    ),
                    issue_code="visual.navigation_overflow",
                    evidence=(
                        f"Navigation overflow was detected. "
                        f"Navigation container width: "
                        f"{visual_result.navigation_width}px. "
                        f"Viewport width: "
                        f"{visual_result.viewport_width}px. "
                        f"Viewport ratio: "
                        f"{visual_result.navigation_viewport_ratio:.2f}. "
                        f"{visual_result.navigation_item_count} "
                        f"navigation item(s) detected."
                    ),
                    commercial_impact=(
                        "Navigation overflow can make menus "
                        "harder to use and may cause links "
                        "or controls to extend beyond their "
                        "intended visible area."
                    ),
                    recommended_action=(
                        "Review navigation spacing, menu "
                        "width and responsive behaviour "
                        "across common screen sizes."
                    ),
                    confidence="MEDIUM",
                    requires_review=True,
                )
            )
        return issues
    def _analyse_mobile_layout(
        self,
        visual_result: VisualScanResult,
    ) -> list[Issue]:
        issues = []
        if not visual_result.successful:
            return issues
        critical_overflow_count = (
            visual_result.critical_overflow_elements
        )
        if (
            critical_overflow_count > 0
            and visual_result.navigation_issue
        ):
            issues.append(
                Issue(
                    severity="MEDIUM",
                    category="Mobile Experience",
                    title=(
                        "Mobile layout contains "
                        "clipped navigation content"
                    ),
                    issue_code="visual.mobile_clipped_navigation",
                    evidence=(
                        f"{critical_overflow_count} "
                        f"critically clipped element(s) "
                        f"were detected at a "
                        f"{visual_result.viewport_width}px "
                        f"viewport. Navigation overflow "
                        f"was also detected."
                    ),
                    commercial_impact=(
                        "Mobile guests may encounter "
                        "cut-off or difficult-to-use "
                        "navigation and page content."
                    ),
                    recommended_action=(
                        "Review the mobile navigation "
                        "and responsive layout at common "
                        "phone widths and remove visible "
                        "content clipping."
                    ),
                    confidence="MEDIUM",
                    requires_review=True,
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