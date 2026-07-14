import os
from models import ExecuteResponse
from pathlib import Path
from services.execute_utils import (
    run,
    parse_metadata,
    SandboxInternalError,
    ISOLATE_DIRS,
    memory_flags,
    get_memory_used,
)
from config import settings


async def execute(
    box_id: int, box_dir: Path, meta_path: str, code: str, stdin: str
) -> ExecuteResponse:
    (box_dir / "Main.java").write_text(code)

    try:
        rc, _, stderr = await run(
            "isolate",
            f"--box-id={box_id}",
            *ISOLATE_DIRS,
            *memory_flags(settings.COMPILE_MEMORY_LIMIT),
            f"--time={settings.COMPILE_TIME_LIMIT}",
            f"--wall-time={settings.COMPILE_TIME_LIMIT * 2:.1f}",
            "--processes=128",
            "--run",
            "--",
            "/usr/bin/javac",
            "/box/Main.java",
        )
    except OSError as e:
        raise OSError(f"Java compile phase: {e}") from e

    if rc != 0:
        return ExecuteResponse(status="CE", stdout="", stderr=stderr)

    for cls_file in box_dir.glob("*.class"):
        os.chmod(cls_file, 0o644)
    (box_dir / "stdin.txt").write_text(stdin)

    try:
        await run(
            "isolate",
            f"--box-id={box_id}",
            *ISOLATE_DIRS,
            *memory_flags(settings.MEMORY_LIMIT),
            f"--time={settings.TIME_LIMIT}",
            f"--wall-time={settings.TIME_LIMIT * 2:.1f}",
            f"--fsize={settings.OUTPUT_LIMIT}",
            "--processes=128",
            f"--meta={meta_path}",
            "--stdin=/box/stdin.txt",
            "--stdout=output.txt",
            "--stderr=error.txt",
            "--run",
            "--",
            "/usr/lib/jvm/java-min/bin/java",
            "-cp",
            "/box",
            "Main",
        )
    except OSError as e:
        raise OSError(f"Java execute phase: {e}") from e

    try:
        meta = parse_metadata(meta_path)
    except SandboxInternalError as e:
        raise SandboxInternalError(f"Java execute phase: {e}") from e
    isolate_status = meta.get("status", "")
    output_limit_bytes = settings.OUTPUT_LIMIT * 1024
    output_limit_exceeded = (
        box_dir / "output.txt"
    ).stat().st_size >= output_limit_bytes or (
        box_dir / "error.txt"
    ).stat().st_size >= output_limit_bytes

    if output_limit_exceeded:
        status = "OLE"
    elif isolate_status == "TO":
        status = "TLE"
    elif meta.get("cg-oom-killed") == "1":
        status = "MLE"
    elif isolate_status in ("RE", "SG"):
        status = "RE"
    elif isolate_status == "XX":
        raise SandboxInternalError("Sandbox internal error")
    else:
        status = "OK"

    stdout = (box_dir / "output.txt").read_text(errors="replace")
    stderr = (box_dir / "error.txt").read_text(errors="replace")

    return ExecuteResponse(
        status=status,
        stdout=stdout if status != "OLE" else "",
        stderr=stderr if status not in ("OK", "OLE") else "",
        time=float(meta["time"]) if "time" in meta else None,
        memory=get_memory_used(meta),
    )
