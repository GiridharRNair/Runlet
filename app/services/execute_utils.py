import asyncio
from pathlib import Path


class SandboxInternalError(Exception):
    pass


async def run(*args: str, stdin_data: str = "") -> tuple[int | None, str, str]:
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate(input=stdin_data.encode())
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
