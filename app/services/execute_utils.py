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
    return [f"--mem={limit_mb * 1024}"]


def is_mle(meta: dict[str, str], isolate_status: str) -> bool:
    if settings.USE_CGROUPS:
        return meta.get("cg-oom-killed") == "1"
    return isolate_status == "ML"


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
