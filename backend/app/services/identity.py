import ipaddress
import re
from dataclasses import dataclass
from urllib.parse import urlparse

from app.services.rules.models import (
    RuleMatch,
    RuleSeverity,
)
COMPANY_DOMAINS: dict[str, tuple[str, ...]] = {
    "amazon": ("amazon.com",),
    "apple": ("apple.com",),
    "google": ("google.com",),
    "microsoft": ("microsoft.com",),
    "netflix": ("netflix.com",),
    "paypal": ("paypal.com",),
}

FREE_EMAIL_DOMAINS = {
    "gmail.com",
    "outlook.com",
    "hotmail.com",
    "yahoo.com",
    "icloud.com",
}

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

URL_PATTERN = re.compile(
    r"https?://[^\s<>'\"]+",
    flags=re.IGNORECASE,
)

URL_SHORTENER_DOMAINS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "ow.ly",
    "is.gd",
    "buff.ly",
    "cutt.ly",
    "rebrand.ly",
}


@dataclass(frozen=True)
class IdentityAnalysis:
    emails: tuple[str, ...]
    urls: tuple[str, ...]
    matches: tuple[RuleMatch, ...]


def remove_trailing_punctuation(url: str) -> str:
    return url.rstrip(".,;:!?)]}")


def extract_emails(text: str) -> list[str]:
    emails = EMAIL_PATTERN.findall(text)

    return list(dict.fromkeys(emails))


def extract_urls(text: str) -> list[str]:
    raw_urls = URL_PATTERN.findall(text)

    cleaned_urls = [
        remove_trailing_punctuation(url)
        for url in raw_urls
    ]

    return list(dict.fromkeys(cleaned_urls))


def hostname_is_ip_address(hostname: str) -> bool:
    try:
        ipaddress.ip_address(hostname)
        return True
    except ValueError:
        return False


def has_excessive_subdomains(hostname: str) -> bool:
    hostname_parts = hostname.split(".")

    return len(hostname_parts) >= 5


def analyze_identity_signals(text: str) -> IdentityAnalysis:
    emails = extract_emails(text)
    urls = extract_urls(text)

    matches: list[RuleMatch] = []
    detected_rule_ids: set[str] = set()

    for url in urls:
        parsed_url = urlparse(url)
        hostname = (parsed_url.hostname or "").lower()

        if not hostname:
            continue

        if (
            hostname_is_ip_address(hostname)
            and "ip-address-url" not in detected_rule_ids
        ):
            matches.append(
                RuleMatch(
                    rule_id="ip-address-url",
                    title="IP-address link",
                    category="phishing",
                    severity=RuleSeverity.HIGH,
                    evidence=url,
                    explanation=(
                        "This link uses a numeric IP address instead of "
                        "a recognizable domain name. Attackers sometimes "
                        "use IP-address links to hide the destination."
                    ),
                    score=20,
                )
            )
            detected_rule_ids.add("ip-address-url")

        if (
            hostname in URL_SHORTENER_DOMAINS
            and "shortened-url" not in detected_rule_ids
        ):
            matches.append(
                RuleMatch(
                    rule_id="shortened-url",
                    title="Shortened URL",
                    category="phishing",
                    severity=RuleSeverity.MEDIUM,
                    evidence=url,
                    explanation=(
                        "URL shorteners hide the final destination. "
                        "The link should be expanded and verified "
                        "before it is opened."
                    ),
                    score=12,
                )
            )
            detected_rule_ids.add("shortened-url")

        if (
            (
                hostname.startswith("xn--")
                or ".xn--" in hostname
            )
            and "punycode-domain" not in detected_rule_ids
        ):
            matches.append(
                RuleMatch(
                    rule_id="punycode-domain",
                    title="Encoded lookalike domain",
                    category="phishing",
                    severity=RuleSeverity.HIGH,
                    evidence=url,
                    explanation=(
                        "The domain contains Punycode encoding. "
                        "Punycode can be legitimate, but it may also "
                        "be used to imitate familiar domain names."
                    ),
                    score=18,
                )
            )
            detected_rule_ids.add("punycode-domain")

        if (
            has_excessive_subdomains(hostname)
            and "excessive-subdomains" not in detected_rule_ids
        ):
            matches.append(
                RuleMatch(
                    rule_id="excessive-subdomains",
                    title="Excessive subdomains",
                    category="phishing",
                    severity=RuleSeverity.MEDIUM,
                    evidence=url,
                    explanation=(
                        "This link contains an unusually long domain "
                        "structure. Attackers may place familiar words "
                        "in subdomains to disguise the real domain."
                    ),
                    score=10,
                )
            )
            detected_rule_ids.add("excessive-subdomains")

    company_matches = find_company_domain_mismatches(
        text,
        emails,
    )

    matches.extend(company_matches)

    return IdentityAnalysis(
        emails=tuple(emails),
        urls=tuple(urls),
        matches=tuple(matches),
    )

def message_claims_company(
    text: str,
    company: str,
) -> bool:
    lowered_text = text.lower()

    claim_patterns = (
        f"i am from {company}",
        f"i'm from {company}",
        f"recruiter from {company}",
        f"{company} recruiter",
        f"{company} recruiting",
        f"{company} hiring",
        f"{company} hr",
        f"representing {company}",
        f"{company} security",
        f"{company} support",
        f"{company} account",
    )

    return any(
        pattern in lowered_text
        for pattern in claim_patterns
    )

def get_email_domain(email: str) -> str:
    _, _, domain = email.lower().rpartition("@")
    return domain

def domain_matches_expected(
    domain: str,
    expected_domains: tuple[str, ...],
) -> bool:
    return any(
        domain == expected_domain
        or domain.endswith(f".{expected_domain}")
        for expected_domain in expected_domains
    )

def find_company_domain_mismatches(
    text: str,
    emails: tuple[str, ...] | list[str],
) -> list[RuleMatch]:
    lowered_text = text.lower()
    matches: list[RuleMatch] = []

    for company, expected_domains in COMPANY_DOMAINS.items():
        if not message_claims_company(
            text,
            company,
        ):
            continue

        for email in emails:
            domain = get_email_domain(email)

            if not domain:
                continue

            if domain_matches_expected(
                domain,
                expected_domains,
            ):
                continue

            expected_display = " or ".join(expected_domains)

            matches.append(
                RuleMatch(
                    rule_id="company-domain-mismatch",
                    title="Company and email domain do not match",
                    category="phishing",
                    severity=RuleSeverity.HIGH,
                    score=20,
                    evidence=email,
                    explanation=(
                        f"The message mentions {company.title()}, "
                        f"but the email address uses {domain} instead "
                        f"of an expected company domain such as "
                        f"{expected_display}."
                    ),
                )
            )

    return matches