from concurrent.futures import ThreadPoolExecutor
import time
from services.website_scanner import WebsiteScanner
from services.link_checker import LinkChecker
def check_timed(
    checker: LinkChecker,
    url: str,
):
    start = time.perf_counter()
    result = checker.check(
        url
    )
    duration = (
        time.perf_counter()
        - start
    )
    return (
        duration,
        url,
        result.status_code,
        result.successful,
        result.error_message,
    )
scanner = WebsiteScanner()
scan_result = scanner.scan(
    "https://www.rocksaltfolkestone.co.uk/"
)
checker = LinkChecker()
urls = scan_result.internal_links[:30]
print(
    "CHECKING",
    len(urls),
    "LINKS",
)
with ThreadPoolExecutor(
    max_workers=6
) as executor:
    futures = [
        executor.submit(
            check_timed,
            checker,
            url,
        )
        for url in urls
    ]
    results = [
        future.result()
        for future in futures
    ]
results.sort(
    key=lambda item: item[0],
    reverse=True,
)
print()
for (
    duration,
    url,
    status_code,
    successful,
    error_message,
) in results:
    print(
        f"{duration:.1f}s | "
        f"{status_code} | "
        f"{successful} | "
        f"{url}"
    )
    if error_message:
        print(
            f"    ERROR: {error_message}"
        )