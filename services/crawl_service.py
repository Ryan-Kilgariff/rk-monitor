from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
@dataclass
@dataclass
class CrawledPage:
    url: str
    title: str | None
    status_code: int | None
    page_type: str
    successful: bool
    image_count: int = 0
    heading_count: int = 0
    link_count: int = 0
    booking_links: list[str] | None = None
class CrawlService:
    IMPORTANT_PAGE_TERMS = {
        "rooms": (
            "room",
            "rooms",
            "accommodation",
            "bedroom",
            "stay",
        ),
        "offers": (
            "offer",
            "offers",
            "special offer",
            "packages",
            "break",
        ),
        "dining": (
            "restaurant",
            "dining",
            "food",
            "eat",
            "bar",
        ),
        "events": (
            "wedding",
            "weddings",
            "event",
            "events",
            "conference",
            "meeting",
            "functions",
        ),
        "guest_information": (
            "guest information",
            "faq",
            "frequently asked",
            "information",
        ),
        "contact": (
            "contact",
            "find us",
            "location",
        ),
    }
    def __init__(
        self,
        timeout: int = 10,
        max_pages: int = 25,
    ):
        self.timeout = timeout
        self.max_pages = max_pages
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(compatible; RKMonitor/0.1; Website Monitoring)"
            )
        }
    def find_important_pages(
        self,
        links: list[str],
    ) -> list[tuple[str, str]]:
        important_pages = []
        for url in links:
            parsed = urlparse(url)
            path = parsed.path.lower().strip("/")
            if not path:
                continue
            path_words = (
                path.replace("-", " ")
                    .replace("_", " ")
                    .split()
            )
            page_type = self._classify_page(
                path,
                path_words,
            )
            if page_type:
                important_pages.append(
                    (url, page_type)
            )
        return important_pages[: self.max_pages]
    def crawl(
        self,
        pages: list[tuple[str, str]],
    ) -> list[CrawledPage]:
        results = []
        for url, page_type in pages:
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout,
                    allow_redirects=True,
                )
                soup = BeautifulSoup(
                    response.text,
                    "html.parser",
                )
                image_count = len(
                    soup.find_all("img")
                )
                heading_count = len(
                    soup.find_all(
                        ["h1", "h2", "h3"]
                    )
                )
                link_count = len(
                    soup.find_all(
                        "a",
                        href=True,
                    )
                )
                booking_links = self._find_booking_links(
                    response.url,
                    soup,
                )
                title = None
                if soup.title and soup.title.string:
                    title = soup.title.string.strip()
                results.append(
                CrawledPage(
                        url=response.url,
                        title=title,
                        status_code=response.status_code,
                        page_type=page_type,
                        successful=True,
                        image_count=image_count,
                        heading_count=heading_count,
                        link_count=link_count,
                        booking_links=booking_links,
                    )
                )
            except requests.RequestException:
                results.append(
                    CrawledPage(
                        url=url,
                        title=None,
                        status_code=None,
                        page_type=page_type,
                        successful=False,
                        booking_links=[],
                    )
                )
        return results
    def _find_booking_links(
        self,
        base_url: str,
        soup: BeautifulSoup,
    ) -> list[str]:
        booking_terms = (
            "book a room",
            "book room",
            "book your stay",
            "book your room",
            "check availability",
            "room availability",
            "reserve a room",
            "reserve your stay",
        )
        booking_domains = (
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
        links = set()
        for tag in soup.find_all(
            "a",
            href=True,
        ):
            href = tag["href"].strip()
            if not href:
                continue
            absolute_url = urljoin(
                base_url,
                href,
            )
            parsed = urlparse(
                absolute_url
            )
            domain = parsed.netloc.lower()
            link_text = tag.get_text(
                " ",
                strip=True,
            ).lower()
            if any(
                excluded in domain
                for excluded in excluded_domains
            ):
                continue
            text_match = any(
                term in link_text
                for term in booking_terms
            )
            domain_match = any(
                provider in domain
                for provider in booking_domains
            )
            if text_match or domain_match:
                links.add(
                    absolute_url
                )
        return sorted(links)
    def _classify_page(
        self,
        path: str,
        path_words: list[str],
    ) -> str | None:
        joined_path = " ".join(path_words)
        page_rules = {
            "rooms": (
                "room",
                "rooms",
                "accommodation",
                "bedroom",
                "bedrooms",
                "stay",
            ),
            "offers": (
                "offer",
                "offers",
                "package",
                "packages",
                "special offers",
            ),
            "dining": (
                "restaurant",
                "dining",
                "drink",
                "dine",
                "bar",
                "food",
            ),
            "events": (
                "wedding",
                "weddings",
                "event",
                "events",
                "conference",
                "conferences",
                "meeting",
                "meetings",
                "function",
                "functions",
            ),
            "guest_information": (
                "faq",
                "guest information",
                "guest-info",
                "guest-information",
            ),
            "contact": (
                "contact",
                "find us",
                "find-us",
                "location",
            ),
        }
        for page_type, terms in page_rules.items():
            for term in terms:
                normalised_term = (
                    term.replace("-", " ")
                )
                if normalised_term in joined_path:
                    return page_type
        return None