from app.schemas.analysis import (
    AnalysisResponse,
    FindingResponse,
    FindingSeverity,
    IdentitySignalsResponse,
    ScoreBreakdownItem,
    PrivacyAnalysisResponse,
    RedactionCountResponse,
    AIAnalysisResponse,
    AIEvidenceResponse,
)

from app.services.ai.service import analyze_with_ai
from app.services.pii import redact_pii
from app.services.identity import analyze_identity_signals
from app.services.recommendations import build_recommendations
from app.services.rules.engine import run_scam_rules
from app.services.scoring import (
    calculate_risk_score,
    determine_primary_category,
    determine_risk_level,
)


def analyze_text(text: str) -> AnalysisResponse:
    rule_matches = run_scam_rules(text)
    identity_analysis = analyze_identity_signals(text)
    pii_analysis = redact_pii(text)
    ai_status, ai_provider, ai_result = analyze_with_ai(pii_analysis.redacted_text)

    matches = [
        *rule_matches,
        *identity_analysis.matches,
    ]

    score = calculate_risk_score(matches)
    risk_level = determine_risk_level(score)
    primary_category = determine_primary_category(matches)

    findings = [
        FindingResponse(
            rule_id=match.rule_id,
            title=match.title,
            category=match.category,
            severity=FindingSeverity(match.severity.value),
            evidence=match.evidence,
            explanation=match.explanation,
            score_contribution=match.score,
        )
        for match in matches
    ]

    score_breakdown = [
        ScoreBreakdownItem(
            signal=match.title,
            points=match.score,
        )
        for match in matches
    ]

    if matches:
        summary = (
            f"ScamLens found {len(matches)} warning signal(s). "
            f"The message has a {risk_level.value} estimated scam risk."
        )
    else:
        summary = (
            "ScamLens did not detect any currently supported "
            "warning patterns. This does not guarantee that "
            "the message is safe."
        )

    if ai_result is None:
        ai_analysis_response = AIAnalysisResponse(
            status=ai_status,
            provider=ai_provider,
            category=None,
            confidence=None,
            summary=(
                "AI contextual analysis was unavailable. "
                "The deterministic analysis still completed."
            ),
            evidence=[],
            limitations=[
                "No AI result was used for this analysis."
            ],
            privacy_applied=True,
        )
    else:
        ai_analysis_response = AIAnalysisResponse(
            status=ai_status,
            provider=ai_provider,
            category=ai_result.category,
            confidence=ai_result.confidence,
            summary=ai_result.summary,
            evidence=[
                AIEvidenceResponse(
                    text=evidence.text,
                    reason=evidence.reason,
                )
                for evidence in ai_result.evidence
            ],
            limitations=ai_result.limitations,
            privacy_applied=True,
        )

    return AnalysisResponse(
        risk_score=score,
        risk_level=risk_level,
        primary_category=primary_category,
        summary=summary,
        findings=findings,
        score_breakdown=score_breakdown,
        recommended_actions=build_recommendations(matches),
        identity_signals=IdentitySignalsResponse(
            emails=list(identity_analysis.emails),
            urls=list(identity_analysis.urls),
        ),
        privacy_analysis=PrivacyAnalysisResponse(
            redacted_text=pii_analysis.redacted_text,
            total_redactions=pii_analysis.total_redactions,
            redactions=[
                RedactionCountResponse(
                    pii_type=redaction.pii_type,
                    count=redaction.count,
                )
                for redaction in pii_analysis.redactions
            ],
        ),
        ai_analysis=ai_analysis_response,
    )