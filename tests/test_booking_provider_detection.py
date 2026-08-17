import pytest
from services.website_scanner import WebsiteScanner
@pytest.mark.parametrize(
    ("booking_url", "expected_provider"),
    [
        (
            "https://booking.roomraccoon.co.uk/example-hotel",
            "RoomRaccoon",
        ),
        (
            "https://booking.roomraccoon.com/example-hotel",
            "RoomRaccoon",
        ),
        (
            "https://via.eviivo.com/example-hotel",
            "Eviivo",
        ),
        (
            "https://booking.mews.com/example-hotel",
            "Mews",
        ),
        (
            "https://booking.cloudbeds.com/example-hotel",
            "Cloudbeds",
        ),
        (
            "https://booking.siteminder.com/example-hotel",
            "SiteMinder",
        ),
        (
            "https://booking.littlehotelier.com/example-hotel",
            "Little Hotelier",
        ),
        (
            "https://booking.guestline.net/example-hotel",
            "Guestline",
        ),
        (
            "https://booking.synxis.com/example-hotel",
            "SynXis",
        ),
        (
            "https://booking.bookingbutton.com/example-hotel",
            "BookingButton",
        ),
        (
            "https://booking.freeonlinebooking.com/example-hotel",
            "FreeOnlineBooking",
        ),
        (
            "https://booking.direct-book.com/example-hotel",
            "Direct Book",
        ),
    ],
)
def test_detect_known_booking_provider(
    booking_url,
    expected_provider,
):
    scanner = WebsiteScanner()
    provider = scanner.detect_booking_provider(
        [booking_url]
    )
    assert provider == expected_provider
def test_unknown_provider_returns_none():
    scanner = WebsiteScanner()
    provider = scanner.detect_booking_provider(
        [
            "https://booking.example.com/hotel"
        ]
    )
    assert provider is None