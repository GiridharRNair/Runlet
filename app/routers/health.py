from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.get("/health")
@limiter.limit("10/minute")
def health(request: Request):
    return {"status": "healthy"}
