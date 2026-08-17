from dataclasses import dataclass
from services.website_scanner import WebsiteScanner, ScanResult
from services.crawl_service import CrawlService, CrawledPage
from services.link_checker import LinkChecker, LinkCheckResult
from services.issue_service import IssueService, Issue
from services.scoring_service import ScoringService, ScoreResult
from services.prospect_service import ProspectService, ProspectResult
from services.scan_repository import ScanRepository
from services.monitoring_service import MonitoringService, ScanComparison
from services.site_quality_service import (
    SiteQualityService,
    SiteQualityResult,
)
from services.content_quality_service import (
    ContentQualityService,
    ContentQualityResult,
)
from services.commercial_scoring_service import (
    CommercialScoringService,
    CommercialScoreResult,
)
from services.domain_identity_service import (
    DomainIdentityService,
    DomainIdentityResult,
)
from services.visual_scan_service import VisualScanService
from services.issue_review_service import IssueReviewService
@dataclass
class FullScanResult:
    scan_result: ScanResult
    crawled_pages: list[CrawledPage]
    link_results: list[LinkCheckResult]
    booking_links: list[str]
    booking_provider: str | None
    issues: list[Issue]
    score: ScoreResult
    prospect: ProspectResult
    scan_id: int
    comparison: ScanComparison
    site_quality: SiteQualityResult
    content_quality: ContentQualityResult
    general_pages: list[CrawledPage]
    commercial_score: CommercialScoreResult
    domain_identity: DomainIdentityResult | None
    @property
    def assessment_status(self) -> str:
        if not self.scan_result.successful:
            return "PARTIAL"
        if (
            self.domain_identity is not None
            and self.domain_identity.mismatch_detected
        ):
            return "PARTIAL"
        return "COMPLETE"
class ScanService:
    def run(
        self,
        url: str,
    ) -> FullScanResult:
        # --------------------------------------------------
        # 1. PRIMARY WEBSITE SCAN
        # --------------------------------------------------
        scanner = WebsiteScanner()
        scan_result = scanner.scan(
            url
        )
        if (
            not scan_result.successful
            and not scan_result.dns_resolution_failed
            and not scan_result.connection_failed
            and not scan_result.timeout_occurred
        ):
            raise RuntimeError(
                scan_result.error_message
                or "Website scan failed."
            )
        # --------------------------------------------------
        # 2. DEFAULT VALUES
        # --------------------------------------------------
        crawled_pages = []
        general_pages = []
        booking_links = []
        booking_provider = None
        link_results = []
        domain_identity = None
        # --------------------------------------------------
        # 3. WEBSITE CRAWLING
        # --------------------------------------------------
        if scan_result.successful:
            crawler = CrawlService()
            important_pages = (
                crawler.find_important_pages(
                    scan_result.internal_links
                )
            )
            crawled_pages = crawler.crawl(
                important_pages
            )
            # ----------------------------------------------
            # GENERAL SITE DISCOVERY
            # ----------------------------------------------
            general_urls = []
            seen_general_urls = set()
            candidate_urls = [
                scan_result.url,
                *crawler.discover_pages(
                    scan_result.internal_links
                ),
            ]
            for candidate_url in candidate_urls:
                normalised_url = (
                    candidate_url.rstrip("/")
                    + "/"
                )
                if normalised_url in seen_general_urls:
                    continue
                seen_general_urls.add(
                    normalised_url
                )
                general_urls.append(
                    candidate_url
                )
            general_pages = (
                crawler.crawl_general_pages(
                    general_urls
                )
            )
            homepage_content_text = ""
            if general_pages:
                homepage_content_text = (
                    general_pages[0].content_text
                )
            domain_identity_service = (
                DomainIdentityService()
            )
            domain_identity = (
                domain_identity_service.analyse(
                    scan_result.page_title,
                    homepage_content_text,
                )
            )
            domain_identity = (
                domain_identity_service.analyse(
                    scan_result.page_title,
                    homepage_content_text,
                )
            )
            # ----------------------------------------------
            # BOOKING DETECTION
            # ----------------------------------------------
            all_booking_links = set(
                scan_result.booking_links
            )
            for page in crawled_pages:
                if page.booking_links:
                    all_booking_links.update(
                        page.booking_links
                    )
            booking_links = sorted(
                link
                for link in all_booking_links
                if scanner.is_valid_booking_route(
                    link
                )
            )
            booking_provider = (
                scanner.detect_booking_provider(
                    booking_links
                )
            )
            # ----------------------------------------------
            # LINK HEALTH
            # ----------------------------------------------
            link_checker = LinkChecker()
            link_results = (
                link_checker.check_many(
                    scan_result.internal_links
                )
            )
        # --------------------------------------------------
        # 4. SITE QUALITY
        # --------------------------------------------------
        site_quality_service = (
            SiteQualityService()
        )
        site_quality = (
            site_quality_service.analyse(
                crawled_pages,
                booking_links,
            )
        )
        # --------------------------------------------------
        # 5. CONTENT QUALITY
        # --------------------------------------------------
        content_quality_service = (
            ContentQualityService()
        )
        content_quality = (
            content_quality_service.analyse(
                general_pages
            )
        )
        # --------------------------------------------------
        # 6. VISUAL ROOM ANALYSIS
        # --------------------------------------------------
        room_visual_result = None
        room_page_candidates = [
            page
            for page in crawled_pages
            if (
                page.page_type == "rooms"
                and page.successful
                and (
                    page.status_code is None
                    or page.status_code < 400
                )
            )
        ]
        if room_page_candidates:
            room_page = min(
                room_page_candidates,
                key=lambda page: len(page.url),
            )
            visual_service = VisualScanService()
            room_visual_result = visual_service.scan(
                room_page.url,
                width=1440,
                height=900,
            )
        # --------------------------------------------------
        # HOMEPAGE VISUAL ANALYSIS
        # --------------------------------------------------
        homepage_visual_result = None
        if scan_result.successful:
            visual_service = VisualScanService()
            homepage_visual_result = (
                visual_service.scan(
                    scan_result.url,
                    width=1440,
                    height=900,
                )
            )
        mobile_homepage_visual_result = None
        if scan_result.successful:
            visual_service = VisualScanService()
            mobile_homepage_visual_result = (
                visual_service.scan(
                    scan_result.url,
                    width=390,
                    height=844,
                )
            )
        # --------------------------------------------------
        # 7. ISSUE ANALYSIS
        # --------------------------------------------------
        issue_service = IssueService()
        issues = issue_service.analyse(
            scan_result=scan_result,
            crawled_pages=crawled_pages,
            booking_provider=booking_provider,
            all_booking_links=booking_links,
            link_results=link_results,
            visual_result=room_visual_result,
            homepage_visual_result=(
                homepage_visual_result
            ),
            mobile_homepage_visual_result=(
                mobile_homepage_visual_result
            ),
            domain_identity=domain_identity,
        )
        review_service = IssueReviewService()
        previous_review_statuses = (
            review_service.get_latest_review_statuses(
                scan_result.url
            )
        )
        for issue in issues:
            if not issue.issue_code:
                continue
            previous_status = (
                previous_review_statuses.get(
                    issue.issue_code
                )
            )
            if previous_status in (
                "CONFIRMED",
                "FALSE_POSITIVE",
                "IGNORED",
            ):
                issue.review_status = (
                    previous_status
                )
        # --------------------------------------------------
        # 7. TECHNICAL SCORE
        # --------------------------------------------------
        scoring_issues = [
            issue
            for issue in issues
            if (
                not issue.requires_review
                or issue.review_status == "CONFIRMED"
            )
        ]
        scoring_service = (
            ScoringService()
        )
        detected_score = (
            scoring_service.calculate(
                issues
            )
        )
        score = (
            scoring_service.calculate(
                scoring_issues
            )
        )
        # --------------------------------------------------
        # 8. COMMERCIAL SCORE
        # --------------------------------------------------
        commercial_scoring_service = (
            CommercialScoringService()
        )
        commercial_score = (
            commercial_scoring_service.calculate(
                technical_score=score,
                site_quality=site_quality,
                content_quality=content_quality,
            )
        )
        # --------------------------------------------------
        # 9. PROSPECT QUALIFICATION
        # --------------------------------------------------
        prospect_service = (
            ProspectService()
        )
        prospect = (
            prospect_service.qualify(
                score,
                commercial_score,
                issues,
            )
        )
        # --------------------------------------------------
        # 10. SAVE SCAN
        # --------------------------------------------------
        repository = ScanRepository()
        scan_id = repository.save(
            scan_result=scan_result,
            issues=issues,
            link_results=link_results,
            booking_provider=booking_provider,
            booking_links=booking_links,
            detected_score=detected_score.overall,
            overall_score=score.overall,
        )
        # --------------------------------------------------
        # 11. MONITORING COMPARISON
        # --------------------------------------------------
        monitoring_service = (
            MonitoringService()
        )
        comparison = (
            monitoring_service.compare_latest(
                scan_result.url
            )
        )
        # --------------------------------------------------
        # 12. RETURN COMPLETE RESULT
        # --------------------------------------------------
        return FullScanResult(
            scan_result=scan_result,
            crawled_pages=crawled_pages,
            general_pages=general_pages,
            link_results=link_results,
            booking_links=booking_links,
            booking_provider=booking_provider,
            issues=issues,
            score=score,
            site_quality=site_quality,
            content_quality=content_quality,
            commercial_score=commercial_score,
            prospect=prospect,
            scan_id=scan_id,
            comparison=comparison,
            domain_identity=domain_identity
        )