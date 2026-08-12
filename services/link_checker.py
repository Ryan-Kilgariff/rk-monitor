from dataclasses import dataclass
import requests
@dataclass
class LinkCheckResult:
    url: str
    status_code: int | None
    response_time: float | None
    successful: bool
    redirected: bool
    final_url: str | None
    error_message: str | None = None
class LinkChecker:
    def __init__(
        self,
        timeout: int = 8,
    ):
        self.timeout = timeout
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(compatible; RKMonitor/0.1; Website Monitoring)"
            )
        }
    def check(
        self,
        url: str,
    ) -> LinkCheckResult:
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True,
                stream=True,
            )
            elapsed = (
                response.elapsed.total_seconds()
            )
            redirected = (
                response.url.rstrip("/")
                != url.rstrip("/")
            )
            return LinkCheckResult(
                url=url,
                status_code=response.status_code,
                response_time=elapsed,
                successful=True,
                redirected=redirected,
                final_url=response.url,
            )
        except requests.RequestException as exc:
            return LinkCheckResult(
                url=url,
                status_code=None,
                response_time=None,
                successful=False,
                redirected=False,
                final_url=None,
                error_message=str(exc),
            )
    def check_many(
        self,
        urls: list[str],
        limit: int = 30,
    ) -> list[LinkCheckResult]:
        results = []
        for url in urls[:limit]:
            results.append(
                self.check(url)
            )
        return results