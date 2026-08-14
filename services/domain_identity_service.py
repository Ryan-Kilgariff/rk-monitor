from dataclasses import dataclass
@dataclass
class DomainIdentityResult:
    hospitality_detected: bool
    mismatch_detected: bool
    confidence: str
    evidence: list[str]
class DomainIdentityService:
    def analyse(
        self,
        page_title: str | None,
        content_text: str,
    ) -> DomainIdentityResult:
        title = (
            page_title
            or ""
        ).lower()
        content = (
            content_text
            or ""
        ).lower()
        combined = (
            title
            + " "
            + content
        )
        hospitality_terms = (
            "hotel",
            "guest house",
            "guesthouse",
            "bed and breakfast",
            "b&b",
            "rooms",
            "accommodation",
            "stay",
            "booking",
            "book a room",
            "restaurant",
            "inn",
        )
        unrelated_terms = (
            "architect",
            "architectural",
            "consultant",
            "consultancy",
            "construction",
            "engineering",
            "property design",
        )
        hospitality_hits = [
            term
            for term in hospitality_terms
            if term in combined
        ]
        unrelated_hits = [
            term
            for term in unrelated_terms
            if term in combined
        ]
        hospitality_detected = (
            len(hospitality_hits) >= 2
        )
        mismatch_detected = (
            not hospitality_detected
            and len(unrelated_hits) >= 2
        )
        evidence = []
        if page_title:
            evidence.append(
                f"Page title: {page_title}"
            )
        if unrelated_hits:
            evidence.append(
                "Unrelated terms detected: "
                + ", ".join(
                    unrelated_hits[:5]
                )
            )
        if hospitality_hits:
            evidence.append(
                "Hospitality terms detected: "
                + ", ".join(
                    hospitality_hits[:5]
                )
            )
        if mismatch_detected:
            confidence = "HIGH"
        elif hospitality_detected:
            confidence = "HIGH"
        else:
            confidence = "LOW"
        return DomainIdentityResult(
            hospitality_detected=(
                hospitality_detected
            ),
            mismatch_detected=(
                mismatch_detected
            ),
            confidence=confidence,
            evidence=evidence,
        )