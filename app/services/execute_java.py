import os
from models import ExecuteResponse
from pathlib import Path
from services.execute_utils import (
    run,
    parse_metadata,
    SandboxInternalError,
    ISOLATE_DIRS,
    is_mle,
    get_memory_used,
)
from config import settings


def _java_memory_flags(limit_mb: int) -> list[str]:
    """
    The JVM reserves a large virtual address space upfront before any user code runs, so --mem
    (which limits virtual memory, not physical) would kill Java during startup rather than when it
    actually exceeds a meaningful memory threshold — making the limit misleading and unusable in
    dev. In production, cgroups measure physical memory accurately so the limit works as intended.
    """
    if settings.USE_CGROUPS:
        return ["--cg", f"--cg-mem={limit_mb * 1024}"]
    return []


async def execute(
    box_id: int, box_dir: Path, meta_path: str, code: str, stdin: str
) -> ExecuteResponse:
    (box_dir / "Main.java").write_text(code)

    try:
        rc, _, stderr = await run(
            "isolate",
            f"--box-id={box_id}",
            *ISOLATE_DIRS,
            *_java_memory_flags(settings.COMPILE_MEMORY_LIMIT),
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
        _, stdout, stderr = await run(
            "isolate",
            f"--box-id={box_id}",
            *ISOLATE_DIRS,
            *_java_memory_flags(settings.MEMORY_LIMIT),
            f"--time={settings.TIME_LIMIT}",
            f"--wall-time={settings.TIME_LIMIT * 2:.1f}",
            "--processes=128",
            f"--meta={meta_path}",
            "--stdin=/box/stdin.txt",
            "--run",
            "--",
            "/usr/lib/jvm/java-min/bin/java",
            "-cp",
            "/box",
            "Main",
        )
    except OSError as e:
        raise OSError(f"Java execute phase: {e}") from e

    meta = parse_metadata(meta_path)
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
