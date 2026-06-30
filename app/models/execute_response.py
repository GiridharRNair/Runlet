from pydantic import BaseModel


class ExecuteResponse(BaseModel):
    status: str  # OK | TLE | MLE | RE | CE
    stdout: str
    stderr: str
    time: float | None = None
    memory: int | None = None  # KB
