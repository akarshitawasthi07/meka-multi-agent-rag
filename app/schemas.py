from pydantic import BaseModel
from typing import Optional

class AskRequest(BaseModel):
    query: str
    web_search: Optional[bool] = False
    thread_id: Optional[str] = "default_user"