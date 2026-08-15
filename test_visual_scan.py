from services.visual_scan_service import (
    VisualScanService,
)
scanner = VisualScanService()
result = scanner.scan(
    "https://www.thefalstafframsgate.com/hotelrooms",
    width=1440,
    height=900,
)
print()
print("VISUAL SCAN")
print("-" * 60)
print(
    f"Successful: {result.successful}"
)
print(
    f"Title: {result.page_title}"
)
print(
    f"Viewport: "
    f"{result.viewport_width} x "
    f"{result.viewport_height}"
)
print(
    f"Rendered Page: "
    f"{result.page_width} x "
    f"{result.page_height}"
)
print(
    f"Horizontal Overflow: "
    f"{result.horizontal_overflow}"
)
print(
    f"Broken Images: "
    f"{result.broken_images}"
)
print(
    f"Overflow Elements: "
    f"{len(result.overflow_elements)}"
)
print(
    f"Critical Overflow: "
    f"{result.critical_overflow_elements}"
)
print(
    f"Off-screen Elements: "
    f"{result.offscreen_elements}"
)
print(
    f"Header Detected: "
    f"{result.header_detected}"
)
print(
    f"Header Height: "
    f"{result.header_height}px"
)
print(
    f"Header Viewport Ratio: "
    f"{result.header_viewport_ratio:.2f}"
)
print(
    f"Header Position: "
    f"{result.header_position}"
)
print(
    f"Header Element: "
    f"{result.header_tag}"
)
print(
    f"Header Class: "
    f"{result.header_class}"
)
print(
    f"Oversized Header: "
    f"{result.oversized_header}"
)
print()
print("TOP / BRANDING IMAGES")
print("-" * 60)
print(
    f"Images Detected: "
    f"{len(result.branding_images)}"
)
for image in result.branding_images:
    print()
    print(
        f"  Alt: {image['alt']}"
    )
    print(
        f"  Class: "
        f"{image['className']}"
    )
    print(
        f"  Position: "
        f"{image['left']}, "
        f"{image['top']}"
    )
    print(
        f"  Rendered: "
        f"{image['renderedWidth']} x "
        f"{image['renderedHeight']}"
    )
    print(
        f"  Native: "
        f"{image['naturalWidth']} x "
        f"{image['naturalHeight']}"
    )
    print(
        f"  Scale Ratio: "
        f"{image['scaleRatio']:.2f}x"
    )
    print(
        f"  Likely Logo: "
        f"{image['likelyLogo']}"
    )
    print(
        f"  Source: "
        f"{image['src'][:120]}"
    )
print()
print("NAVIGATION")
print("-" * 60)
print(
    f"Navigation Detected: "
    f"{result.navigation_detected}"
)
print(
    f"Navigation Width: "
    f"{result.navigation_width}px"
)
print(
    f"Navigation Viewport Ratio: "
    f"{result.navigation_viewport_ratio:.2f}"
)
print(
    f"Navigation Overflow: "
    f"{result.navigation_overflow}"
)
print(
    f"Navigation Items: "
    f"{result.navigation_item_count}"
)
print(
    f"Longest Label: "
    f"{result.navigation_longest_label}"
)
print(
    f"Longest Label Length: "
    f"{result.navigation_longest_label_length}"
)
print(
    f"Navigation Dense: "
    f"{result.navigation_dense}"
)
print(
    f"Navigation Issue: "
    f"{result.navigation_issue}"
)
print()
print("ROOM / CONTENT IMAGES")
print("-" * 60)
print(
    f"Content Images: "
    f"{result.content_image_count}"
)
print(
    f"Large Content Images: "
    f"{result.large_content_image_count}"
)
print(
    f"Small Content Images: "
    f"{result.small_content_image_count}"
)
print(
    f"Upscaled Images: "
    f"{result.upscaled_image_count}"
)
print(
    f"Background Images: "
    f"{result.background_image_count}"
)
print(
    f"Substantial Visual Images: "
    f"{result.substantial_visual_image_count}"
)
print(
    f"Room Offerings: "
    f"{result.room_offering_count}"
)
print(
    f"Offering Detection Source: "
    f"{result.room_offering_source}"
)
print(
    f"Images Per Room Offering: "
    f"{result.images_per_room_offering:.2f}"
)
print(
    f"Room Presentation Issue: "
    f"{result.room_presentation_issue}"
)
print()
print("ROOM OFFERING CANDIDATES")
print("-" * 60)
for offering in result.room_offerings:
    print()
    print(
        f"  Tag: {offering['tag']}"
    )
    print(
        f"  Class: "
        f"{offering['className']}"
    )
    print(
        f"  Heading: "
        f"{offering['heading']}"
    )
    print(
        f"  Link: "
        f"{offering['href']}"
    )
    print(
        f"  Size: "
        f"{offering['width']} x "
        f"{offering['height']}"
    )
    print(
        f"  Text: "
        f"{offering['text']}"
    )
    print()
print("ROOM STRUCTURE CANDIDATES")
print("-" * 60)
for candidate in (
    result.room_structure_candidates
):
    print()
    print(
        f"  Type: "
        f"{candidate['type']}"
    )
    print(
        f"  Text: "
        f"{candidate['text']}"
    )
    if candidate["href"]:
        print(
            f"  Link: "
            f"{candidate['href']}"
        )
for image in result.background_images:
    print()
    print(
        f"  Background Element: "
        f"{image['tag']}"
    )
    print(
        f"  Class: "
        f"{image['className']}"
    )
    print(
        f"  Rendered: "
        f"{image['renderedWidth']} x "
        f"{image['renderedHeight']}"
    )
    print(
        f"  Background: "
        f"{image['backgroundImage'][:120]}"
    )
for image in result.content_images:
    print()
    print(
        f"  Alt: {image['alt']}"
    )
    print(
        f"  Rendered: "
        f"{image['renderedWidth']} x "
        f"{image['renderedHeight']}"
    )
    print(
        f"  Native: "
        f"{image['naturalWidth']} x "
        f"{image['naturalHeight']}"
    )
    print(
        f"  Scale Ratio: "
        f"{image['scaleRatio']:.2f}x"
    )
    print(
        f"  Source: "
        f"{image['src'][:100]}"
    )
for element in result.overflow_elements:
    print()
    print(
        f"  {element['tag']} "
        f"id='{element['id']}' "
        f"class='{element['className']}'"
    )
    print(
        f"  Left: {element['left']} "
        f"Right: {element['right']} "
        f"Width: {element['width']}"
    )
    print(
    f"  Fully Off-screen: "
    f"{element['fullyOffScreen']}"
    )
    print(
        f"  Partially Clipped: "
        f"{element['partiallyClipped']}"
    )
    if element["text"]:
        print(
            f"  Text: {element['text']}"
        )
if result.error_message:
    print(
        f"Error: {result.error_message}"
    )