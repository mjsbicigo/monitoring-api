from fastapi import APIRouter

router = APIRouter()

@router.get("/isalive", status_code=200)
async def is_alive():
    return {"status": "true"}