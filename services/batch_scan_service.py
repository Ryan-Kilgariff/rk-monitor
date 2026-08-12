from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from services.scan_service import ScanService, FullScanResult
@dataclass
class BatchScanItem:
    url: str
    successful: bool
    result: FullScanResult | None
    error_message: str | None
@dataclass
class BatchScanResult:
    items: list[BatchScanItem]
    @property
    def successful_items(
        self,
    ) -> list[BatchScanItem]:
        return [
            item
            for item in self.items
            if item.successful
        ]
    @property
    def failed_items(
        self,
    ) -> list[BatchScanItem]:
        return [
            item
            for item in self.items
            if not item.successful
        ]
class BatchScanService:
    def __init__(
        self,
        max_sites: int = 50,
        max_workers: int = 4,
    ):
        self.max_sites = max_sites
        self.max_workers = max_workers
    def run(
        self,
        urls: list[str],
    ) -> BatchScanResult:
        cleaned_urls = self._clean_urls(
            urls
        )
        urls_to_scan = cleaned_urls[
            : self.max_sites
        ]
        items = []
        with ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            futures = {
                executor.submit(
                    self._scan_one,
                    url,
                ): url
                for url in urls_to_scan
            }
            completed = 0
            total = len(futures)
            for future in as_completed(
                futures
            ):
                item = future.result()
                items.append(item)
                completed += 1
                status = (
                    "OK"
                    if item.successful
                    else "FAILED"
                )
                print(
                    f"[{completed}/{total}] "
                    f"{status} - {item.url}"
                )
        return BatchScanResult(
            items=items
        )
    def _scan_one(
        self,
        url: str,
    ) -> BatchScanItem:
        scan_service = ScanService()
        try:
            result = scan_service.run(
                url
            )
            return BatchScanItem(
                url=url,
                successful=True,
                result=result,
                error_message=None,
            )
        except Exception as exc:
            return BatchScanItem(
                url=url,
                successful=False,
                result=None,
                error_message=str(exc),
            )
    def _clean_urls(
        self,
        urls: list[str],
    ) -> list[str]:
        cleaned = []
        seen = set()
        for url in urls:
            url = url.strip()
            if not url:
                continue
            if url in seen:
                continue
            seen.add(url)
            cleaned.append(url)
        return cleaned