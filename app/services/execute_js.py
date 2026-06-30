from pathlib import Path
from models import ExecuteResponse
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
    (box_dir / "solution.js").write_text(code)
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
        "/usr/bin/node",
        "/box/solution.js",
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
        stderr=stderr if status != "OK" else "",
        time=float(meta["time"]) if "time" in meta else None,
        memory=int(meta["cg-mem"]) if "cg-mem" in meta else None,
    )
