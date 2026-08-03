from enum import Enum

from pydantic import BaseModel, Field, field_validator


class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class FindingSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TextAnalysisRequest(BaseModel):
    text: str = Field(
        min_length=10,
        max_length=20_000,
        description="Suspicious text submitted for scam analysis.",
    )

    @field_validator("text")
    @classmethod
    def remove_surrounding_spaces(cls, value: str) -> str:
        cleaned_text = value.strip()

        if not cleaned_text:
            raise ValueError("Text cannot be empty.")

        return cleaned_text


class FindingResponse(BaseModel):
    rule_id: str
    title: str
    category: str
    severity: FindingSeverity
    evidence: str
    explanation: str
    score_contribution: int


class ScoreBreakdownItem(BaseModel):
    signal: str
    points: int


class IdentitySignalsResponse(BaseModel):
    emails: list[str]
    urls: list[str]

class RedactionCountResponse(BaseModel):
    pii_type: str
    count: int = Field(ge=1)


class PrivacyAnalysisResponse(BaseModel):
    redacted_text: str
    total_redactions: int = Field(ge=0)
    redactions: list[RedactionCountResponse]

class AnalysisResponse(BaseModel):
    risk_score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    primary_category: str
    summary: str
    findings: list[FindingResponse]
    score_breakdown: list[ScoreBreakdownItem]
    recommended_actions: list[str]
    identity_signals: IdentitySignalsResponse
    privacy_analysis: PrivacyAnalysisResponse
    ai_analysis: AIAnalysisResponse

class AIEvidenceResponse(BaseModel):
    text: str
    reason: str


class AIAnalysisResponse(BaseModel):
    status: str
    provider: str
    category: str | None
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    summary: str
    evidence: list[AIEvidenceResponse]
    limitations: list[str]
    privacy_applied: bool