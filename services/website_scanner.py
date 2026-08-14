import requests
import urllib3
from requests.exceptions import SSLError
from requests.exceptions import ConnectionError
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import time
import requests
from bs4 import BeautifulSoup
@dataclass
class ScanResult:
    url: str
    status_code: int | None
    response_time: float | None
    page_title: str | None
    has_https: bool
    has_mobile_viewport: bool
    has_google_analytics: bool
    booking_links: list[str]
    internal_links: list[str]
    successful: bool
    ssl_verification_failed: bool
    ssl_error_message: str | None
    dns_resolution_failed: bool
    connection_failed: bool
    timeout_occurred: bool = False
    error_message: str | None = None
class WebsiteScanner:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(compatible; RKMonitor/0.1; Website Monitoring)"
            )
        }
    def _request_with_retry(
        self,
        url: str,
        verify: bool,
    ):
        transient_status_codes = {
            403,
            408,
            429,
            500,
            502,
            503,
            504,
        }
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True,
                verify=verify,
            )
        except requests.exceptions.Timeout:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True,
                verify=verify,
            )
        if (
            response.status_code
            in transient_status_codes
        ):
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True,
                verify=verify,
            )
        return response
    def scan(self, url: str) -> ScanResult:
        url = self._normalise_url(url)
        ssl_verification_failed = False
        ssl_error_message = None
        dns_resolution_failed = False
        connection_failed = False
        try:
            started = time.perf_counter()
            try:
                response = self._request_with_retry(
                    url,
                    verify=True,
                )
            except SSLError as exc:
                ssl_verification_failed = True
                ssl_error_message = str(exc)
                try:
                    response = self._request_with_retry(
                        url,
                        verify=False,
                    )
                except requests.exceptions.Timeout as timeout_exc:
                    return ScanResult(
                        url=url,
                        status_code=None,
                        response_time=None,
                        page_title=None,
                        has_https=url.startswith("https://"),
                        has_mobile_viewport=False,
                        has_google_analytics=False,
                        booking_links=[],
                        internal_links=[],
                        successful=False,
                        ssl_verification_failed=True,
                        ssl_error_message=ssl_error_message,
                        dns_resolution_failed=False,
                        connection_failed=False,
                        timeout_occurred=True,
                        error_message=str(timeout_exc),
                    )
            response_time = (
                time.perf_counter()
                - started
            )
            soup = BeautifulSoup(
                response.text,
                "html.parser",
            )
            response_time = time.perf_counter() - started
            soup = BeautifulSoup(response.text, "html.parser")
            page_title = self._get_page_title(soup)
            mobile_viewport = self._has_mobile_viewport(soup)
            google_analytics = self._has_google_analytics(
                response.text
            )
            urllib3.disable_warnings(
                urllib3.exceptions.InsecureRequestWarning
            )
            internal_links = self._get_internal_links(
                response.url,
                soup,
            )
            booking_links = self._get_booking_links(
                response.url,
                soup,
            )
            return ScanResult(
                url=response.url,
                status_code=response.status_code,
                response_time=response_time,
                page_title=page_title,
                has_https=response.url.startswith("https://"),
                has_mobile_viewport=mobile_viewport,
                has_google_analytics=google_analytics,
                booking_links=booking_links,
                internal_links=internal_links,
                successful=True,
                ssl_verification_failed=ssl_verification_failed,
                ssl_error_message=ssl_error_message,
                dns_resolution_failed=False,
                connection_failed=False,
                timeout_occurred=False,
            )
        except requests.exceptions.Timeout as exc:
            error_text = str(exc)
            return ScanResult(
                url=url,
                status_code=None,
                response_time=None,
                page_title=None,
                has_https=url.startswith("https://"),
                has_mobile_viewport=False,
                has_google_analytics=False,
                booking_links=[],
                internal_links=[],
                successful=False,
                ssl_verification_failed=False,
                ssl_error_message=None,
                dns_resolution_failed=False,
                connection_failed=False,
                timeout_occurred=True,
                error_message=error_text,
            )
        except ConnectionError as exc:
            error_text = str(exc)
            error_lower = error_text.lower()
            ssl_handshake_failed = any(
                term in error_lower
                for term in (
                    "handshake failure",
                    "ssl handshake",
                    "tlsv1 alert",
                    "sslv3 alert",
                    "wrong version number",
                    "protocol version",
                )
            )
            dns_resolution_failed = any(
                term in error_lower
                for term in (
                    "nameresolutionerror",
                    "failed to resolve",
                    "getaddrinfo failed",
                    "name or service not known",
                )
            )
            connection_failed = (
                not dns_resolution_failed
            )
            return ScanResult(
                url=url,
                status_code=None,
                response_time=None,
                page_title=None,
                has_https=url.startswith("https://"),
                has_mobile_viewport=False,
                has_google_analytics=False,
                booking_links=[],
                internal_links=[],
                successful=False,
                ssl_verification_failed=ssl_handshake_failed,
                ssl_error_message=(
                    error_text
                    if ssl_handshake_failed
                    else None
                ),
                dns_resolution_failed=dns_resolution_failed,
                connection_failed=connection_failed,
                timeout_occurred=False,
                error_message=error_text,
            )
        except requests.RequestException as exc:
            error_text = str(exc)
            error_lower = error_text.lower()
            ssl_handshake_failed = any(
                term in error_lower
                for term in (
                    "handshake failure",
                    "ssl handshake",
                    "tlsv1 alert",
                    "sslv3 alert",
                    "wrong version number",
                    "protocol version",
                )
            )
            dns_resolution_failed = any(
                term in error_lower
                for term in (
                    "nameresolutionerror",
                    "failed to resolve",
                    "getaddrinfo failed",
                    "name or service not known",
                )
            )
            return ScanResult(
                url=url,
                status_code=None,
                response_time=None,
                page_title=None,
                has_https=url.startswith("https://"),
                has_mobile_viewport=False,
                has_google_analytics=False,
                booking_links=[],
                internal_links=[],
                successful=False,
                ssl_verification_failed=ssl_handshake_failed,
                ssl_error_message=(
                    error_text
                    if ssl_handshake_failed
                    else None
                ),
                dns_resolution_failed=dns_resolution_failed,
                connection_failed=(
                    not dns_resolution_failed
                ),
                timeout_occurred=False,
                error_message=error_text,
            )
    def _normalise_url(self, url: str) -> str:
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        return url
    def _get_page_title(
        self,
        soup: BeautifulSoup,
    ) -> str | None:
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        return None
    def _has_mobile_viewport(
        self,
        soup: BeautifulSoup,
    ) -> bool:
        viewport = soup.find(
            "meta",
            attrs={"name": "viewport"},
        )
        return viewport is not None
    def _has_google_analytics(
        self,
        html: str,
    ) -> bool:
        indicators = (
            "googletagmanager.com",
            "google-analytics.com",
            "gtag(",
            "G-",
        )
        return any(
            indicator in html
            for indicator in indicators
        )
    def _get_internal_links(
        self,
        base_url: str,
        soup: BeautifulSoup,
    ) -> list[str]:
        base_domain = urlparse(base_url).netloc
        links = set()
        for tag in soup.find_all("a", href=True):
            href = tag["href"].strip()
            if not href:
                continue
            absolute_url = urljoin(base_url, href)
            parsed = urlparse(absolute_url)
            if parsed.scheme not in ("http", "https"):
                continue
            if parsed.netloc != base_domain:
                continue
            clean_url = absolute_url.split("#")[0]
            links.add(clean_url)
        return sorted(links)
    def _get_booking_links(
        self,
        base_url: str,
        soup: BeautifulSoup,
    ) -> list[str]:
        hotel_booking_terms = (
            "book a room",
            "book room",
            "book your stay",
            "book your room",
            "book this room",
            "check availability",
            "room availability",
            "reserve a room",
            "reserve your stay",
            "hotel booking",
            "make a reservation",
            "make your reservation",
            "book online",
            "booking online",
            "make a booking",
            "book immediately online",
        )
        hotel_booking_domains = (
            "eviivo.com",
            "mews.com",
            "cloudbeds.com",
            "siteminder.com",
            "littlehotelier.com",
            "roomraccoon.com",
            "guestline.net",
            "synxis.com",
            "bookingbutton.com",
            "freeonlinebooking.com",
            "direct-book.com",
        )
        excluded_domains = (
            "facebook.com",
            "instagram.com",
            "twitter.com",
            "x.com",
            "linkedin.com",
            "youtube.com",
            "tiktok.com",
            "opentable.com",
            "tripadvisor.com",
        )
        excluded_terms = (
            "book a table",
            "reserve a table",
            "restaurant booking",
            "table booking",
            "book restaurant",
        )
        links = set()
        for tag in soup.find_all("a", href=True):
            href = tag["href"].strip()
            if not href:
                continue
            absolute_url = urljoin(base_url, href)
            parsed = urlparse(absolute_url)
            link_text = tag.get_text(
                " ",
                strip=True,
            ).lower()
            href_lower = absolute_url.lower()
            domain = parsed.netloc.lower()
            if any(
                excluded_domain in domain
                for excluded_domain in excluded_domains
            ):
                continue
            if any(
                term in link_text
                for term in excluded_terms
            ):
                continue
            text_match = any(
                term in link_text
                for term in hotel_booking_terms
            )
            domain_match = any(
                booking_domain in domain
                for booking_domain in hotel_booking_domains
            )
            href_match = any(
                term.replace(" ", "-") in href_lower
                or term.replace(" ", "") in href_lower
                for term in hotel_booking_terms
            )
            if text_match or domain_match or href_match:
                links.add(absolute_url)
        return sorted(links)
    def is_valid_booking_route(
        self,
        url: str,
    ) -> bool:
        parsed = urlparse(url)
        path = (
            parsed.path
            .lower()
            .strip("/")
        )
        path_words = (
            path
            .replace("-", " ")
            .replace("_", " ")
            .replace("/", " ")
            .replace(".", " ")
            .split()
        )
        if not path_words:
            return True
        article_starters = {
            "how",
            "why",
            "what",
            "which",
            "when",
            "where",
            "who",
        }
        if (
            path_words[0] in article_starters
            and len(path_words) >= 4
        ):
            return False
        return True
    def detect_booking_provider(
        self,
        booking_links: list[str],
    ) -> str | None:
        providers = {
            "eviivo": "Eviivo",
            "mews.com": "Mews",
            "cloudbeds.com": "Cloudbeds",
            "siteminder.com": "SiteMinder",
            "littlehotelier.com": "Little Hotelier",
            "roomraccoon.com": "RoomRaccoon",
            "guestline.net": "Guestline",
            "synxis.com": "SynXis",
            "bookingbutton.com": "BookingButton",
            "freeonlinebooking.com": "FreeOnlineBooking",
            "direct-book.com": "Direct Book",
        }
        for link in booking_links:
            link_lower = link.lower()
            for indicator, provider_name in providers.items():
                if indicator in link_lower:
                    return provider_name
        return None