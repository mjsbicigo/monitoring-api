from pydantic import BaseModel
from typing import Optional

class MongoDbServerStatus(BaseModel):
    server: str
    status: str
    error: Optional[str] = None