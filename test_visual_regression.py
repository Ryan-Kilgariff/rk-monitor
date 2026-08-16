from services.visual_scan_service import (
    VisualScanService,
)
def run_check(
    name: str,
    url: str,
    width: int,
    height: int,
    checks: dict,
) -> bool | None:
    print()
    print("=" * 70)
    print(name)
    print("=" * 70)
    print(url)
    print(
        f"Viewport: {width} x {height}"
    )
    scanner = VisualScanService()
    result = scanner.scan(
        url,
        width=width,
        height=height,
    )
    if not result.successful:
        print()
        print("SCAN INCONCLUSIVE")
        print(
            result.error_message
            or "Unknown visual scan error."
        )
        return None
    all_passed = True
    print()
    print("CHECKS")
    print("-" * 70)
    for field_name, expected in checks.items():
        actual = getattr(
            result,
            field_name,
        )
        passed = actual == expected
        status = (
            "PASS"
            if passed
            else "FAIL"
        )
        print(
            f"{status:4} | "
            f"{field_name}: "
            f"expected={expected!r} "
            f"actual={actual!r}"
        )
        if not passed:
            all_passed = False
    print()
    print(
        "RESULT: "
        + (
            "PASS"
            if all_passed
            else "FAIL"
        )
    )
    return all_passed
def main() -> None:
    controls = [
        {
            "name": (
                "Desktop Navigation - "
                "Wycliffe Bad Control"
            ),
            "url": (
                "https://www.wycliffeguesthouse.co.uk/"
            ),
            "width": 1440,
            "height": 900,
            "checks": {
                "navigation_issue": True,
                "navigation_overflow": True,
            },
        },
        {
            "name": (
                "Desktop Navigation - "
                "Falstaff Good Control"
            ),
            "url": (
                "https://www.thefalstafframsgate.com/"
            ),
            "width": 1440,
            "height": 900,
            "checks": {
                "navigation_issue": False,
                "navigation_overflow": False,
            },
        },
        {
            "name": (
                "Mobile Layout - "
                "House Ramsgate Bad Control"
            ),
            "url": (
                "https://thehouseatramsgate.co.uk/"
            ),
            "width": 390,
            "height": 844,
            "checks": {
                "navigation_issue": True,
            },
        },
        {
            "name": (
                "Mobile Layout - "
                "Falstaff Good Control"
            ),
            "url": (
                "https://www.thefalstafframsgate.com/"
            ),
            "width": 390,
            "height": 844,
            "checks": {
                "navigation_issue": False,
                "critical_overflow_elements": 0,
            },
        },
        {
            "name": (
                "Room Presentation - "
                "Castaways Bad Control"
            ),
            "url": (
                "https://castawaysdungeness.com/rooms/"
            ),
            "width": 1440,
            "height": 900,
            "checks": {
                "room_offering_count": 4,
                "room_offering_source": (
                    "room_links"
                ),
                "room_presentation_issue": True,
            },
        },
        {
            "name": (
                "Room Presentation - "
                "Saint Peters Good Control"
            ),
            "url": (
                "https://www.saintpetersbandb.co.uk/rooms"
            ),
            "width": 1440,
            "height": 900,
            "checks": {
                "room_offering_count": 4,
                "room_offering_source": (
                    "room_headings"
                ),
                "room_presentation_issue": False,
            },
        },
        {
            "name": (
                "Room Presentation - "
                "Falstaff Good Control"
            ),
            "url": (
                "https://www.thefalstafframsgate.com/hotelrooms"
            ),
            "width": 1440,
            "height": 900,
            "checks": {
                "room_offering_count": 9,
                "room_offering_source": (
                    "room_links"
                ),
                "room_presentation_issue": False,
            },
        },
        {
            "name": (
                "Healthy Site - "
                "New Inn Desktop"
            ),
            "url": (
                "https://www.newinn-sandwich.co.uk/"
            ),
            "width": 1440,
            "height": 900,
            "checks": {
                "horizontal_overflow": False,
                "navigation_issue": False,
                "broken_images": 0,
            },
        },
        {
            "name": (
                "Healthy Site - "
                "New Inn Mobile"
            ),
            "url": (
                "https://www.newinn-sandwich.co.uk/"
            ),
            "width": 390,
            "height": 844,
            "checks": {
                "horizontal_overflow": False,
                "navigation_issue": False,
                "broken_images": 0,
            },
        },
        {
            "name": (
                "Healthy Site - "
                "Rocksalt Desktop"
            ),
            "url": (
                "https://www.rocksaltfolkestone.co.uk/"
            ),
            "width": 1440,
            "height": 900,
            "checks": {
                "horizontal_overflow": False,
                "navigation_issue": False,
                "broken_images": 0,
            },
        },
        {
            "name": (
                "Healthy Site - "
                "Rocksalt Mobile"
            ),
            "url": (
                "https://www.rocksaltfolkestone.co.uk/"
            ),
            "width": 390,
            "height": 844,
            "checks": {
                "horizontal_overflow": False,
                "navigation_issue": False,
                "broken_images": 0,
            },
        },
        {
            "name": (
                "Healthy Site - "
                "Clarendon Desktop"
            ),
            "url": (
                "https://www.theclarendon-hotel.com/"
            ),
            "width": 1440,
            "height": 900,
            "checks": {
                "horizontal_overflow": False,
                "navigation_issue": False,
                "broken_images": 0,
            },
        },
        {
            "name": (
                "Healthy Site - "
                "Clarendon Mobile"
            ),
            "url": (
                "https://www.theclarendon-hotel.com/"
            ),
            "width": 390,
            "height": 844,
            "checks": {
                "horizontal_overflow": False,
                "navigation_issue": False,
                "broken_images": 0,
            },
        },
        {
            "name": (
                "Mobile Layout - "
                "Judds Folly Bad Control"
            ),
            "url": (
                "https://www.juddsfollyhotel.co.uk/"
            ),
            "width": 390,
            "height": 844,
            "checks": {
                "horizontal_overflow": True,
                "navigation_overflow": True,
                "navigation_issue": True,
            },
        },
        {
            "name": (
                "Healthy Site - "
                "Judds Folly Desktop"
            ),
            "url": (
                "https://www.juddsfollyhotel.co.uk/"
            ),
            "width": 1440,
            "height": 900,
            "checks": {
                "horizontal_overflow": False,
                "navigation_issue": False,
                "broken_images": 0,
            },
        },
    ]
    passed = 0
    failed = 0
    inconclusive = 0
    for control in controls:
        result = run_check(
            name=control["name"],
            url=control["url"],
            width=control["width"],
            height=control["height"],
            checks=control["checks"],
        )
        if result is True:
            passed += 1
        elif result is False:
            failed += 1
        else:
            inconclusive += 1
    print()
    print("=" * 70)
    print("VISUAL REGRESSION SUMMARY")
    print("=" * 70)
    print(
        f"Passed:       {passed}"
    )
    print(
        f"Failed:       {failed}"
    )
    print(
        f"Inconclusive: {inconclusive}"
    )
    print(
        f"Total:        "
        f"{passed + failed + inconclusive}"
    )
    if failed > 0:
        print()
        print(
            "VISUAL REGRESSION "
            "FAILURES DETECTED"
        )
    elif inconclusive > 0:
        print()
        print(
            "NO REGRESSION FAILURES DETECTED"
        )
        print(
            f"{inconclusive} CONTROL(S) "
            f"WERE INCONCLUSIVE"
        )
    else:
        print()
        print(
            "ALL VISUAL REGRESSION "
            "CONTROLS PASSED"
        )
if __name__ == "__main__":
    main()