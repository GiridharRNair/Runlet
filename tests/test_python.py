from conftest import execute


def test_hello_world(client):
    result = execute(client, "python", 'print("Hello, World!")')
    assert result["status"] == "OK"
    assert result["stdout"] == "Hello, World!\n"
    assert result["stderr"] == ""


def test_stdin(client):
    code = "a, b = map(int, input().split())\nprint(a + b)"
    result = execute(client, "python", code, stdin="3 5")
    assert result["status"] == "OK"
    assert result["stdout"].strip() == "8"


def test_multiline_output(client):
    code = "for i in range(1, 4):\n    print(i)"
    result = execute(client, "python", code)
    assert result["status"] == "OK"
    assert result["stdout"] == "1\n2\n3\n"


def test_tle(client):
    result = execute(client, "python", "while True: pass")
    assert result["status"] == "TLE"


def test_runtime_error(client):
    result = execute(client, "python", "print(1 / 0)")
    assert result["status"] == "RE"
    assert result["stderr"] != ""


def test_empty_output(client):
    result = execute(client, "python", "x = 1 + 1")
    assert result["status"] == "OK"
    assert result["stdout"] == ""
