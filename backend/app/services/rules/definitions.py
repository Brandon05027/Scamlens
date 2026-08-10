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
        ScamRule(
        rule_id="advance-payment-reimbursement",
        title="Advance payment or reimbursement scheme",
        category="fake_job",
        severity=RuleSeverity.HIGH,
        patterns=(
            (
                r"\bdeposit (?:the|a) "
                r"(?:payment|funds|money) we send\b"
            ),
            (
                r"\bdeposit (?:the|a) "
                r"(?:payment|funds|money)\b"
            ),
        ),
        explanation=(
            "Scammers may send supposed funds first and ask the recipient "
            "to deposit or use them before the payment is later reversed."
        ),
        score=20,
    ),

    ScamRule(
        rule_id="account-verification-threat",
        title="Account verification threat",
        category="phishing",
        severity=RuleSeverity.HIGH,
        patterns=(
            (
                r"\bconfirm your details\b"
                r".{0,80}"
                r"\b(?:service|account)\b"
                r".{0,40}"
                r"\b(?:not interrupted|suspended|restricted|closed)\b"
            ),
            (
                r"\bverify your account\b"
                r".{0,80}"
                r"\b(?:suspended|restricted|closed)\b"
            ),
        ),
        explanation=(
            "Phishing messages often pressure recipients to confirm "
            "account information by threatening loss of service or access."
        ),
        score=20,
    ),

    ScamRule(
        rule_id="overpayment-forwarding",
        title="Overpayment forwarding request",
        category="payment_scam",
        severity=RuleSeverity.HIGH,
        patterns=(
            (
                r"\b(?:send|pay) extra money\b"
                r".{0,100}"
                r"\bforward the difference\b"
            ),
            (
                r"\boverpay\b"
                r".{0,100}"
                r"\b(?:send|forward|return) "
                r"(?:the )?(?:difference|remaining money)\b"
            ),
        ),
        explanation=(
            "Overpayment scams send more money than expected and ask the "
            "recipient to forward part of it elsewhere before the original "
            "payment is reversed."
        ),
        score=25,
    ),

    ScamRule(
        rule_id="job-supplies-purchase",
        title="Job supplies purchase request",
        category="fake_job",
        severity=RuleSeverity.HIGH,
        patterns=(
            (
                r"\bselected without an interview\b"
                r".{0,120}"
                r"\bpurchase (?:the )?(?:required )?"
                r"(?:supplies|equipment)\b"
            ),
            (
                r"\bpurchase (?:the )?(?:required )?"
                r"(?:supplies|equipment)\b"
                r".{0,100}"
                r"\breimbursement\b"
            ),
        ),
        explanation=(
            "Fake-job scams may ask applicants to purchase equipment or "
            "supplies with a promise that the cost will later be reimbursed."
        ),
        score=20,
    ),
)