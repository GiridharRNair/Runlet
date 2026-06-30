import asyncio
from pathlib import Path

ISOLATE_DIRS = [
    "--dir=/usr",
    "--dir=/bin",
    "--dir=/lib",
    "--dir=/lib64:maybe",
    "--dir=/etc",
    "--dir=/dev:maybe",
]


class SandboxInternalError(Exception):
    pass


async def run(*args: str, stdin_data: str = "") -> tuple[int | None, str, str]:
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate(input=stdin_data.encode())
    except OSError as e:
        raise OSError(f"Failed to spawn '{args[0]}': {e}") from e
    return (
        proc.returncode,
        stdout.decode(errors="replace"),
        stderr.decode(errors="replace"),
    )


def parse_metadata(path: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    try:
        for line in Path(path).read_text().splitlines():
            key, _, value = line.partition(":")
            meta[key] = value
    except FileNotFoundError:
        pass
    return meta
