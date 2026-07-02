import os
import pytest
import httpx

BASE_URL = os.getenv("API_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as c:
        yield c


def execute(client, language: str, code: str, stdin: str = "") -> dict:
    resp = client.post(
        "/execute", json={"language": language, "code": code, "stdin": stdin}
    )
    resp.raise_for_status()
    return resp.json()
