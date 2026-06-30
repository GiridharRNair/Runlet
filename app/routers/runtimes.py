from fastapi import APIRouter, Request
from models import LanguageRuntime
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


RUNTIMES: list[LanguageRuntime] = [
    LanguageRuntime(
        language_name="Python",
        language_version="3.13.14",
    ),
    LanguageRuntime(
        language_name="JavaScript (Node.js)",
        language_version="20.19.2",
    ),
    LanguageRuntime(
        language_name="C++ (g++)",
        language_version="14.2.0",
    ),
    LanguageRuntime(
        language_name="Java",
        language_version="21.0.11",
    ),
]


@router.get("/runtimes", response_model=list[LanguageRuntime])
@limiter.limit("10/minute")
async def get_runtimes(request: Request) -> list[LanguageRuntime]:
    return RUNTIMES
