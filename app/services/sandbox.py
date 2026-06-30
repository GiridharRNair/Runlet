import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from config import settings
from services.execute_utils import run, SandboxInternalError


_pool: asyncio.Queue[int] = asyncio.Queue()


def init_pool() -> None:
    for i in range(settings.MAX_BOXES):
        _pool.put_nowait(i)


@asynccontextmanager
async def sandbox():
    box_id = await _pool.get()
    box_dir = Path(f"/var/local/lib/isolate/{box_id}/box")
    meta_path = f"/tmp/meta_{box_id}.txt"
    try:
        yield box_id, box_dir, meta_path
    finally:
        await run("isolate", f"--box-id={box_id}", "--cleanup")
        rc, _, stderr = await run("isolate", f"--box-id={box_id}", "--init")
        if rc != 0:
            raise SandboxInternalError(f"Failed to reset sandbox {box_id}: {stderr}")
        _pool.put_nowait(box_id)
