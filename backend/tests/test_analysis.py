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

    assert response.status_code == 200

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

    assert response.status_code == 200

    body = response.json()

    assert body["risk_score"] == 0
    assert body["risk_level"] == "low"
    assert body["findings"] == []


def test_short_message_is_rejected() -> None:
    response = client.post(
        "/api/v1/analyses/text",
        json={"text": "Hello"},
    )

    assert response.status_code == 422