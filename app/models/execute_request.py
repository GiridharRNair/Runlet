from pydantic import BaseModel, Field
from typing import Literal
from config import settings


class ExecuteRequest(BaseModel):
    language: Literal["python", "javascript", "cpp", "java"]
    code: str = Field(max_length=settings.CODE_LIMIT * 1024)
    stdin: str = Field(default="", max_length=settings.STDIN_LIMIT * 1024)
