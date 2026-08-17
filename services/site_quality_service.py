from dataclasses import dataclass
from services.crawl_service import CrawledPage
@dataclass
class SiteQualityResult:
    has_rooms: bool
    has_dining: bool
    has_events: bool
    has_offers: bool
    has_guest_information: bool
    has_contact_page: bool
    has_booking_route: bool
    room_page_count: int
    room_image_count: int
    important_page_count: int
    quality_score: int
class SiteQualityService:
    def analyse(
        self,
        crawled_pages: list[CrawledPage],
        booking_links: list[str],
    ) -> SiteQualityResult:
        successful_pages = [
            page
            for page in crawled_pages
            if page.successful
        ]
        page_types = {
            page.page_type
            for page in successful_pages
        }
        room_pages = [
            page
            for page in successful_pages
            if page.page_type == "rooms"
        ]
        homepage_room_pages = [
            page
            for page in successful_pages
            if (
                page.url.rstrip("/").count("/") == 2
                and any(
                    term in (
                        (page.content_text or "")
                        .lower()
                    )
                    for term in (
                        "rooms",
                        "room",
                        "suites",
                        "suite",
                        "accommodation",
                    )
                )
                and len(page.booking_links) >= 2
            )
        ]
        for page in homepage_room_pages:
            if page not in room_pages:
                room_pages.append(page)
        has_rooms = bool(room_pages)
        has_dining = (
            "dining" in page_types
        )
        has_events = (
            "events" in page_types
        )
        has_offers = (
            "offers" in page_types
        )
        has_guest_information = (
            "guest_information"
            in page_types
        )
        has_contact_page = (
            "contact" in page_types
        )
        has_booking_route = bool(
            booking_links
        )
        room_page_count = len(
            room_pages
        )
        room_image_count = sum(
            page.image_count
            for page in room_pages
        )
        important_page_count = len(
            page_types
        )
        score = 100
        # Accommodation is fundamental
        if not has_rooms:
            score -= 30
        # A detected rooms section should
        # contain meaningful imagery
        if (
            has_rooms
            and room_image_count < 4
        ):
            score -= 15
        # Booking route is commercially important
        if not has_booking_route:
            score -= 25
        # Helpful but not catastrophic
        if not has_guest_information:
            score -= 5
        # Dedicated contact page is useful,
        # but contact information may exist elsewhere
        if not has_contact_page:
            score -= 5
        # Extremely shallow structure
        if important_page_count <= 1:
            score -= 10
        elif important_page_count == 2:
            score -= 5
        return SiteQualityResult(
            has_rooms=has_rooms,
            has_dining=has_dining,
            has_events=has_events,
            has_offers=has_offers,
            has_guest_information=(
                has_guest_information
            ),
            has_contact_page=(
                has_contact_page
            ),
            has_booking_route=(
                has_booking_route
            ),
            room_page_count=(
                room_page_count
            ),
            room_image_count=(
                room_image_count
            ),
            important_page_count=(
                important_page_count
            ),
            quality_score=max(
                0,
                score,
            ),
        )