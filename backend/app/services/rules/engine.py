import re

from app.services.rules.definitions import SCAM_RULES
from app.services.rules.models import RuleMatch


SAFE_BANKING_CONTEXTS = (
    "never send my banking information",
    "never send your banking information",
    "do not send my banking information",
    "do not send your banking information",
    "don't send my banking information",
    "don't send your banking information",
)


def should_skip_match(
    rule_id: str,
    text: str,
) -> bool:
    lowered_text = text.lower()

    if rule_id == "bank-information-request":
        return any(
            safe_context in lowered_text
            for safe_context in SAFE_BANKING_CONTEXTS
        )

    return False

def run_scam_rules(text: str) -> list[RuleMatch]:
    matches: list[RuleMatch] = []

    for rule in SCAM_RULES:
        for pattern in rule.patterns:
            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            if not match:
                continue

            if should_skip_match(
                rule.rule_id,
                text,
            ):
                continue

            matches.append(
                RuleMatch(
                    rule_id=rule.rule_id,
                    title=rule.title,
                    category=rule.category,
                    severity=rule.severity,
                    evidence=match.group(0),
                    explanation=rule.explanation,
                    score=rule.score,
                )
            )

            break

    return matches
