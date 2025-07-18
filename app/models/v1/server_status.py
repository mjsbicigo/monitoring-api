from pydantic import BaseModel
from typing import Optional

class ServerStatus(BaseModel):
    server: str
    status: str
    error: Optional[str] = None
