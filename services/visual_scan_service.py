from dataclasses import dataclass
from playwright.sync_api import sync_playwright
@dataclass
class VisualScanResult:
    url: str
    successful: bool
    page_title: str | None
    viewport_width: int
    viewport_height: int
    page_width: int
    page_height: int
    horizontal_overflow: bool
    overflow_elements: list[dict]
    critical_overflow_elements: int
    offscreen_elements: int
    header_detected: bool
    header_height: int
    header_viewport_ratio: float
    header_position: str | None
    header_tag: str | None
    header_class: str | None
    oversized_header: bool
    branding_images: list[dict]
    navigation_detected: bool
    navigation_width: int
    navigation_viewport_ratio: float
    navigation_overflow: bool
    navigation_item_count: int
    navigation_longest_label: str | None
    navigation_longest_label_length: int
    navigation_dense: bool
    navigation_issue: bool
    content_image_count: int
    large_content_image_count: int
    small_content_image_count: int
    upscaled_image_count: int
    content_images: list[dict]
    background_image_count: int
    background_images: list[dict]
    substantial_visual_image_count: int
    room_offering_count: int
    room_offering_source: str
    room_offerings: list[dict]
    images_per_room_offering: float
    room_presentation_issue: bool
    room_structure_candidates: list[dict]
    broken_images: int
    error_message: str | None = None
class VisualScanService:
    def _is_specific_room_label(
        self,
        text: str,
    ) -> bool:
        cleaned = " ".join(
            text.lower().split()
        )
        if not cleaned:
            return False
        generic_labels = {
            "room",
            "rooms",
            "our rooms",
            "hotel rooms",
            "our hotel rooms",
            "accommodation",
            "book a room",
            "book room",
        }
        if cleaned in generic_labels:
            return False
        generic_prefixes = (
            "our rooms &",
            "our rooms and",
            "find out more",
            "castaways offers",
        )
        if cleaned.startswith(
            generic_prefixes
        ):
            return False
        excluded_terms = (
            "accessibility",
            "review",
            "parking",
            "book a room",
            "booking",
        )
        if any(
            term in cleaned
            for term in excluded_terms
        ):
            return False
        room_terms = (
            "room",
            "suite",
            "double",
            "twin",
            "single",
            "family",
            "king",
            "superior",
            "deluxe",
        )
        if not any(
            term in cleaned
            for term in room_terms
        ):
            return False
        if len(cleaned) > 110:
            return False
        return True
    def _get_room_offering_count(
        self,
        structure_candidates: list[dict],
        visual_offerings: list[dict],
    ) -> tuple[int, str]:
        specific_links = {
            " ".join(
                candidate["text"]
                .lower()
                .split()
            )
            for candidate in structure_candidates
            if (
                candidate["type"] == "link"
                and self._is_specific_room_label(
                    candidate["text"]
                )
            )
        }
        if specific_links:
            return (
                len(specific_links),
                "room_links",
            )
        specific_headings = {
            " ".join(
                candidate["text"]
                .lower()
                .split()
            )
            for candidate in structure_candidates
            if (
                candidate["type"] == "heading"
                and self._is_specific_room_label(
                    candidate["text"]
                )
            )
        }
        if specific_headings:
            return (
                len(specific_headings),
                "room_headings",
            )
        if visual_offerings:
            return (
                len(visual_offerings),
                "visual_cards",
            )
        return (0, "none")
    def scan(
        self,
        url: str,
        width: int = 390,
        height: int = 844,
    ) -> VisualScanResult:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True
                )
                page = browser.new_page(
                    viewport={
                        "width": width,
                        "height": height,
                    }
                )
                page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=30000,
                )
                page.wait_for_timeout(1500)
                page_title = page.title()
                challenge_titles = {
                    "one moment, please...",
                    "just a moment...",
                    "checking your browser...",
                    "attention required!",
                }
                normalised_title = (
                    page_title
                    .strip()
                    .lower()
                )
                if normalised_title in challenge_titles:
                    browser.close()
                    return VisualScanResult(
                                url=url,
                                successful=False,
                                page_title=page_title,
                                viewport_width=width,
                                viewport_height=height,
                                page_width=0,
                                page_height=0,
                                horizontal_overflow=False,
                                overflow_elements=[],
                                critical_overflow_elements=0,
                                offscreen_elements=0,
                                header_detected=False,
                                header_height=0,
                                header_viewport_ratio=0.0,
                                header_position=None,
                                header_tag=None,
                                header_class=None,
                                oversized_header=False,
                                branding_images=[],
                                navigation_detected=False,
                                navigation_width=0,
                                navigation_viewport_ratio=0.0,
                                navigation_overflow=False,
                                navigation_item_count=0,
                                navigation_longest_label=None,
                                navigation_longest_label_length=0,
                                navigation_dense=False,
                                navigation_issue=False,
                                content_image_count=0,
                                large_content_image_count=0,
                                small_content_image_count=0,
                                upscaled_image_count=0,
                                content_images=[],
                                background_image_count=0,
                                background_images=[],
                                substantial_visual_image_count=0,
                                room_offering_count=0,
                                room_offering_source="none",
                                room_offerings=[],
                                room_structure_candidates=[],
                                images_per_room_offering=0.0,
                                room_presentation_issue=False,
                                broken_images=0,
                                error_message=(
                                    "Visual scan blocked by "
                                    "challenge/interstitial page."
                                ),
                            )
                dimensions = page.evaluate(
                    """
                    () => ({
                        pageWidth:
                            document.documentElement.scrollWidth,
                        pageHeight:
                            document.documentElement.scrollHeight
                    })
                    """
                )
                overflow_elements = page.evaluate(
                    """
                    () => {
                        const viewportWidth =
                            document.documentElement.clientWidth;
                        const isVisible = element => {
                            const style =
                                window.getComputedStyle(element);
                            if (
                                style.display === "none" ||
                                style.visibility === "hidden" ||
                                parseFloat(style.opacity || "1") === 0
                            ) {
                                return false;
                            }
                            if (
                                element.getAttribute(
                                    "aria-hidden"
                                ) === "true"
                            ) {
                                return false;
                            }
                            const rect =
                                element.getBoundingClientRect();
                            if (
                                rect.width <= 0 ||
                                rect.height <= 0
                            ) {
                                return false;
                            }
                            return true;
                        };
                        const isIntentionalOffCanvas =
                            element => {
                                const rect =
                                    element.getBoundingClientRect();
                                const style =
                                    window.getComputedStyle(element);
                                const classText =
                                    typeof element.className === "string"
                                        ? element.className.toLowerCase()
                                        : "";
                                const role = (
                                    element.getAttribute("role") || ""
                                ).toLowerCase();
                                const likelyNavigation =
                                    element.closest(
                                        "nav, [role='navigation']"
                                    ) !== null ||
                                    role === "navigation" ||
                                    classText.includes("menu") ||
                                    classText.includes("nav");
                                const fullyOffScreen =
                                    rect.right <= 0 ||
                                    rect.left >= viewportWidth;
                                const isSkipLink =
                                element.tagName.toLowerCase() === "a" &&
                                (
                                    classText.includes("skip-link") ||
                                    (element.innerText || "")
                                        .toLowerCase()
                                        .includes("skip to content")
                                );
                                const elementTitle = (
                                    element.getAttribute("title") || ""
                                ).toLowerCase();

                                const elementSrc = (
                                    element.getAttribute("src") || ""
                                ).toLowerCase();
                                const isKnownFloatingWidget =
                                    classText.includes("grecaptcha-badge") ||
                                    classText.includes("recaptcha") ||
                                    element.closest(
                                        ".grecaptcha-badge"
                                    ) !== null ||
                                    (
                                        element.tagName.toLowerCase() === "iframe" &&
                                        (
                                            elementTitle.includes("recaptcha") ||
                                            elementSrc.includes("recaptcha") ||
                                            elementSrc.includes("google.com/recaptcha")
                                        )
                                    );
                                const isKnownCarousel =
                                    classText.includes("carousel") ||
                                    classText.includes("slider") ||
                                    classText.includes("slides") ||
                                    classText.includes("slick-track") ||
                                    classText.includes("swiper-wrapper");
                                const transformed =
                                    style.transform !== "none";
                                if (
                                    isSkipLink ||
                                    isKnownFloatingWidget ||
                                    isKnownCarousel ||
                                    (
                                        fullyOffScreen &&
                                        (
                                            likelyNavigation ||
                                            transformed
                                        )
                                    )
                                ) {
                                    return true;
                                }
                                return false;
                            };
                        const isOverflowing = element => {
                            const rect =
                                element.getBoundingClientRect();
                            return (
                                rect.width > 0 &&
                                (
                                    rect.left < -2 ||
                                    rect.right >
                                        viewportWidth + 2
                                )
                            );
                        };
                        const candidates = Array.from(
                            document.querySelectorAll("body *")
                        )
                        .filter(
                            element =>
                                isVisible(element) &&
                                !isIntentionalOffCanvas(element) &&
                                isOverflowing(element)
                        );
                        const rootCandidates = candidates.filter(
                            element => {
                                const parent = element.parentElement;
                                if (!parent) {
                                    return true;
                                }
                                return !(
                                    isVisible(parent) &&
                                    !isIntentionalOffCanvas(parent) &&
                                    isOverflowing(parent)
                                );
                            }
                        );
                        return rootCandidates
                        .map(element => {
                            const rect =
                                element.getBoundingClientRect();
                            return {
                                tag:
                                    element.tagName.toLowerCase(),
                                id:
                                    element.id || "",
                                className:
                                    typeof element.className === "string"
                                        ? element.className
                                        : "",
                                text:
                                    (element.innerText || "")
                                        .trim()
                                        .replace(/\\s+/g, " ")
                                        .slice(0, 120),
                                left:
                                    Math.round(rect.left),
                                right:
                                    Math.round(rect.right),
                                width:
                                    Math.round(rect.width),
                                fullyOffScreen:
                                    rect.right <= 0 ||
                                    rect.left >= viewportWidth,
                                partiallyClipped:
                                    (
                                        rect.left < 0 &&
                                        rect.right > 0
                                    ) ||
                                    (
                                        rect.left < viewportWidth &&
                                        rect.right > viewportWidth
                                    ),
                            };
                        })
                        .slice(0, 25);
                    }
                    """
                )
                header_metrics = page.evaluate(
                    """
                    () => {
                        const viewportWidth =
                            window.innerWidth;
                        const viewportHeight =
                            window.innerHeight;
                        const isVisible = element => {
                            const style =
                                window.getComputedStyle(element);
                            const rect =
                                element.getBoundingClientRect();
                            return !(
                                style.display === "none" ||
                                style.visibility === "hidden" ||
                                parseFloat(
                                    style.opacity || "1"
                                ) === 0 ||
                                rect.width <= 0 ||
                                rect.height <= 0
                            );
                        };
                        const candidates = Array.from(
                            document.querySelectorAll(
                                "body *"
                            )
                        )
                        .filter(element => {
                            if (!isVisible(element)) {
                                return false;
                            }
                            const rect =
                                element.getBoundingClientRect();
                            /*
                            * Header candidates should begin
                            * close to the top of the page.
                            */
                            if (
                                rect.top > 180 ||
                                rect.bottom <= 0
                            ) {
                                return false;
                            }
                            /*
                            * Ignore tiny controls and narrow
                            * individual navigation items.
                            */
                            if (
                                rect.width <
                                    viewportWidth * 0.65 ||
                                rect.height < 30
                            ) {
                                return false;
                            }
                            /*
                            * Avoid treating the whole page
                            * wrapper as a header.
                            */
                            if (
                                rect.height >
                                    viewportHeight * 0.80
                            ) {
                                return false;
                            }
                            return true;
                        })
                        .map(element => {
                            const rect =
                                element.getBoundingClientRect();
                            const style =
                                window.getComputedStyle(element);
                            const links =
                                element.querySelectorAll("a");
                            const navElements =
                                element.querySelectorAll(
                                    "nav, [role='navigation']"
                                );
                            const buttons =
                                element.querySelectorAll(
                                    "button, [role='button']"
                                );
                            const images =
                                element.querySelectorAll(
                                    "img, svg"
                                );
                            const contactLinks =
                                element.querySelectorAll(
                                    "a[href^='tel:'], " +
                                    "a[href^='mailto:']"
                                );
                            const classText = (
                                typeof element.className ===
                                "string"
                                    ? element.className
                                    : ""
                            ).toLowerCase();
                            const idText = (
                                element.id || ""
                            ).toLowerCase();
                            let score = 0;
                            if (links.length >= 2) {
                                score += 2;
                            }
                            if (links.length >= 4) {
                                score += 1;
                            }
                            if (navElements.length > 0) {
                                score += 3;
                            }
                            if (buttons.length > 0) {
                                score += 1;
                            }
                            if (images.length > 0) {
                                score += 1;
                            }
                            if (contactLinks.length > 0) {
                                score += 1;
                            }
                            if (
                                classText.includes("header") ||
                                classText.includes("nav") ||
                                classText.includes("menu") ||
                                idText.includes("header") ||
                                idText.includes("nav")
                            ) {
                                score += 2;
                            }
                            if (
                                element.tagName.toLowerCase()
                                === "header"
                            ) {
                                score += 3;
                            }
                            return {
                                element,
                                score,
                                height:
                                    Math.round(rect.height),
                                width:
                                    Math.round(rect.width),
                                top:
                                    Math.round(rect.top),
                                position:
                                    style.position,
                                tag:
                                    element.tagName
                                        .toLowerCase(),
                                className:
                                    typeof element.className
                                        === "string"
                                            ? element.className
                                            : "",
                            };
                        })
                        .filter(
                            candidate =>
                                candidate.score >= 3
                        );
                        if (candidates.length === 0) {
                            return {
                                detected: false,
                                height: 0,
                                ratio: 0,
                                position: null,
                                tag: null,
                                className: null,
                            };
                        }
                        /*
                        * Highest structural score wins.
                        * For equal scores prefer the
                        * smaller container, which avoids
                        * selecting a giant page wrapper.
                        */
                        candidates.sort(
                            (a, b) => {
                                if (b.score !== a.score) {
                                    return b.score - a.score;
                                }
                                return a.height - b.height;
                            }
                        );
                        const best = candidates[0];
                        return {
                            detected: true,
                            height:
                                best.height,
                            ratio:
                                best.height /
                                viewportHeight,
                            position:
                                best.position,
                            tag:
                                best.tag,
                            className:
                                best.className,
                        };
                    }
                    """
                )
                branding_images = page.evaluate(
                    """
                    () => {
                        const viewportHeight =
                            window.innerHeight;
                        return Array.from(
                            document.querySelectorAll("img")
                        )
                        .map(image => {
                            const rect =
                                image.getBoundingClientRect();
                            const style =
                                window.getComputedStyle(image);
                            const classText =
                                typeof image.className === "string"
                                    ? image.className
                                    : "";
                            const altText =
                                image.getAttribute("alt") || "";
                            const src =
                                image.currentSrc ||
                                image.getAttribute("src") ||
                                "";
                            const identityText = (
                                classText +
                                " " +
                                altText +
                                " " +
                                src
                            ).toLowerCase();
                            const renderedWidth =
                                Math.round(rect.width);
                            const renderedHeight =
                                Math.round(rect.height);
                            const naturalWidth =
                                image.naturalWidth || 0;
                            const naturalHeight =
                                image.naturalHeight || 0;
                            const widthScale =
                                naturalWidth > 0
                                    ? renderedWidth /
                                        naturalWidth
                                    : 0;
                            const heightScale =
                                naturalHeight > 0
                                    ? renderedHeight /
                                        naturalHeight
                                    : 0;
                            const scaleRatio =
                                Math.max(
                                    widthScale,
                                    heightScale
                                );
                            const likelyLogo =
                                identityText.includes("logo") ||
                                identityText.includes("brand");
                            return {
                                alt:
                                    altText,
                                className:
                                    classText,
                                src:
                                    src,
                                top:
                                    Math.round(rect.top),
                                left:
                                    Math.round(rect.left),
                                renderedWidth:
                                    renderedWidth,
                                renderedHeight:
                                    renderedHeight,
                                naturalWidth:
                                    naturalWidth,
                                naturalHeight:
                                    naturalHeight,
                                scaleRatio:
                                    Math.round(
                                        scaleRatio * 100
                                    ) / 100,
                                likelyLogo:
                                    likelyLogo,
                                visible:
                                    !(
                                        style.display === "none" ||
                                        style.visibility === "hidden" ||
                                        rect.width <= 0 ||
                                        rect.height <= 0
                                    ),
                            };
                        })
                        .filter(image =>
                            image.visible &&
                            image.top >= -100 &&
                            image.top <
                                Math.min(
                                    viewportHeight,
                                    500
                                )
                        )
                        .slice(0, 15);
                    }
                    """
                )
                navigation_metrics = page.evaluate(
                    """
                    () => {
                        const viewportWidth =
                            window.innerWidth;
                        const isVisible = element => {
                            const style =
                                window.getComputedStyle(element);
                            const rect =
                                element.getBoundingClientRect();
                            return !(
                                style.display === "none" ||
                                style.visibility === "hidden" ||
                                parseFloat(
                                    style.opacity || "1"
                                ) === 0 ||
                                rect.width <= 0 ||
                                rect.height <= 0
                            );
                        };
                        const candidates = Array.from(
                            document.querySelectorAll(
                                "nav, [role='navigation']"
                            )
                        )
                        .filter(
                            element =>
                                isVisible(element)
                        )
                        .map(element => {
                            const rect =
                                element.getBoundingClientRect();
                            const links = Array.from(
                                element.querySelectorAll("a")
                            )
                            .filter(link => {
                                const linkRect =
                                    link.getBoundingClientRect();
                                const style =
                                    window.getComputedStyle(link);
                                return !(
                                    style.display === "none" ||
                                    style.visibility === "hidden" ||
                                    linkRect.width <= 0 ||
                                    linkRect.height <= 0
                                );
                            });
                            const labels = links
                                .map(link =>
                                    (link.innerText || "")
                                        .trim()
                                        .replace(/\\s+/g, " ")
                                )
                                .filter(
                                    label =>
                                        label.length > 0
                                );
                            const uniqueLabels = [
                                ...new Set(labels)
                            ];
                            let longestLabel = "";
                            for (
                                const label
                                of uniqueLabels
                            ) {
                                if (
                                    label.length >
                                    longestLabel.length
                                ) {
                                    longestLabel = label;
                                }
                            }
                            const overflow =
                                rect.left < -2 ||
                                rect.right >
                                    viewportWidth + 2;
                            return {
                                width:
                                    Math.round(rect.width),
                                left:
                                    Math.round(rect.left),
                                right:
                                    Math.round(rect.right),
                                itemCount:
                                    uniqueLabels.length,
                                longestLabel:
                                    longestLabel,
                                longestLabelLength:
                                    longestLabel.length,
                                overflow:
                                    overflow,
                                ratio:
                                    rect.width /
                                    viewportWidth,
                            };
                        })
                        .filter(
                            candidate =>
                                candidate.itemCount >= 2
                        );
                        if (
                            candidates.length === 0
                        ) {
                            return {
                                detected: false,
                                width: 0,
                                ratio: 0,
                                overflow: false,
                                itemCount: 0,
                                longestLabel: null,
                                longestLabelLength: 0,
                            };
                        }
                        /*
                        * Prefer the navigation containing
                        * the greatest number of visible
                        * navigation items.
                        */
                        candidates.sort(
                            (a, b) => {
                                if (
                                    b.itemCount !==
                                    a.itemCount
                                ) {
                                    return (
                                        b.itemCount -
                                        a.itemCount
                                    );
                                }
                                return (
                                    b.width -
                                    a.width
                                );
                            }
                        );
                        const best =
                            candidates[0];
                        return {
                            detected: true,
                            width:
                                best.width,
                            ratio:
                                best.ratio,
                            overflow:
                                best.overflow,
                            itemCount:
                                best.itemCount,
                            longestLabel:
                                best.longestLabel,
                            longestLabelLength:
                                best.longestLabelLength,
                        };
                    }
                    """
                )
                content_image_metrics = page.evaluate(
                    """
                    () => {
                        const viewportWidth =
                            window.innerWidth;
                        const images = Array.from(
                            document.querySelectorAll("img")
                        )
                        .map(image => {
                            const rect =
                                image.getBoundingClientRect();
                            const style =
                                window.getComputedStyle(image);
                            const classText = (
                                typeof image.className === "string"
                                    ? image.className
                                    : ""
                            );
                            const altText =
                                image.getAttribute("alt") || "";
                            const src =
                                image.currentSrc ||
                                image.getAttribute("src") ||
                                "";
                            const identityText = (
                                classText +
                                " " +
                                altText +
                                " " +
                                src
                            ).toLowerCase();
                            const renderedWidth =
                                Math.round(rect.width);
                            const renderedHeight =
                                Math.round(rect.height);
                            const naturalWidth =
                                image.naturalWidth || 0;
                            const naturalHeight =
                                image.naturalHeight || 0;
                            const widthScale =
                                naturalWidth > 0
                                    ? renderedWidth /
                                        naturalWidth
                                    : 0;
                            const heightScale =
                                naturalHeight > 0
                                    ? renderedHeight /
                                        naturalHeight
                                    : 0;
                            const scaleRatio =
                                Math.max(
                                    widthScale,
                                    heightScale
                                );
                            const visible = !(
                                style.display === "none" ||
                                style.visibility === "hidden" ||
                                parseFloat(
                                    style.opacity || "1"
                                ) === 0 ||
                                rect.width <= 0 ||
                                rect.height <= 0
                            );
                            const likelyBranding =
                                identityText.includes("logo") ||
                                identityText.includes("brand");
                            const likelyIcon =
                                renderedWidth <= 80 &&
                                renderedHeight <= 80;
                            return {
                                alt:
                                    altText,
                                className:
                                    classText,
                                src:
                                    src,
                                top:
                                    Math.round(rect.top),
                                renderedWidth:
                                    renderedWidth,
                                renderedHeight:
                                    renderedHeight,
                                naturalWidth:
                                    naturalWidth,
                                naturalHeight:
                                    naturalHeight,
                                scaleRatio:
                                    Math.round(
                                        scaleRatio * 100
                                    ) / 100,
                                visible:
                                    visible,
                                likelyBranding:
                                    likelyBranding,
                                likelyIcon:
                                    likelyIcon,
                            };
                        })
                        .filter(image =>
                            image.visible &&
                            !image.likelyBranding &&
                            !image.likelyIcon
                        );
                        const substantial = images.filter(
                            image =>
                                image.renderedWidth >= 200 &&
                                image.renderedHeight >= 120
                        );
                        const small = images.filter(
                            image =>
                                (
                                    image.renderedWidth < 200 ||
                                    image.renderedHeight < 120
                                )
                        );
                        const upscaled = images.filter(
                            image =>
                                image.scaleRatio > 1.15
                        );
                        const backgroundImages = Array.from(
                            document.querySelectorAll("body *")
                        )
                        .map(element => {
                            const rect =
                                element.getBoundingClientRect();
                            const style =
                                window.getComputedStyle(element);
                            const backgroundImage =
                                style.backgroundImage || "";
                            const visible = !(
                                style.display === "none" ||
                                style.visibility === "hidden" ||
                                parseFloat(
                                    style.opacity || "1"
                                ) === 0 ||
                                rect.width <= 0 ||
                                rect.height <= 0
                            );
                            const hasBackgroundImage =
                                backgroundImage !== "none" &&
                                backgroundImage.includes("url(");
                           const className =
                                typeof element.className === "string"
                                    ? element.className
                                    : "";
                            const identityText = (
                                className +
                                " " +
                                backgroundImage
                            ).toLowerCase();
                            const likelyDecorative =
                                identityText.includes("blur") ||
                                identityText.includes("background") ||
                                identityText.includes("pattern") ||
                                identityText.includes("texture") ||
                                className
                                    .toLowerCase()
                                    .includes("parallax");
                            return {
                                tag:
                                    element.tagName
                                        .toLowerCase(),
                                className:
                                    className,
                                backgroundImage:
                                    backgroundImage,
                                top:
                                    Math.round(rect.top),
                                renderedWidth:
                                    Math.round(rect.width),
                                renderedHeight:
                                    Math.round(rect.height),
                                visible:
                                    visible,
                                hasBackgroundImage:
                                    hasBackgroundImage,
                                likelyDecorative:
                                    likelyDecorative,
                            };
                        })
                        .filter(item =>
                            item.visible &&
                            item.hasBackgroundImage &&
                            !item.likelyDecorative &&
                            item.renderedWidth >= 200 &&
                            item.renderedHeight >= 120
                        )
                        .slice(0, 30);
                        return {
                            total:
                                images.length,
                            large:
                                substantial.length,
                            small:
                                small.length,
                            upscaled:
                                upscaled.length,
                            images:
                                images.slice(0, 30),
                            backgroundImages:
                                backgroundImages,
                            backgroundImageCount:
                                backgroundImages.length,
                        };
                    }
                    """
                )
                room_metrics = page.evaluate(
                    """
                    () => {
                        const roomTerms = [
                            "room",
                            "suite",
                            "double",
                            "twin",
                            "single",
                            "family",
                            "king",
                            "superior",
                            "deluxe"
                        ];
                        const isVisible = element => {
                            const style =
                                window.getComputedStyle(element);
                            const rect =
                                element.getBoundingClientRect();
                            return !(
                                style.display === "none" ||
                                style.visibility === "hidden" ||
                                parseFloat(
                                    style.opacity || "1"
                                ) === 0 ||
                                rect.width <= 0 ||
                                rect.height <= 0
                            );
                        };
                        const hasSubstantialVisual =
                            element => {
                                const images = Array.from(
                                    element.querySelectorAll("img")
                                );
                                const normalImage =
                                    images.some(image => {
                                        const rect =
                                            image.getBoundingClientRect();
                                        return (
                                            rect.width >= 200 &&
                                            rect.height >= 120
                                        );
                                    });
                                if (normalImage) {
                                    return true;
                                }
                                const descendants = [
                                    element,
                                    ...element.querySelectorAll("*")
                                ];
                                return descendants.some(
                                    child => {
                                        const rect =
                                            child.getBoundingClientRect();
                                        const style =
                                            window.getComputedStyle(
                                                child
                                            );
                                        return (
                                            style.backgroundImage !==
                                                "none" &&
                                            style.backgroundImage.includes(
                                                "url("
                                            ) &&
                                            rect.width >= 200 &&
                                            rect.height >= 120
                                        );
                                    }
                                );
                            };
                        const candidates = Array.from(
                            document.querySelectorAll(
                                "article, section, li, " +
                                "[class*='room'], " +
                                "[class*='suite'], " +
                                "[class*='accommodation']"
                            )
                        )
                        .filter(element => {
                            if (!isVisible(element)) {
                                return false;
                            }
                            const rect =
                                element.getBoundingClientRect();
                            if (
                                rect.height < 120 ||
                                rect.height > 1200
                            ) {
                                return false;
                            }
                            const text = (
                                element.innerText || ""
                            )
                            .trim()
                            .toLowerCase();
                            const classText = (
                                typeof element.className ===
                                    "string"
                                    ? element.className
                                    : ""
                            ).toLowerCase();
                            const roomContext =
                                roomTerms.some(
                                    term =>
                                        text.includes(term) ||
                                        classText.includes(term)
                                );
                            return (
                                roomContext &&
                                hasSubstantialVisual(element)
                            );
                        });
                        /*
                        * Keep the smallest qualifying
                        * visual room container.
                        *
                        * If a child also qualifies, the
                        * larger parent is just a wrapper.
                        */
                        const visualCards = candidates.filter(
                            element =>
                                !candidates.some(
                                    other =>
                                        other !== element &&
                                        element.contains(other)
                                )
                        );
                        const offerings = visualCards.map(
                            element => {
                                const rect =
                                    element.getBoundingClientRect();
                                const heading =
                                    element.querySelector(
                                        "h1, h2, h3, h4, h5, h6"
                                    );
                                const link =
                                    element.querySelector(
                                        "a[href]"
                                    );
                                const text = (
                                    element.innerText || ""
                                )
                                .trim()
                                .replace(/\\s+/g, " ")
                                .slice(0, 160);
                                return {
                                    tag:
                                        element.tagName
                                            .toLowerCase(),
                                    className:
                                        typeof element.className ===
                                            "string"
                                            ? element.className
                                            : "",
                                    heading:
                                        heading
                                            ? (
                                                heading.innerText ||
                                                ""
                                            ).trim()
                                            : "",
                                    href:
                                        link
                                            ? link.href
                                            : "",
                                    text:
                                        text,
                                    width:
                                        Math.round(
                                            rect.width
                                        ),
                                    height:
                                        Math.round(
                                            rect.height
                                        ),
                                };
                            }
                        );
                        return {
                            count:
                                offerings.length,
                            offerings:
                                offerings.slice(0, 30),
                        };
                    }
                    """
                )
                room_structure_candidates = page.evaluate(
                    """
                    () => {
                        const roomTerms = [
                            "room",
                            "suite",
                            "double",
                            "twin",
                            "single",
                            "family",
                            "king",
                            "superior",
                            "deluxe"
                        ];
                        const results = [];
                        const addCandidate = (
                            type,
                            text,
                            href = ""
                        ) => {
                            const cleaned = (
                                text || ""
                            )
                            .trim()
                            .replace(/\\s+/g, " ");
                            if (!cleaned) {
                                return;
                            }
                            const lower =
                                cleaned.toLowerCase();
                            if (
                                !roomTerms.some(
                                    term =>
                                        lower.includes(term)
                                )
                            ) {
                                return;
                            }
                            results.push({
                                type:
                                    type,
                                text:
                                    cleaned.slice(
                                        0,
                                        160
                                    ),
                                href:
                                    href,
                            });
                        };
                        for (
                            const heading of
                            document.querySelectorAll(
                                "h1, h2, h3, h4, h5, h6"
                            )
                        ) {
                            addCandidate(
                                "heading",
                                heading.innerText
                            );
                        }
                        for (
                            const link of
                            document.querySelectorAll(
                                "a[href]"
                            )
                        ) {
                            addCandidate(
                                "link",
                                link.innerText,
                                link.href
                            );
                        }
                        for (
                            const option of
                            document.querySelectorAll(
                                "option"
                            )
                        ) {
                            addCandidate(
                                "option",
                                option.innerText
                            );
                        }
                        const unique = [];
                        const seen = new Set();
                        for (const item of results) {
                            const key = (
                                item.type +
                                "|" +
                                item.text.toLowerCase() +
                                "|" +
                                item.href
                            );
                            if (seen.has(key)) {
                                continue;
                            }
                            seen.add(key);
                            unique.push(item);
                        }
                        return unique.slice(0, 40);
                    }
                    """
                )
                broken_images = page.evaluate(
                    """
                    () => Array.from(
                        document.images
                    ).filter(
                        image => {
                            const source = (
                                image.currentSrc ||
                                image.src ||
                                ""
                            ).trim();
                            if (!source) {
                                return false;
                            }
                            return (
                                image.complete &&
                                image.naturalWidth === 0
                            );
                        }
                    ).length
                    """
                )
                page_width = dimensions[
                    "pageWidth"
                ]
                page_height = dimensions[
                    "pageHeight"
                ]
                horizontal_overflow = (
                    page_width > width
                )
                critical_overflow_elements = sum(
                    1
                    for element in overflow_elements
                    if element["partiallyClipped"]
                )
                offscreen_elements = sum(
                    1
                    for element in overflow_elements
                    if element["fullyOffScreen"]
                )
                header_detected = (
                    header_metrics["detected"]
                )
                header_height = (
                    header_metrics["height"]
                )
                header_viewport_ratio = (
                    header_metrics["ratio"]
                )
                header_position = (
                    header_metrics["position"]
                )
                header_tag = (
                    header_metrics["tag"]
                )
                header_class = (
                    header_metrics["className"]
                )
                oversized_header = (
                    header_detected
                    and
                    header_viewport_ratio >= 0.35
                )
                navigation_detected = (
                    navigation_metrics["detected"]
                )
                navigation_width = (
                    navigation_metrics["width"]
                )
                navigation_viewport_ratio = (
                    navigation_metrics["ratio"]
                )
                navigation_overflow = (
                    navigation_metrics["overflow"]
                )
                navigation_item_count = (
                    navigation_metrics["itemCount"]
                )
                navigation_longest_label = (
                    navigation_metrics["longestLabel"]
                )
                navigation_longest_label_length = (
                    navigation_metrics[
                        "longestLabelLength"
                    ]
                )
                navigation_dense = (
                    navigation_item_count >= 9
                )
                navigation_issue = (
                    navigation_overflow
                )
                content_image_count = (
                    content_image_metrics["total"]
                )
                large_content_image_count = (
                    content_image_metrics["large"]
                )
                small_content_image_count = (
                    content_image_metrics["small"]
                )
                upscaled_image_count = (
                    content_image_metrics["upscaled"]
                )
                content_images = (
                    content_image_metrics["images"]
                )
                background_image_count = (
                    content_image_metrics[
                        "backgroundImageCount"
                    ]
                )
                background_images = (
                    content_image_metrics[
                        "backgroundImages"
                    ]
                )
                substantial_visual_image_count = (
                    large_content_image_count
                    + background_image_count
                )
                room_offerings = (
                    room_metrics["offerings"]
                )
                room_structure = (
                    room_structure_candidates
                )
                (
                    room_offering_count,
                    room_offering_source,
                ) = self._get_room_offering_count(
                    room_structure,
                    room_offerings,
                )
                images_per_room_offering = (
                    substantial_visual_image_count /
                    room_offering_count
                    if room_offering_count > 0
                    else 0.0
                )
                room_presentation_issue = (
                    room_offering_count >= 3
                    and images_per_room_offering < 0.5
                )
                browser.close()
                return VisualScanResult(
                    url=url,
                    successful=True,
                    page_title=page_title,
                    viewport_width=width,
                    viewport_height=height,
                    page_width=page_width,
                    page_height=page_height,
                    horizontal_overflow=(
                        horizontal_overflow
                    ),
                    overflow_elements=overflow_elements,
                    critical_overflow_elements=(
                        critical_overflow_elements
                    ),
                    offscreen_elements=offscreen_elements,
                    header_detected=header_detected,
                    header_height=header_height,
                    header_viewport_ratio=(
                        header_viewport_ratio
                    ),
                    header_position=header_position,
                    header_tag=header_tag,
                    header_class=header_class,
                    oversized_header=oversized_header,
                    branding_images=branding_images,
                    navigation_detected=(
                        navigation_detected
                    ),
                    navigation_width=(
                        navigation_width
                    ),
                    navigation_viewport_ratio=(
                        navigation_viewport_ratio
                    ),
                    navigation_overflow=(
                        navigation_overflow
                    ),
                    navigation_item_count=(
                        navigation_item_count
                    ),
                    navigation_longest_label=(
                        navigation_longest_label
                    ),
                    navigation_longest_label_length=(
                        navigation_longest_label_length
                    ),
                    navigation_dense=navigation_dense,
                    navigation_issue=navigation_issue,
                    content_image_count=(
                        content_image_count
                    ),
                    large_content_image_count=(
                        large_content_image_count
                    ),
                    small_content_image_count=(
                        small_content_image_count
                    ),
                    upscaled_image_count=(
                        upscaled_image_count
                    ),
                    content_images=content_images,
                    background_image_count=(
                        background_image_count
                    ),
                    background_images=(
                        background_images
                    ),
                    substantial_visual_image_count=(
                        substantial_visual_image_count
                    ),
                    room_offering_count=room_offering_count,
                    room_offering_source=(
                        room_offering_source
                    ),
                    room_offerings=room_offerings,
                    images_per_room_offering=(
                        images_per_room_offering
                    ),
                    room_presentation_issue=(
                        room_presentation_issue
                    ),
                    room_structure_candidates=(
                        room_structure
                    ),
                    broken_images=broken_images,
                )
        except Exception as exc:
            return VisualScanResult(
                url=url,
                successful=False,
                page_title=None,
                viewport_width=width,
                viewport_height=height,
                page_width=0,
                page_height=0,
                horizontal_overflow=False,
                overflow_elements=[],
                critical_overflow_elements=0,
                offscreen_elements=0,
                header_detected=False,
                header_height=0,
                header_viewport_ratio=0.0,
                header_position=None,
                header_tag=None,
                header_class=None,
                oversized_header=False,
                branding_images=[],
                navigation_detected=False,
                navigation_width=0,
                navigation_viewport_ratio=0.0,
                navigation_overflow=False,
                navigation_item_count=0,
                navigation_longest_label=None,
                navigation_longest_label_length=0,
                navigation_dense=False,
                navigation_issue=False,
                content_image_count=0,
                large_content_image_count=0,
                small_content_image_count=0,
                upscaled_image_count=0,
                content_images=[],
                background_image_count=0,
                background_images=[],
                substantial_visual_image_count=0,
                room_offering_count=0,
                room_offering_source="none",
                room_offerings=[],
                room_structure_candidates=[],
                images_per_room_offering=0.0,
                room_presentation_issue=False,
                broken_images=0,
                error_message=str(exc),
            )