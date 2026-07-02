from conftest import execute

HELLO_WORLD = """\
#include <iostream>
int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}"""

STDIN_SUM = """\
#include <iostream>
int main() {
    int a, b;
    std::cin >> a >> b;
    std::cout << a + b << std::endl;
    return 0;
}"""

MULTILINE = """\
#include <iostream>
int main() {
    for (int i = 1; i <= 3; i++)
        std::cout << i << "\\n";
    return 0;
}"""

TLE = """\
int main() {
    while (true) {}
    return 0;
}"""

SEGFAULT = """\
int main() {
    int* p = nullptr;
    *p = 42;
    return 0;
}"""

COMPILE_ERROR = """\
int main() {
    this is not valid c++
}"""


def test_hello_world(client):
    result = execute(client, "cpp", HELLO_WORLD)
    assert result["status"] == "OK"
    assert result["stdout"] == "Hello, World!\n"
    assert result["stderr"] == ""


def test_stdin(client):
    result = execute(client, "cpp", STDIN_SUM, stdin="3 5")
    assert result["status"] == "OK"
    assert result["stdout"].strip() == "8"


def test_multiline_output(client):
    result = execute(client, "cpp", MULTILINE)
    assert result["status"] == "OK"
    assert result["stdout"] == "1\n2\n3\n"


def test_tle(client):
    result = execute(client, "cpp", TLE)
    assert result["status"] == "TLE"


def test_runtime_error(client):
    result = execute(client, "cpp", SEGFAULT)
    assert result["status"] == "RE"


def test_compile_error(client):
    result = execute(client, "cpp", COMPILE_ERROR)
    assert result["status"] == "CE"
    assert result["stderr"] != ""
