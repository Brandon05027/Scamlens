import re
from dataclasses import dataclass


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\+?1[\s.-]?)?"
    r"(?:\(?\d{3}\)?[\s.-]?)"
    r"\d{3}[\s.-]?\d{4}"
    r"(?!\d)"
)

SSN_PATTERN = re.compile(
    r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"
)

ACCOUNT_NUMBER_PATTERN = re.compile(
    r"\b(?:account|acct)"
    r"\s*(?:number|no\.?|#)?"
    r"\s*(?:is|:|-)?"
    r"\s*\d{6,17}\b",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class RedactionCount:
    pii_type: str
    count: int


@dataclass(frozen=True)
class PiiRedactionResult:
    redacted_text: str
    redactions: tuple[RedactionCount, ...]
    total_redactions: int


def redact_pii(text: str) -> PiiRedactionResult:
    redacted_text = text
    redaction_counts: list[RedactionCount] = []

    redaction_rules = (
        (
            "email_address",
            EMAIL_PATTERN,
            "[EMAIL_ADDRESS]",
        ),
        (
            "phone_number",
            PHONE_PATTERN,
            "[PHONE_NUMBER]",
        ),
        (
            "social_security_number",
            SSN_PATTERN,
            "[SSN]",
        ),
        (
            "account_number",
            ACCOUNT_NUMBER_PATTERN,
            "[ACCOUNT_NUMBER]",
        ),
    )

    for pii_type, pattern, replacement in redaction_rules:
        redacted_text, count = pattern.subn(
            replacement,
            redacted_text,
        )

        if count > 0:
            redaction_counts.append(
                RedactionCount(
                    pii_type=pii_type,
                    count=count,
                )
            )

    total_redactions = sum(
        redaction.count
        for redaction in redaction_counts
    )

    return PiiRedactionResult(
        redacted_text=redacted_text,
        redactions=tuple(redaction_counts),
        total_redactions=total_redactions,
    )