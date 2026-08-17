from services.website_scanner import WebsiteScanner
def test_valid_hotel_booking_route_is_accepted():
    scanner = WebsiteScanner()
    result = scanner.is_valid_booking_route(
        "https://booking.roomraccoon.co.uk/example-hotel"
    )
    assert result is True
def test_eviivo_booking_route_is_accepted():
    scanner = WebsiteScanner()
    result = scanner.is_valid_booking_route(
        "https://via.eviivo.com/example-hotel"
    )
    assert result is True
def test_restaurant_booking_route_is_rejected():
    scanner = WebsiteScanner()
    result = scanner.is_valid_booking_route(
        "https://www.opentable.com/r/example-restaurant"
    )
    assert result is False
def test_random_external_link_is_rejected():
    scanner = WebsiteScanner()
    result = scanner.is_valid_booking_route(
        "https://example.com/about-us"
    )
    assert result is False