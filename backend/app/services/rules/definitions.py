from app.services.rules.models import ScamRule, RuleSeverity


SCAM_RULES: tuple[ScamRule, ...] = (
    ScamRule(
        rule_id="unexpected-check",
        title="Unexpected check",
        category="fake_job",
        severity=RuleSeverity.HIGH,
        patterns=(
            r"\bwe will send you a check\b",
            r"\bwe'll send you a check\b",
            r"\bdeposit (?:the|this|a) check\b",
            r"\bcashier'?s check\b",
        ),
        explanation=(
            "Unexpected checks are commonly used in fake-job and "
            "overpayment scams. The check may later be reversed."
        ),
        score=25,
    ),
    ScamRule(
        rule_id="gift-card-payment",
        title="Gift-card payment request",
        category="payment_scam",
        severity=RuleSeverity.HIGH,
        patterns=(
            r"\bgift cards?\b",
            r"\bgoogle play cards?\b",
            r"\bapple gift cards?\b",
            r"\bsteam cards?\b",
        ),
        explanation=(
            "Legitimate companies and government agencies rarely require "
            "payment through gift cards."
        ),
        score=25,
    ),
    ScamRule(
        rule_id="bank-information-request",
        title="Banking-information request",
        category="credential_theft",
        severity=RuleSeverity.HIGH,
        patterns=(
            r"\bbank(?:ing)? information\b",
            r"\baccount number\b",
            r"\brouting number\b",
            r"\bonline banking login\b",
        ),
        explanation=(
            "Requests for banking details may expose the recipient to "
            "financial theft or account takeover."
        ),
        score=25,
    ),
    ScamRule(
        rule_id="urgency-pressure",
        title="Urgency or pressure",
        category="social_engineering",
        severity=RuleSeverity.MEDIUM,
        patterns=(
            r"\breply immediately\b",
            r"\bact now\b",
            r"\burgent(?:ly)?\b",
            r"\bfinal warning\b",
            r"\bwithin \d+ (?:minutes?|hours?)\b",
        ),
        explanation=(
            "Scammers often create urgency so the recipient acts before "
            "checking whether the request is legitimate."
        ),
        score=10,
    ),
)