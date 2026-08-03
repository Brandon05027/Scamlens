from pydantic import BaseModel, Field


class AIEvidence(BaseModel):
    text: str
    reason: str


class AIContextResult(BaseModel):
    category: str
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str
    evidence: list[AIEvidence]
    limitations: list[str]