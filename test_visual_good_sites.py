from services.visual_scan_service import (
    VisualScanService,
)
SITES = [
    (
        "Corner Broadstairs",
        "https://thecornerbroadstairs.co.uk/",
    ),
    (
        "Clarendon Hotel",
        "https://www.theclarendon-hotel.com/",
    ),
    (
        "Judds Folly Hotel",
        "https://www.juddsfollyhotel.co.uk/",
    ),
]
def print_result(
    name: str,
    url: str,
    width: int,
    height: int,
) -> None:
    scanner = VisualScanService()
    result = scanner.scan(
        url,
        width=width,
        height=height,
    )
    print()
    print("=" * 70)
    print(
        f"{name} - "
        f"{width} x {height}"
    )
    print("=" * 70)
    print(url)
    if not result.successful:
        print(
            "Status: INCONCLUSIVE"
        )
        print(
            "Reason: "
            f"{result.error_message}"
        )
        return
    print("Status: SUCCESS")
    print(
        "Horizontal Overflow: "
        f"{result.horizontal_overflow}"
    )
    print(
        "Critical Overflow: "
        f"{result.critical_overflow_elements}"
    )
    print(
        "Off-screen Elements: "
        f"{result.offscreen_elements}"
    )
    print(
        "Oversized Header: "
        f"{result.oversized_header}"
    )
    print(
        "Navigation Detected: "
        f"{result.navigation_detected}"
    )
    print(
        "Navigation Overflow: "
        f"{result.navigation_overflow}"
    )
    print(
        "Navigation Dense: "
        f"{result.navigation_dense}"
    )
    print(
        "Navigation Issue: "
        f"{result.navigation_issue}"
    )
    print(
        "Broken Images: "
        f"{result.broken_images}"
    )
def main() -> None:
    for name, url in SITES:
        print_result(
            name,
            url,
            width=1440,
            height=900,
        )
        print_result(
            name,
            url,
            width=390,
            height=844,
        )
if __name__ == "__main__":
    main()