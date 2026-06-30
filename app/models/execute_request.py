from pydantic import BaseModel
from typing import Literal


class ExecuteRequest(BaseModel):
    language: Literal["python", "javascript", "cpp", "java"]
    code: str
    stdin: str = ""
