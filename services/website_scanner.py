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
    def scan(self, url: str) -> ScanResult:
        url = self._normalise_url(url)
        try:
            started = time.perf_counter()
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True,
            )
            response_time = time.perf_counter() - started
            soup = BeautifulSoup(response.text, "html.parser")
            page_title = self._get_page_title(soup)
            mobile_viewport = self._has_mobile_viewport(soup)
            google_analytics = self._has_google_analytics(
                response.text
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
            )
        except requests.RequestException as exc:
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
                error_message=str(exc),
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
        }
        for link in booking_links:
            link_lower = link.lower()
            for indicator, provider_name in providers.items():
                if indicator in link_lower:
                    return provider_name
        return None