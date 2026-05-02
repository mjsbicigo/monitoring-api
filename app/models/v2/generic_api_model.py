from pydantic import BaseModel, AnyHttpUrl
from typing import Optional, Any, Dict

class ApiStatus(BaseModel):
    url: str
    status: str                          # "ok" if successful, "error" if there was an exception
    status_code: Optional[int] = None    # response status code received from the target URL (if any)
    response: Optional[Any] = None       # body response received from the target URL (if any)
    error: Optional[str] = None          # error message if an exception occurred

class GenericRequest(BaseModel):
    url: AnyHttpUrl                             # Provides built-in validation for URLs
    method: Optional[str] = "GET"               # HTTP method to use (default: GET)
    headers: Optional[Dict[str, str]] = None    # Optional headers to include in the request
    payload: Optional[Any] = None               # Optional request body (can be dict, list, str, etc.)
    auth: Optional[Dict[str, str]] = None       # ex.: {"username": "...", "password": "..."}