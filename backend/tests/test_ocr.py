import pytest

from app.services.ocr import extract_text_from_image


class FakeOCRProvider:
    name = "fake-ocr"

    def extract_text(
        self,
        image_bytes: bytes,
    ) -> str:
        assert image_bytes == b"fake-image"

        return (
            "We will send you a check. "
            "Reply immediately with your banking information."
        )


class EmptyOCRProvider:
    name = "empty-ocr"

    def extract_text(
        self,
        image_bytes: bytes,
    ) -> str:
        return ""


def test_injected_ocr_provider_extracts_text() -> None:
    provider_name, extracted_text = extract_text_from_image(
        b"fake-image",
        provider=FakeOCRProvider(),
    )

    assert provider_name == "fake-ocr"
    assert "send you a check" in extracted_text


def test_ocr_provider_can_return_empty_text() -> None:
    provider_name, extracted_text = extract_text_from_image(
        b"fake-image",
        provider=EmptyOCRProvider(),
    )

    assert provider_name == "empty-ocr"
    assert extracted_text == ""


def test_fake_ocr_text_can_enter_analysis_pipeline() -> None:
    from app.services.analysis import analyze_text

    _, extracted_text = extract_text_from_image(
        b"fake-image",
        provider=FakeOCRProvider(),
    )

    result = analyze_text(extracted_text)

    assert result.risk_score >= 50
    assert result.risk_level.value in {
        "high",
        "critical",
    }