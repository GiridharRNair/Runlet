from pathlib import Path
from models import ExecuteResponse
from services.execute_utils import (
    run,
    parse_metadata,
    SandboxInternalError,
    ISOLATE_DIRS,
    memory_flags,
    is_mle,
    get_memory_used,
)
from config import settings


async def execute(
    box_id: int, box_dir: Path, meta_path: str, code: str, stdin: str
) -> ExecuteResponse:
    (box_dir / "main.js").write_text(code)
    (box_dir / "stdin.txt").write_text(stdin)

    try:
        _, stdout, stderr = await run(
            "isolate",
            f"--box-id={box_id}",
            *ISOLATE_DIRS,
            *memory_flags(settings.MEMORY_LIMIT),
            f"--time={settings.TIME_LIMIT}",
            f"--wall-time={settings.TIME_LIMIT * 2:.1f}",
            "--processes=128",
            f"--meta={meta_path}",
            "--stdin=/box/stdin.txt",
            "--run",
            "--",
            "/usr/bin/node",
            "/box/main.js",
        )
    except OSError as e:
        raise OSError(f"JavaScript execute phase: {e}") from e

    try:
        meta = parse_metadata(meta_path)
    except SandboxInternalError as e:
        raise SandboxInternalError(f"JavaScript execute phase: {e}") from e
    isolate_status = meta.get("status", "")

    if isolate_status == "TO":
        status = "TLE"
    elif is_mle(meta, isolate_status):
        status = "MLE"
    elif isolate_status in ("RE", "SG"):
        status = "RE"
    elif isolate_status == "XX":
        raise SandboxInternalError("Sandbox internal error")
    else:
        status = "OK"

    return ExecuteResponse(
        status=status,
        stdout=stdout,
        stderr=stderr if status != "OK" else "",
        time=float(meta["time"]) if "time" in meta else None,
        memory=get_memory_used(meta),
    )
