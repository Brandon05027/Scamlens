from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_screenshot_rate_limit_returns_429() -> None:
    response = None

    for _ in range(12):
        response = client.post(
            "/api/v1/analyses/screenshot",
            files={
                "file": (
                    "invalid.txt",
                    b"not an image",
                    "text/plain",
                )
            },
        )

    assert response is not None
    assert response.status_code == 429