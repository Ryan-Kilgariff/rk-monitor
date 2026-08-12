from dataclasses import dataclass
from services.issue_service import Issue
@dataclass
class ScoreResult:
    technical_health: int
    booking_journey: int
    mobile_experience: int
    room_presentation: int
    guest_information: int
    analytics: int
    overall: int
    high_issues: int
    medium_issues: int
    low_issues: int
class ScoringService:
    CATEGORY_MAP = {
        "Technical Health": "technical_health",
        "Booking Journey": "booking_journey",
        "Mobile Experience": "mobile_experience",
        "Room Presentation": "room_presentation",
        "Guest Information": "guest_information",
        "Analytics": "analytics",
    }
    PENALTIES = {
        "HIGH": 30,
        "MEDIUM": 15,
        "LOW": 5,
    }
    def calculate(
        self,
        issues: list[Issue],
    ) -> ScoreResult:
        scores = {
            "technical_health": 100,
            "booking_journey": 100,
            "mobile_experience": 100,
            "room_presentation": 100,
            "guest_information": 100,
            "analytics": 100,
        }
        high_issues = 0
        medium_issues = 0
        low_issues = 0
        for issue in issues:
            penalty = self.PENALTIES.get(
                issue.severity,
                0,
            )
            if issue.severity == "HIGH":
                high_issues += 1
            elif issue.severity == "MEDIUM":
                medium_issues += 1
            elif issue.severity == "LOW":
                low_issues += 1
            score_key = self.CATEGORY_MAP.get(
                issue.category
            )
            if score_key:
                scores[score_key] = max(
                    0,
                    scores[score_key] - penalty,
                )
        overall = round(
            sum(scores.values())
            / len(scores)
        )
        return ScoreResult(
            technical_health=scores[
                "technical_health"
            ],
            booking_journey=scores[
                "booking_journey"
            ],
            mobile_experience=scores[
                "mobile_experience"
            ],
            room_presentation=scores[
                "room_presentation"
            ],
            guest_information=scores[
                "guest_information"
            ],
            analytics=scores[
                "analytics"
            ],
            overall=overall,
            high_issues=high_issues,
            medium_issues=medium_issues,
            low_issues=low_issues,
        )