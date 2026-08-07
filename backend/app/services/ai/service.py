import os

from app.services.ai.models import AIContextResult
from app.services.ai.providers import (
    AIProvider,
    MockAIProvider,
    OpenAIProvider,
)


def build_ai_provider() -> AIProvider:
    provider_name = os.getenv(
        "SCAMLENS_AI_PROVIDER",
        "mock",
    ).lower()

    if provider_name == "mock":
        return MockAIProvider()

    if provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is required when "
                "SCAMLENS_AI_PROVIDER=openai."
            )

        if not model:
            raise RuntimeError(
                "OPENAI_MODEL is required when "
                "SCAMLENS_AI_PROVIDER=openai."
            )

        return OpenAIProvider(
            api_key=api_key,
            model=model,
        )

    raise RuntimeError(
        f"Unsupported AI provider: {provider_name}"
    )


def analyze_with_ai(
    redacted_text: str,
    provider: AIProvider | None = None,
) -> tuple[str, str, AIContextResult | None]:
    try:
        selected_provider = provider or build_ai_provider() #if a test supplies the provider then selected_provider = provider will be used. If not, it will use the normal provider from the env.

        result = selected_provider.analyze(
            redacted_text
        )

        return (
            "completed",
            selected_provider.name,
            result,
        )

    except Exception:
        return (
            "unavailable",
            "none",
            None,
        )