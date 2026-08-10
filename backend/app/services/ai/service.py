import os
import logging
logger = logging.getLogger(__name__)

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


#The logger is safer allow us to get enough information to debug without receiving sus info from the users
def analyze_with_ai(
    redacted_text: str,
    provider: AIProvider | None = None,
) -> tuple[str, str, AIContextResult | None]:
    selected_provider = provider

    try:
        selected_provider = (
            selected_provider
            or build_ai_provider()
        )

        result = selected_provider.analyze(
            redacted_text
        )

        return (
            "completed",
            selected_provider.name,
            result,
        )

    except Exception:
        provider_name = getattr(
            selected_provider,
            "name",
            "unknown",
        )

        logger.exception(
            "AI contextual analysis failed for provider %s",
            provider_name,
        )

        return (
            "unavailable",
            "none",
            None,
        ) 