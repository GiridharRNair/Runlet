from fastapi import APIRouter, HTTPException, Request
from models import ExecuteRequest, ExecuteResponse
from services import execute_cpp, execute_java, execute_js, execute_python, sandbox
from limiter import limiter
from config import settings


CODE_EXECUTION_RATE_LIMIT = settings.CODE_EXECUTION_RATE_LIMIT

router = APIRouter()

_handlers = {
    "python": execute_python,
    "javascript": execute_js,
    "cpp": execute_cpp,
    "java": execute_java,
}


@router.post("/execute", response_model=ExecuteResponse)
@limiter.limit(f"{CODE_EXECUTION_RATE_LIMIT}/minute")
async def execute(request: Request, data: ExecuteRequest) -> ExecuteResponse:
    handler = _handlers[data.language]
    try:
        async with sandbox() as (box_id, box_dir, meta_path):
            return await handler(box_id, box_dir, meta_path, data.code, data.stdin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
