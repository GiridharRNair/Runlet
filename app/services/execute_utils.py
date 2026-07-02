import asyncio
from pathlib import Path
from config import settings

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


def memory_flags(limit_mb: int) -> list[str]:
    if settings.USE_CGROUPS:
        return ["--cg", f"--cg-mem={limit_mb * 1024}"]
    return []


def get_memory_used(meta: dict[str, str]) -> int | None:
    key = "cg-mem" if settings.USE_CGROUPS else "max-rss"
    return int(meta[key]) if key in meta else None


async def run(*args: str, stdin_data: str = "") -> tuple[int | None, str, str]:
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except OSError as e:
        raise OSError(f"Failed to spawn '{args[0]}': {e}") from e
    try:
        stdout, stderr = await proc.communicate(input=stdin_data.encode())
    except asyncio.CancelledError:
        proc.kill()
        await proc.wait()
        raise
    return (
        proc.returncode,
        stdout.decode(errors="replace"),
        stderr.decode(errors="replace"),
    )


def parse_metadata(path: str) -> dict[str, str]:
    try:
        text = Path(path).read_text()
    except FileNotFoundError:
        raise SandboxInternalError(f"Metadata file not created by isolate: {path}")
    meta: dict[str, str] = {}
    for line in text.splitlines():
        key, _, value = line.partition(":")
        meta[key] = value
    return meta
