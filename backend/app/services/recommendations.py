from app.services.rules.models import RuleMatch


DEFAULT_ACTIONS = [
    "Pause before replying, clicking a link, or sending money.",
    "Verify the sender using contact information from an official website.",
    "Do not open unexpected links or attachments.",
]


def build_recommendations(matches: list[RuleMatch]) -> list[str]:
    actions = list(DEFAULT_ACTIONS)
    rule_ids = {match.rule_id for match in matches}

    if "unexpected-check" in rule_ids:
        actions.append(
            "Do not deposit the check or use its funds to purchase equipment."
        )

    if "bank-information-request" in rule_ids:
        actions.append(
            "Do not send account numbers, routing numbers, passwords, or login codes."
        )

    if "gift-card-payment" in rule_ids:
        actions.append(
            "Do not purchase or send gift-card numbers to the requester."
        )

    if "urgency-pressure" in rule_ids:
        actions.append(
            "Slow down and verify the request before taking any immediate action."
        )

    if "ip-address-url" in rule_ids:
        actions.append(
            "Do not open the IP-address link until its destination "
            "and sender have been independently verified."
        )

    if "shortened-url" in rule_ids:
        actions.append(
            "Expand the shortened link with a trusted link-preview "
            "service before deciding whether to open it."
        )

    if "punycode-domain" in rule_ids:
        actions.append(
            "Compare the encoded domain with the organization's official "
            "website before entering any information."
        )

    if "excessive-subdomains" in rule_ids:
        actions.append(
            "Read the domain from right to left and verify the actual "
            "registered website rather than trusting familiar words "
            "at the beginning of the link."
        )
        
    return list(dict.fromkeys(actions))