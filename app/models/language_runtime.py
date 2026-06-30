from pydantic import BaseModel


class LanguageRuntime(BaseModel):
    language_name: str
    language_version: str
