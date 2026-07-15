from conftest import execute


def test_hello_world(client):
    result = execute(client, "javascript", 'console.log("Hello, World!");')
    assert result["status"] == "OK"
    assert result["stdout"] == "Hello, World!\n"
    assert result["stderr"] == ""


def test_stdin(client):
    code = (
        "const input = require('fs').readFileSync(0, 'utf8').trim();\n"
        "const [a, b] = input.split(' ').map(Number);\n"
        "console.log(a + b);"
    )
    result = execute(client, "javascript", code, stdin="3 5")
    assert result["status"] == "OK"
    assert result["stdout"].strip() == "8"


def test_multiline_output(client):
    code = "[1, 2, 3].forEach(n => console.log(n));"
    result = execute(client, "javascript", code)
    assert result["status"] == "OK"
    assert result["stdout"] == "1\n2\n3\n"


def test_tle(client):
    result = execute(client, "javascript", "while (true) {}")
    assert result["status"] == "TLE"


def test_ole(client):
    code = "console.log('A'.repeat(1024));"
    result = execute(client, "javascript", code)
    assert result["status"] == "OLE"
    assert result["stdout"] == ""
    assert result["stderr"] == ""


def test_runtime_error(client):
    result = execute(client, "javascript", "throw new Error('boom');")
    assert result["status"] == "RE"
    assert result["stderr"] != ""


def test_empty_output(client):
    result = execute(client, "javascript", "const x = 1 + 1;")
    assert result["status"] == "OK"
    assert result["stdout"] == ""
