from pydantic import BaseModel
from typing import List


class ChatResponse(BaseModel):

    response: str

    safe: bool

    risk: str

    reasons: List[str]