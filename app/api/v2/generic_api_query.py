from fastapi import APIRouter, Depends
from datetime import datetime
from models.v2.generic_api_model import ApiStatus, GenericRequest
from security.api_key import get_api_key
import requests
import logging
from urllib.parse import urlparse

router = APIRouter()

@router.post("/generic", response_model=ApiStatus, dependencies=[Depends(get_api_key)])
def generic_api_query(req: GenericRequest, timeout: int = 10):
    """
    This route checks any external API.  
    Payload, headers, and authentication are optional.  
    This route always returns 200 to the caller with information about what happened, regardless of whether the target API is up or down.  

    Args for GenericRequest:
    - url: URL of the API to check.
    - method: HTTP method (GET, POST, etc). Default: GET.
    - headers: Optional headers.
    - payload: Request body (optional).
    - auth: Dictionary with username/password (optional).
    - timeout (int): Request timeout in seconds (default: 10).

    Returns:
    - ApiStatus: Details of the check result.
    """
    
    target_url = str(req.url) # Convert AnyHttpUrl back to string after validation

    try:
        method = req.method or "GET"
        kwargs = {"timeout": timeout}

        if req.headers:
            kwargs["headers"] = req.headers

        if req.payload is not None:
            if method.upper() in ("GET", "DELETE"):
                kwargs["params"] = req.payload
            else:
                kwargs["json"] = req.payload

        if req.auth and "username" in req.auth and "password" in req.auth:
            kwargs["auth"] = (req.auth["username"], req.auth["password"])

        resp = requests.request(method, target_url, **kwargs)

        # Try to parse response as JSON, fallback to text
        try:
            response_content = resp.json()
        except Exception:
            response_content = resp.text

        return ApiStatus(
            url=target_url,
            status="ok",
            status_code=resp.status_code,
            response=response_content
        )
    except Exception as exc:
        # Hide sensitive headers in logs
        headers_log = dict(req.headers) if req.headers else {}
        keys_to_hide = [k for k in headers_log.keys() if k.lower() == "authorization"]
        for k in keys_to_hide:
            headers_log[k] = "***"
            
        logging.exception(f"{datetime.now()} - Exception while checking {target_url} | headers: {headers_log}")
        return ApiStatus(
            url=target_url,
            status="error",
            error=str(exc)
        )