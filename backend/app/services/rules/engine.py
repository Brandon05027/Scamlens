import re

from app.services.rules.definitions import SCAM_RULES
from app.services.rules.models import RuleMatch


def run_scam_rules(text: str) -> list[RuleMatch]:
    matches: list[RuleMatch] = []

    for rule in SCAM_RULES:
        for pattern in rule.patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)

            if match:
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