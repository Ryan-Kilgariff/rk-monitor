from dataclasses import dataclass
from services.crawl_service import CrawledPage
@dataclass
class DuplicatePagePair:
    first_url: str
    second_url: str
    overlap: float
@dataclass
class ContentQualityResult:
    pages_checked: int
    thin_pages: list[str]
    duplicate_pairs: list[DuplicatePagePair]
    average_word_count: int
    content_depth_score: int
class ContentQualityService:
    def __init__(
        self,
        thin_page_threshold: int = 120,
        duplicate_threshold: float = 0.60,
    ):
        self.thin_page_threshold = (
            thin_page_threshold
        )
        self.duplicate_threshold = (
            duplicate_threshold
        )
    def analyse(
        self,
        pages: list[CrawledPage],
    ) -> ContentQualityResult:
        usable_pages = [
            page
            for page in pages
            if (
                page.successful
                and page.content_text
            )
        ]
        thin_pages = [
            page.url
            for page in usable_pages
            if (
                page.word_count
                < self.thin_page_threshold
            )
        ]
        duplicate_pairs = (
            self._find_duplicates(
                usable_pages
            )
        )
        if usable_pages:
            average_word_count = round(
                sum(
                    page.word_count
                    for page in usable_pages
                )
                / len(usable_pages)
            )
        else:
            average_word_count = 0
        score = 100
        if len(thin_pages) >= 3:
            score -= 25
        elif len(thin_pages) == 2:
            score -= 15
        elif len(thin_pages) == 1:
            score -= 5
        if len(duplicate_pairs) >= 2:
            score -= 30
        elif len(duplicate_pairs) == 1:
            score -= 15
        if (
            usable_pages
            and average_word_count < 100
        ):
            score -= 15
        return ContentQualityResult(
            pages_checked=len(
                usable_pages
            ),
            thin_pages=thin_pages,
            duplicate_pairs=duplicate_pairs,
            average_word_count=(
                average_word_count
            ),
            content_depth_score=max(
                0,
                score,
            ),
        )
    def _find_duplicates(
        self,
        pages: list[CrawledPage],
    ) -> list[DuplicatePagePair]:
        duplicates = []
        for index, first in enumerate(pages):
            for second in pages[index + 1:]:
                if (
                    first.word_count < 50
                    or second.word_count < 50
                ):
                    continue
                similarity = (
                    self._content_similarity(
                        first.content_text,
                        second.content_text,
                    )
                )
                threshold = self.duplicate_threshold
                if (
                    first.page_type == "rooms"
                    and second.page_type == "rooms"
                ):
                    threshold = 0.90
                if similarity >= threshold:
                    duplicates.append(
                        DuplicatePagePair(
                            first_url=first.url,
                            second_url=second.url,
                            overlap=similarity,
                        )
                    )
        return duplicates
    def _content_similarity(
        self,
        first_text: str,
        second_text: str,
    ) -> float:
        first_words = self._normalise_words(
            first_text
        )
        second_words = self._normalise_words(
            second_text
        )
        if not first_words or not second_words:
            return 0.0
        first_set = set(first_words)
        second_set = set(second_words)
        shared_words = (
            first_set & second_set
        )
        smaller_page_size = min(
            len(first_set),
            len(second_set),
        )
        if smaller_page_size == 0:
            return 0.0
        return (
            len(shared_words)
            / smaller_page_size
        )
    def _normalise_words(
        self,
        text: str,
    ) -> list[str]:
        stop_words = {
            "the",
            "and",
            "a",
            "an",
            "of",
            "to",
            "in",
            "is",
            "for",
            "with",
            "on",
            "at",
            "our",
            "your",
            "we",
            "you",
            "it",
            "as",
            "are",
            "be",
            "from",
            "this",
            "that",
        }
        cleaned = (
            text.lower()
            .replace(",", " ")
            .replace(".", " ")
            .replace(":", " ")
            .replace(";", " ")
            .replace("!", " ")
            .replace("?", " ")
            .replace("(", " ")
            .replace(")", " ")
        )
        return [
            word
            for word in cleaned.split()
            if (
                len(word) > 2
                and word not in stop_words
            )
        ]