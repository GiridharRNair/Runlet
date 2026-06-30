import os
from models import ExecuteResponse
from pathlib import Path
from services.execute_utils import (
    run,
    parse_metadata,
    SandboxInternalError,
    ISOLATE_DIRS,
)
from config import settings


async def execute(
    box_id: int, box_dir: Path, meta_path: str, code: str, stdin: str
) -> ExecuteResponse:
    (box_dir / "solution.cpp").write_text(code)

    rc, _, stderr = await run(
        "isolate",
        f"--box-id={box_id}",
        *ISOLATE_DIRS,
        # "--cg",
        f"--time={settings.COMPILE_TIME_LIMIT}",
        f"--wall-time={settings.COMPILE_TIME_LIMIT * 2:.1f}",
        # f"--cg-mem={COMPILE_MEMORY_LIMIT * 1024}",
        "--processes=128",
        "--env=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "--run",
        "--",
        "/usr/bin/g++",
        "-O2",
        "-o",
        "/box/solution",
        "/box/solution.cpp",
    )

    if rc != 0:
        return ExecuteResponse(status="CE", stdout="", stderr=stderr)

    os.chmod(box_dir / "solution", 0o755)
    (box_dir / "stdin.txt").write_text(stdin)

    _, stdout, stderr = await run(
        "isolate",
        f"--box-id={box_id}",
        *ISOLATE_DIRS,
        # "--cg",
        f"--time={settings.TIME_LIMIT}",
        f"--wall-time={settings.TIME_LIMIT * 2:.1f}",
        # f"--cg-mem={MEMORY_LIMIT * 1024}",
        "--processes=128",
        f"--meta={meta_path}",
        "--stdin=/box/stdin.txt",
        "--run",
        "--",
        "/box/solution",
    )

    meta = parse_metadata(meta_path)
    isolate_status = meta.get("status", "")

    if isolate_status == "TO":
        status = "TLE"
    elif meta.get("cg-oom-killed") == "1":
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
        stderr=stderr,
        time=float(meta["time"]) if "time" in meta else None,
        memory=int(meta["cg-mem"]) if "cg-mem" in meta else None,
    )
