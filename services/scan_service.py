from dataclasses import dataclass
from services.website_scanner import WebsiteScanner, ScanResult
from services.crawl_service import CrawlService, CrawledPage
from services.link_checker import LinkChecker, LinkCheckResult
from services.issue_service import IssueService, Issue
from services.scoring_service import ScoringService, ScoreResult
from services.prospect_service import ProspectService, ProspectResult
from services.scan_repository import ScanRepository
from services.monitoring_service import MonitoringService, ScanComparison
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
class ScanService:
    def run(
        self,
        url: str,
    ) -> FullScanResult:
        scanner = WebsiteScanner()
        scan_result = scanner.scan(url)
        if (
            not scan_result.successful
            and not scan_result.dns_resolution_failed
            and not scan_result.connection_failed
        ):
            raise RuntimeError(
            scan_result.error_message
            or "Website scan failed."
        )
        crawled_pages = []
        booking_links = []
        booking_provider = None
        link_results = []
        if scan_result.successful:
            crawler = CrawlService()
            important_pages = crawler.find_important_pages(
                scan_result.internal_links
            )
            crawled_pages = crawler.crawl(
                important_pages
            )
            all_booking_links = set(
                scan_result.booking_links
            )
            for page in crawled_pages:
                if page.booking_links:
                    all_booking_links.update(
                        page.booking_links
                    )
            booking_links = sorted(
                all_booking_links
            )
            booking_provider = scanner.detect_booking_provider(
                booking_links
            )
            link_checker = LinkChecker()
            link_results = link_checker.check_many(
                scan_result.internal_links
            )
        issue_service = IssueService()
        issues = issue_service.analyse(
            scan_result=scan_result,
            crawled_pages=crawled_pages,
            booking_provider=booking_provider,
            all_booking_links=booking_links,
            link_results=link_results,
        )
        scoring_service = ScoringService()
        score = scoring_service.calculate(
            issues
        )
        prospect_service = ProspectService()
        prospect = prospect_service.qualify(
            score,
            issues,
        )
        repository = ScanRepository()
        scan_id = repository.save(
            scan_result=scan_result,
            issues=issues,
            link_results=link_results,
            booking_provider=booking_provider,
            booking_links=booking_links,
            overall_score=score.overall,
        )
        monitoring_service = (
            MonitoringService()
        )
        comparison = (
            monitoring_service.compare_latest(
                scan_result.url
            )
        )
        return FullScanResult(
            scan_result=scan_result,
            crawled_pages=crawled_pages,
            link_results=link_results,
            booking_links=booking_links,
            booking_provider=booking_provider,
            issues=issues,
            score=score,
            prospect=prospect,
            scan_id=scan_id,
            comparison=comparison,
        )