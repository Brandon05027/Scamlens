from collections import Counter

from app.schemas.analysis import RiskLevel
from app.services.rules.models import RuleMatch


def calculate_risk_score(matches: list[RuleMatch]) -> int:
    raw_score = sum(match.score for match in matches)

    return min(raw_score, 100)


def determine_risk_level(score: int) -> RiskLevel:
    if score >= 75:
        return RiskLevel.CRITICAL

    if score >= 50:
        return RiskLevel.HIGH

    if score >= 25:
        return RiskLevel.MODERATE

    return RiskLevel.LOW


def determine_primary_category(matches: list[RuleMatch]) -> str:
    if not matches:
        return "none_detected"

    category_scores: Counter[str] = Counter()

    for match in matches:
        category_scores[match.category] += match.score

    return category_scores.most_common(1)[0][0]