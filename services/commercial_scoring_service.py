from dataclasses import dataclass
from services.scoring_service import ScoreResult
from services.site_quality_service import SiteQualityResult
from services.content_quality_service import ContentQualityResult
@dataclass
class CommercialScoreResult:
    technical_score: int
    site_quality_score: int
    content_quality_score: int
    commercial_score: int
class CommercialScoringService:
    def calculate(
        self,
        technical_score: ScoreResult,
        site_quality: SiteQualityResult,
        content_quality: ContentQualityResult,
    ) -> CommercialScoreResult:
        technical = technical_score.overall
        site_quality_score = site_quality.quality_score
        content_quality_score = (
            content_quality.content_depth_score
        )
        commercial_score = round(
            technical * 0.30
            + site_quality_score * 0.40
            + content_quality_score * 0.30
        )
        return CommercialScoreResult(
            technical_score=technical,
            site_quality_score=site_quality_score,
            content_quality_score=content_quality_score,
            commercial_score=commercial_score,
        )