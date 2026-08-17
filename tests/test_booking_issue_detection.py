from types import SimpleNamespace
from services.issue_service import IssueService
def _successful_scan_result():
    return SimpleNamespace(
        dns_resolution_failed=False,
        connection_failed=False,
        timeout_occurred=False,
    )
def test_known_booking_provider_does_not_create_unknown_issue():
    service = IssueService()
    issues = service._analyse_booking_journey(
        scan_result=_successful_scan_result(),
        crawled_pages=[],
        booking_provider="RoomRaccoon",
        all_booking_links=[
            (
                "https://booking.roomraccoon.co.uk/"
                "example-hotel"
            )
        ],
    )
    unknown_provider_issues = [
        issue
        for issue in issues
        if issue.issue_code
        == "booking.provider_unrecognised"
    ]
    assert unknown_provider_issues == []
def test_unknown_booking_provider_requires_review():
    service = IssueService()
    issues = service._analyse_booking_journey(
        scan_result=_successful_scan_result(),
        crawled_pages=[],
        booking_provider=None,
        all_booking_links=[
            "https://booking.example.com/example-hotel"
        ],
    )
    unknown_provider_issues = [
        issue
        for issue in issues
        if issue.issue_code
        == "booking.provider_unrecognised"
    ]
    assert len(unknown_provider_issues) == 1
    issue = unknown_provider_issues[0]
    assert issue.severity == "LOW"
    assert issue.confidence == "MEDIUM"
    assert issue.requires_review is True
def test_rooms_without_booking_route_creates_one_booking_issue():
    service = IssueService()
    room_page = SimpleNamespace(
        page_type="rooms",
    )
    issues = service._analyse_booking_journey(
        scan_result=_successful_scan_result(),
        crawled_pages=[room_page],
        booking_provider=None,
        all_booking_links=[],
    )
    booking_issues = [
        issue
        for issue in issues
        if issue.category == "Booking Journey"
    ]
    assert len(booking_issues) == 1
    assert (
        booking_issues[0].title
        == "Rooms detected without booking path"
    )