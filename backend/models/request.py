from pydantic import BaseModel


class ChatRequest(BaseModel):

    message: str

    session_id: str | None = None

    language: str | None = None