from pydantic import BaseModel, Field, field_validator


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
