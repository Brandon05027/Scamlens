from dataclasses import dataclass
from enum import Enum


class RuleSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class ScamRule:
    rule_id: str
    title: str
    category: str
    severity: RuleSeverity
    patterns: tuple[str, ...]
    explanation: str
    score: int


@dataclass(frozen=True)
class RuleMatch:
    rule_id: str
    title: str
    category: str
    severity: RuleSeverity
    evidence: str
    explanation: str
    score: int