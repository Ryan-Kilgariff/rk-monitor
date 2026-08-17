from types import SimpleNamespace
from services.site_quality_service import (
    SiteQualityService,
)
def test_homepage_with_strong_room_evidence_counts_as_rooms():
    service = SiteQualityService()
    homepage = SimpleNamespace(
        successful=True,
        page_type="general",
        url="https://examplehotel.com/",
        content_text=(
            "Explore our Rooms and Suites "
            "and choose your perfect stay."
        ),
        booking_links=[
            "https://booking.example.com/room-1",
            "https://booking.example.com/room-2",
        ],
        image_count=8,
    )
    result = service.analyse(
        crawled_pages=[homepage],
        booking_links=homepage.booking_links,
    )
    assert result.has_rooms is True
    assert result.room_page_count == 1
    assert result.room_image_count == 8
def test_homepage_with_weak_room_mention_does_not_count_as_rooms():
        service = SiteQualityService()
        homepage = SimpleNamespace(
            successful=True,
            page_type="general",
            url="https://examplehotel.com/",
            content_text=(
                "Our hotel has comfortable rooms "
                "and a welcoming restaurant."
            ),
            booking_links=[],
            image_count=6,
        )
        result = service.analyse(
            crawled_pages=[homepage],
            booking_links=[],
        )
        assert result.has_rooms is False
        assert result.room_page_count == 0