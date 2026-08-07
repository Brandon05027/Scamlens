from app.services.ai.models import(
    AIContextResult,
    AIEvidence,
)
from app.services.analysis import analyze_text
class RecordingAIProvider: #controlled test provider
    name = "recording-test"

    def __init__(self) -> None:
        self.received_text: str | None = None

    def analyze(
        self,
        redacted_text: str,
    ) -> AIContextResult:
        self.received_text = redacted_text #stored the value 

        return AIContextResult(
            category="test_category",
            confidence=0.75,
            summary="The test provider completed successfully.",
            evidence=[
                AIEvidence(
                    text="[EMAIL_ADDRESS]",
                    reason=(
                        "The provider received a privacy placeholder "
                        "instead of the original email address."
                    ),
                )
            ],
            limitations=[
                "This result was produced by a test provider."
            ],
        )


class FailingAIProvider: #simulate the outstage
    name = "failing-test"

    def analyze(
        self,
        redacted_text: str,
    ) -> AIContextResult:
        raise TimeoutError("Simulated AI timeout")


def test_ai_provider_receives_redacted_text() -> None:
    provider = RecordingAIProvider()

    result = analyze_text(
        (
            "Contact brandon@example.com. We will send "
            "you a check to purchase equipment."
        ),
        ai_provider=provider,
    )

    assert provider.received_text is not None
    assert "[EMAIL_ADDRESS]" in provider.received_text
    assert "brandon@example.com" not in provider.received_text #it proves here which also inspect the interaction

    assert result.ai_analysis.status == "completed"
    assert result.ai_analysis.provider == "recording-test"
    assert result.ai_analysis.privacy_applied is True


def test_ai_failure_preserves_deterministic_analysis() -> None:
    provider = FailingAIProvider()

    result = analyze_text(
        (
            "We will send you a check. Reply immediately "
            "with your banking information."
        ),
        ai_provider=provider,
    )

    assert result.ai_analysis.status == "unavailable"
    assert result.ai_analysis.provider == "none"
    assert result.ai_analysis.category is None
    assert result.ai_analysis.confidence is None

    assert result.risk_score >= 50 #even if AI breaks down it will still run 
    assert result.risk_level.value in {"high", "critical"}
    assert len(result.findings) >= 2