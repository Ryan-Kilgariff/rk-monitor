from services.website_scanner import WebsiteScanner
def test_detect_roomraccoon_uk():
    scanner = WebsiteScanner()
    provider = scanner.detect_booking_provider(
        [
            (
                "https://booking.roomraccoon.co.uk/"
                "the-clarendon-hotel/en/"
            )
        ]
    )
    assert provider == "RoomRaccoon"
def test_detect_roomraccoon_com():
    scanner = WebsiteScanner()
    provider = scanner.detect_booking_provider(
        [
            "https://booking.roomraccoon.com/example-hotel"
        ]
    )
    assert provider == "RoomRaccoon"
def test_detect_eviivo():
    scanner = WebsiteScanner()
    provider = scanner.detect_booking_provider(
        [
            "https://via.eviivo.com/example-hotel"
        ]
    )
    assert provider == "Eviivo"
def test_unknown_provider_returns_none():
    scanner = WebsiteScanner()
    provider = scanner.detect_booking_provider(
        [
            "https://booking.example.com/hotel"
        ]
    )
    assert provider is None