from fastapi import FastAPI
import uvicorn
from api.v1 import mongo_health
from api.v1 import is_alive

app = FastAPI()

app.include_router(is_alive.router, prefix="/v1")
app.include_router(mongo_health.router, prefix="/v1")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
