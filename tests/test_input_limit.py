import os

CODE_LIMIT_KB = int(os.getenv("CODE_LIMIT", "1"))
STDIN_LIMIT_KB = int(os.getenv("STDIN_LIMIT", "1"))


def test_code_within_limit_is_accepted(client):
    code = "a" * (CODE_LIMIT_KB * 1024)
    resp = client.post(
        "/execute", json={"language": "python", "code": code, "stdin": ""}
    )
    assert resp.status_code != 422


def test_code_exceeding_limit_is_rejected(client):
    code = "a" * (CODE_LIMIT_KB * 1024 + 1)
    resp = client.post(
        "/execute", json={"language": "python", "code": code, "stdin": ""}
    )
    assert resp.status_code == 422


def test_stdin_within_limit_is_accepted(client):
    stdin = "a" * (STDIN_LIMIT_KB * 1024)
    resp = client.post(
        "/execute",
        json={"language": "python", "code": "print(1)", "stdin": stdin},
    )
    assert resp.status_code != 422


def test_stdin_exceeding_limit_is_rejected(client):
    stdin = "a" * (STDIN_LIMIT_KB * 1024 + 1)
    resp = client.post(
        "/execute",
        json={"language": "python", "code": "print(1)", "stdin": stdin},
    )
    assert resp.status_code == 422
