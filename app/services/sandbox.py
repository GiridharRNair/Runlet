import asyncio
from pathlib import Path
from config import settings
from services.execute_utils import run, SandboxInternalError


_pool: asyncio.Queue[int] = asyncio.Queue()


def init_pool() -> None:
    if not _pool.empty():
        return
    for i in range(settings.MAX_BOXES):
        _pool.put_nowait(i)


class sandbox:
    async def __aenter__(self) -> tuple[int, Path, str]:
        self._box_id = await _pool.get()
        box_dir = Path(f"/var/local/lib/isolate/{self._box_id}/box")
        meta_path = f"/tmp/meta_{self._box_id}.txt"
        return self._box_id, box_dir, meta_path

    async def __aexit__(self, *_) -> None:
        cg_flag = ["--cg"] if settings.USE_CGROUPS else []
        try:
            await run("isolate", f"--box-id={self._box_id}", *cg_flag, "--cleanup")
            rc, _, stderr = await run(
                "isolate", f"--box-id={self._box_id}", *cg_flag, "--init"
            )
            if rc != 0:
                raise SandboxInternalError(
                    f"Failed to reset sandbox {self._box_id}: {stderr}"
                )
        finally:
            _pool.put_nowait(self._box_id)
