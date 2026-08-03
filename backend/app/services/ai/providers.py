import json
from typing import Protocol

from openai import OpenAI

from app.services.ai.models import (
    AIContextResult,
    AIEvidence,
)


class AIProvider(Protocol):
    name: str

    def analyze(self, redacted_text: str) -> AIContextResult:
        """Analyze privacy-redacted text."""


class MockAIProvider:
    name = "mock"

    def analyze(self, redacted_text: str) -> AIContextResult:
        lowered_text = redacted_text.lower()

        if "check" in lowered_text and "equipment" in lowered_text:
            return AIContextResult(
                category="fake_job",
                confidence=0.86,
                summary=(
                    "The message resembles a fake-job payment scam "
                    "involving an unexpected check and equipment purchase."
                ),
                evidence=[
                    AIEvidence(
                        text="check and equipment purchase",
                        reason=(
                            "Fake employers may send fraudulent checks "
                            "and direct applicants to purchase equipment."
                        ),
                    )
                ],
                limitations=[
                    "This is a development mock, not a real model result."
                ],
            )

        if "gift card" in lowered_text:
            return AIContextResult(
                category="payment_scam",
                confidence=0.82,
                summary=(
                    "The message contains a gift-card payment pattern "
                    "commonly associated with scams."
                ),
                evidence=[
                    AIEvidence(
                        text="gift card",
                        reason=(
                            "Gift cards are difficult to reverse and are "
                            "frequently requested by scammers."
                        ),
                    )
                ],
                limitations=[
                    "This is a development mock, not a real model result."
                ],
            )

        return AIContextResult(
            category="uncertain",
            confidence=0.30,
            summary=(
                "The development mock did not recognize a strong "
                "contextual scam pattern."
            ),
            evidence=[],
            limitations=[
                "This is a development mock, not a real model result.",
                "A low confidence result does not prove the message is safe.",
            ],
        )


class OpenAIProvider:
    name = "openai"

    def __init__(
        self,
        api_key: str,
        model: str,
    ) -> None:
        self.model = model
        self.client = OpenAI(
            api_key=api_key,
            timeout=15.0,
            max_retries=1,
        )

    def analyze(self, redacted_text: str) -> AIContextResult:
        response = self.client.responses.create(
            model=self.model,
            store=False,
            instructions=(
                "You are a security-analysis component inside ScamLens. "
                "Analyze the supplied privacy-redacted message for scam "
                "context. Do not invent facts. Evidence must refer only "
                "to wording present in the supplied message. A low-risk "
                "result is not proof that the message is safe."
            ),
            input=redacted_text,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "scam_context_analysis",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "category": {
                                "type": "string"
                            },
                            "confidence": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1
                            },
                            "summary": {
                                "type": "string"
                            },
                            "evidence": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "properties": {
                                        "text": {
                                            "type": "string"
                                        },
                                        "reason": {
                                            "type": "string"
                                        },
                                    },
                                    "required": [
                                        "text",
                                        "reason",
                                    ],
                                },
                            },
                            "limitations": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                            },
                        },
                        "required": [
                            "category",
                            "confidence",
                            "summary",
                            "evidence",
                            "limitations",
                        ],
                    },
                }
            },
        )

        response_data = json.loads(response.output_text)

        return AIContextResult.model_validate(response_data)