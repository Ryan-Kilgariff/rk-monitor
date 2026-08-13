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
    primary_problem: str
    outreach_angle: str
    supporting_reasons: list[str]
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
        high_issues = [
            issue
            for issue in issues
            if issue.severity == "HIGH"
        ]
        medium_issues = [
            issue
            for issue in issues
            if issue.severity == "MEDIUM"
        ]
        low_issues = [
            issue
            for issue in issues
            if issue.severity == "LOW"
        ]
        high_families = {
            self._get_issue_family(issue)
            for issue in high_issues
        }
        high_family_count = len(
            high_families
        )
        medium_count = len(
            medium_issues
        )
        critical_technical_issue = any(
            issue.title in (
                "Website domain could not be resolved",
                "Website connection failed",
                "Homepage returned an error",
                "Secure website connection failed",
            )
            for issue in issues
        )
        primary_problem = self._get_primary_problem(
            issues
        )
        outreach_angle = self._get_outreach_angle(
            issues,
            commercial_score,
        )
        supporting_reasons = (
            self._get_supporting_reasons(
                issues,
                commercial_score,
            )
        )
        if critical_technical_issue:
            critical_reasons = []
            for issue in issues:
                if issue.severity in (
                    "HIGH",
                    "MEDIUM",
                ):
                    critical_reasons.append(
                        issue.title
                    )
            return ProspectResult(
                strength="STRONG",
                recommended_service=(
                    "Website Recovery / Redesign"
                ),
                reason=(
                    "A critical website availability "
                    "problem was detected."
                ),
                primary_problem=primary_problem,
                outreach_angle=outreach_angle,
                supporting_reasons=critical_reasons[:3],
            )
        if (
            commercial <= 55
            or high_family_count >= 2
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
                primary_problem=primary_problem,
                outreach_angle=outreach_angle,
                supporting_reasons=supporting_reasons,
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
                primary_problem=primary_problem,
                outreach_angle=outreach_angle,
                supporting_reasons=supporting_reasons,
            )
        if (
            commercial <= 82
            or high_family_count == 1
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
                primary_problem=primary_problem,
                outreach_angle=outreach_angle,
                supporting_reasons=supporting_reasons,
            )
        return ProspectResult(
            strength="WEAK",
            recommended_service="RK Monitor",
            reason=(
                "No major redesign-level weaknesses "
                "were detected by the current rules."
            ),
            primary_problem=primary_problem,
            outreach_angle=outreach_angle,
            supporting_reasons=supporting_reasons,
        )
    def _get_primary_problem(
        self,
        issues: list[Issue],
    ) -> str:
        significant_issues = [
            issue
            for issue in issues
            if issue.severity in ("HIGH", "MEDIUM")
        ]
        if significant_issues:
            severity_order = {
                "HIGH": 0,
                "MEDIUM": 1,
            }
            ranked = sorted(
                significant_issues,
                key=lambda issue: severity_order.get(
                    issue.severity,
                    99,
                ),
            )
            return ranked[0].title
        return "No major automated issue detected"
    def _get_outreach_angle(
        self,
        issues: list[Issue],
        commercial_score: CommercialScoreResult,
    ) -> str:
        significant_categories = {
            issue.category
            for issue in issues
            if issue.severity in ("HIGH", "MEDIUM")
        }
        if "Booking Journey" in significant_categories:
            return "Booking journey"
        if "Room Presentation" in significant_categories:
            return "Room presentation"
        if "Technical Health" in significant_categories:
            return "Website reliability"
        if (
            commercial_score.site_quality_score
            <= 60
        ):
            return (
                "Website structure and "
                "guest journey"
            )
        if (
            commercial_score.content_quality_score
            <= 60
        ):
            return (
                "Website content and "
                "information quality"
            )
        if "Guest Information" in significant_categories:
            return "Guest information"
        return "General website review"
    def _get_supporting_reasons(
        self,
        issues: list[Issue],
        commercial_score: CommercialScoreResult,
    ) -> list[str]:
        reasons = []
        seen_families = set()
        for issue in issues:
            if issue.severity not in (
                "HIGH",
                "MEDIUM",
            ):
                continue
            family = self._get_issue_family(
                issue
            )
            if family in seen_families:
                continue
            seen_families.add(
                family
            )
            reasons.append(
                issue.title
            )
        if (
            commercial_score.site_quality_score
            <= 60
        ):
            reasons.append(
                "Limited hospitality website structure"
            )
        if (
            commercial_score.content_quality_score
            <= 60
        ):
            reasons.append(
                "Weak or repetitive website content"
            )
        unique_reasons = []
        for reason in reasons:
            if reason not in unique_reasons:
                unique_reasons.append(
                    reason
                )
        return unique_reasons[:3]
    def _get_issue_family(
        self,
        issue: Issue,
    ) -> str:
        title = issue.title.lower()
        if issue.category == "Booking Journey":
            return "booking_journey"
        if issue.category == "Technical Health":
            if (
                "domain could not be resolved" in title
                or "connection failed" in title
                or "homepage returned an error" in title
            ):
                return "website_availability"
            if "ssl" in title:
                return "ssl"
            if "broken" in title:
                return "broken_links"
            if "slow" in title:
                return "performance"
            return "technical_health"
        if issue.category == "Room Presentation":
            return "room_presentation"
        if issue.category == "Guest Information":
            return "guest_information"
        if issue.category == "Mobile Experience":
            return "mobile_experience"
        if issue.category == "Analytics":
            return "analytics"
        return issue.category.lower().replace(
            " ",
            "_",
        )