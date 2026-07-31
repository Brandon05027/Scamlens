from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_suspicious_message_returns_high_risk() -> None:
    response = client.post(
        "/api/v1/analyses/text",
        json={
            "text": (
                "We will send you a check. Reply immediately "
                "with your banking information."
            )
        },
    )

    assert response.status_code == 200, response.json()

    body = response.json()

    assert body["risk_score"] >= 50
    assert body["risk_level"] in {"high", "critical"}
    assert len(body["findings"]) >= 2


def test_normal_message_returns_low_risk() -> None:
    response = client.post(
        "/api/v1/analyses/text",
        json={
            "text": (
                "Our computer science study group will meet "
                "in the library tomorrow afternoon."
            )
        },
    )

    assert response.status_code == 200, response.json()

    body = response.json()

    assert body["risk_score"] == 0
    assert body["risk_level"] == "low"
    assert body["findings"] == []


def test_short_message_is_rejected() -> None:
    response = client.post(
        "/api/v1/analyses/text",
        json={"text": "Hello"},
    )

    assert response.status_code == 422, response.json()


def test_ip_address_url_is_detected() -> None:
    response = client.post(
        "/api/v1/analyses/text",
        json={
            "text": (
                "Verify your account using "
                "http://192.168.10.20/login immediately."
            )
        },
    )

    assert response.status_code == 200, response.json()

    body = response.json()

    rule_ids = {
        finding["rule_id"]
        for finding in body["findings"]
    }

    assert "ip-address-url" in rule_ids
    assert "http://192.168.10.20/login" in body[
        "identity_signals"
    ]["urls"]


def test_email_address_is_extracted() -> None:
    response = client.post(
        "/api/v1/analyses/text",
        json={
            "text": (
                "Contact the scholarship office at "
                "help@example.edu for additional information."
            )
        },
    )

    assert response.status_code == 200, response.json()

    body = response.json()

    assert body["identity_signals"]["emails"] == [
        "help@example.edu"
    ]


def test_normal_url_does_not_create_url_warning() -> None:
    response = client.post(
        "/api/v1/analyses/text",
        json={
            "text": (
                "Course information is available at "
                "https://www.rutgers.edu/academics."
            )
        },
    )

    assert response.status_code == 200, response.json()

    body = response.json()

    url_rule_ids = {
        "ip-address-url",
        "shortened-url",
        "punycode-domain",
        "excessive-subdomains",
    }

    detected_rule_ids = {
        finding["rule_id"]
        for finding in body["findings"]
    }

    assert detected_rule_ids.isdisjoint(url_rule_ids)