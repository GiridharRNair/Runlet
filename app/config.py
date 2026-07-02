from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TIME_LIMIT: float = 5.0
    MEMORY_LIMIT: int = 256
    COMPILE_TIME_LIMIT: float = 30.0
    COMPILE_MEMORY_LIMIT: int = 512
    MAX_BOXES: int = 3
    USE_CGROUPS: bool = True
    CODE_EXECUTION_RATE_LIMIT: str = "10"


settings = Settings()
