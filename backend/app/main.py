from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.analysis import TextAnalysisRequest
from app.services.rules.engine import run_scam_rules

app = FastAPI(
    title="ScamLens API",
    description="API for explainable scam-content analysis.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "scamlens-api",
        "version": "0.1.0",
    }


@app.post("/api/v1/analyses/text")
def create_text_analysis(
    request: TextAnalysisRequest,
) -> dict[str, object]:
    matches = run_scam_rules(request.text)
    total_score = sum(match.score for match in matches)

    return {
        "message": "Text analyzed successfully.",
        "text": request.text,
        "character_count": len(request.text),
        "risk_score": min(total_score, 100),
        "findings": [
            {
                "rule_id": match.rule_id,
                "title": match.title,
                "category": match.category,
                "severity": match.severity.value,
                "evidence": match.evidence,
                "explanation": match.explanation,
                "score": match.score,
            }
            for match in matches
        ],
    }