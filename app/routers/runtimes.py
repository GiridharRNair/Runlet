from fastapi import APIRouter, Request
from models import LanguageRuntime
from limiter import limiter

ROUTE_RATE_LIMIT = "10"

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
@limiter.limit(f"{ROUTE_RATE_LIMIT}/minute")
async def get_runtimes(request: Request) -> list[LanguageRuntime]:
    return RUNTIMES
