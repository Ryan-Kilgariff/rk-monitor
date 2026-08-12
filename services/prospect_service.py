from dataclasses import dataclass
from services.issue_service import Issue
from services.scoring_service import ScoreResult
from services.commercial_scoring_service import (
    CommercialScoreResult,
)
@dataclass
class ProspectResult:
    strength: str
    recommended_service: str
    reason: str
class ProspectService:
    def qualify(
        self,
        score: ScoreResult,
        commercial_score: CommercialScoreResult,
        issues: list[Issue],
    ) -> ProspectResult:
        commercial = (
                commercial_score.commercial_score
            )
        critical_technical_issue = any(
            issue.title in (
                "Website domain could not be resolved",
                "Website connection failed",
                "Homepage returned an error",
            )
            for issue in issues
        )
        if critical_technical_issue:
            return ProspectResult(
                strength="STRONG",
                recommended_service=(
                    "Website Recovery / Redesign"
                ),
                reason=(
                    "A critical website availability "
                    "problem was detected."
                ),
            )
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
        if (
            commercial <= 55
            or high_count >= 2
        ):
            return ProspectResult(
                strength="STRONG",
                recommended_service=(
                    "Website Redesign"
                ),
                reason=(
                    "The website shows significant "
                    "commercial or structural weaknesses."
                ),
            )
        if commercial <= 70:
            return ProspectResult(
                strength="GOOD",
                recommended_service=(
                    "Website Improvement / Redesign"
                ),
                reason=(
                    "Meaningful hospitality structure "
                    "or content weaknesses were detected."
                ),
            )
        if (
            commercial <= 82
            or high_count == 1
            or medium_count >= 2
        ):
            return ProspectResult(
                strength="POSSIBLE",
                recommended_service=(
                    "Targeted Website Improvements"
                ),
                reason=(
                    "Some commercially relevant "
                    "improvement opportunities were detected."
                ),
            )
        return ProspectResult(
            strength="WEAK",
            recommended_service="RK Monitor",
            reason=(
                "No major redesign-level weaknesses "
                "were detected by the current rules."
            ),
        )