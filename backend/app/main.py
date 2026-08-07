from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.analysis import TextAnalysisRequest
from app.schemas.analysis import AnalysisResponse, TextAnalysisRequest
from app.schemas.analysis import OCRAnalysisResponse,ScreenshotAnalysisResponse
from app.services.analysis import analyze_text
from app.services.ocr import extract_text_from_image


from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile,
)


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

ALLOWED_IMAGE_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
}

MAX_SCREENSHOT_BYTES = 5 * 1024 * 1024 #5MB
@app.post(
    "/api/v1/analyses/screenshot",
    response_model=ScreenshotAnalysisResponse,
)
async def create_screenshot_analysis(
    file: UploadFile = File(...),
) -> ScreenshotAnalysisResponse:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=415,
            detail=(
                "Unsupported image type. "
                "Use PNG, JPEG, or WebP."
            ),
        )

    image_bytes = await file.read()

    if len(image_bytes) > MAX_SCREENSHOT_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Screenshot must be 5 MB or smaller.",
        )

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded screenshot is empty.",
        )

    try:
        ocr_provider, extracted_text = (
            extract_text_from_image(image_bytes)
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    if len(extracted_text.strip()) < 10:
        raise HTTPException(
            status_code=422,
            detail=(
                "OCR could not extract enough readable text "
                "from the screenshot."
            ),
        )

    analysis = analyze_text(extracted_text)

    return ScreenshotAnalysisResponse(
        ocr=OCRAnalysisResponse(
            provider=ocr_provider,
            extracted_text=extracted_text,
        ),
        analysis=analysis,
    )