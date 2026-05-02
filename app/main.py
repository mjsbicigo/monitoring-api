from fastapi import FastAPI
import uvicorn
from api.v2 import is_alive
from api.v2 import mongo_health
from api.v2 import generic_api_query

app = FastAPI()

# Version 1 of the API
app.include_router(is_alive.router, prefix="/v1")
app.include_router(mongo_health.router, prefix="/v1")
app.include_router(generic_api_query.router, prefix="/v1")

# Version 2 of the API
app.include_router(is_alive.router, prefix="/v2")
app.include_router(mongo_health.router, prefix="/v2")
app.include_router(generic_api_query.router, prefix="/v2")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
