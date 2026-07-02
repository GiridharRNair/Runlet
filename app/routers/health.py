from fastapi import APIRouter, Request
from limiter import limiter

ROUTE_RATE_LIMIT = "10"

router = APIRouter()


@router.get("/health")
@limiter.limit(f"{ROUTE_RATE_LIMIT}/minute")
def health(request: Request):
    return {"status": "healthy"}
