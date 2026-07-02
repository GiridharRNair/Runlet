from conftest import execute

HELLO_WORLD = """\
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}"""

STDIN_SUM = """\
import java.util.Scanner;
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        System.out.println(a + b);
    }
}"""

MULTILINE = """\
public class Main {
    public static void main(String[] args) {
        for (int i = 1; i <= 3; i++)
            System.out.println(i);
    }
}"""

TLE = """\
public class Main {
    public static void main(String[] args) {
        while (true) {}
    }
}"""

RUNTIME_ERROR = """\
public class Main {
    public static void main(String[] args) {
        int[] arr = new int[5];
        System.out.println(arr[10]);
    }
}"""

COMPILE_ERROR = """\
public class Main {
    public static void main(String[] args) {
        this is not valid java
    }
}"""


def test_hello_world(client):
    result = execute(client, "java", HELLO_WORLD)
    assert result["status"] == "OK"
    assert result["stdout"] == "Hello, World!\n"
    assert result["stderr"] == ""


def test_stdin(client):
    result = execute(client, "java", STDIN_SUM, stdin="3 5")
    assert result["status"] == "OK"
    assert result["stdout"].strip() == "8"


def test_multiline_output(client):
    result = execute(client, "java", MULTILINE)
    assert result["status"] == "OK"
    assert result["stdout"] == "1\n2\n3\n"


def test_tle(client):
    result = execute(client, "java", TLE)
    assert result["status"] == "TLE"


def test_runtime_error(client):
    result = execute(client, "java", RUNTIME_ERROR)
    assert result["status"] == "RE"
    assert result["stderr"] != ""


def test_compile_error(client):
    result = execute(client, "java", COMPILE_ERROR)
    assert result["status"] == "CE"
    assert result["stderr"] != ""
