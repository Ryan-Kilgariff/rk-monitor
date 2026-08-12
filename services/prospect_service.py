from dataclasses import dataclass
from services.issue_service import Issue
from services.scoring_service import ScoreResult
@dataclass
class ProspectResult:
    strength: str
    recommended_service: str
    reason: str
class ProspectService:
    def qualify(
        self,
        score: ScoreResult,
        issues: list[Issue],
    ) -> ProspectResult:
        high_count = sum(
            1
            for issue in issues
            if issue.severity == "HIGH"
        )
        medium_count = sum(
            1
            for issue in issues
            if issue.severity == "MEDIUM"
        )
        booking_issues = any(
            issue.category == "Booking Journey"
            for issue in issues
        )
        room_issues = any(
            issue.category == "Room Presentation"
            for issue in issues
        )
        technical_issues = any(
            issue.category == "Technical Health"
            for issue in issues
        )
        if (
            score.overall <= 60
            or high_count >= 2
        ):
            return ProspectResult(
                strength="STRONG",
                recommended_service=(
                    "Website Redesign"
                ),
                reason=(
                    "Multiple significant issues "
                    "or a low overall website score."
                ),
            )
        if booking_issues:
            return ProspectResult(
                strength="STRONG",
                recommended_service=(
                    "Booking Journey Improvement"
                ),
                reason=(
                    "Commercial booking issues "
                    "were detected."
                ),
            )
        if (
            score.overall <= 75
            or high_count == 1
            or medium_count >= 2
        ):
            return ProspectResult(
                strength="GOOD",
                recommended_service=(
                    "Website Improvement"
                ),
                reason=(
                    "Several meaningful improvement "
                    "opportunities were detected."
                ),
            )
        if room_issues or technical_issues:
            return ProspectResult(
                strength="POSSIBLE",
                recommended_service=(
                    "Targeted Website Improvements"
                ),
                reason=(
                    "Some commercially relevant "
                    "issues were detected."
                ),
            )
        return ProspectResult(
            strength="WEAK",
            recommended_service=(
                "RK Monitor"
            ),
            reason=(
                "No major redesign-level problems "
                "were detected by the current rules."
            ),
        )