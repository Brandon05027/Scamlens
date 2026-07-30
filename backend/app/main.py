from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.analysis import TextAnalysisRequest
from app.schemas.analysis import AnalysisResponse, TextAnalysisRequest
from app.services.analysis import analyze_text

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


@app.post(
    "/api/v1/analyses/text",
    response_model=AnalysisResponse,
)
def create_text_analysis(
    request: TextAnalysisRequest,
) -> AnalysisResponse:
    return analyze_text(request.text)