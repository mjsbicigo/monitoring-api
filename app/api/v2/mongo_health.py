from fastapi import APIRouter, Depends, Query
from datetime import datetime
from models.v2.db_server_status import MongoDbServerStatus
from security.api_key import get_api_key
from pymongo import MongoClient
from config import settings
from typing import List, Optional
import re

router = APIRouter()

def get_mongodb_collection(mongodb_uri: str):
    """
    This function receives a MongoDB connection string and defines the connection parameters with the server.
    Returns the collection to be queried.
    """
    client = MongoClient(mongodb_uri)
    db = client["AllTenants"]
    
    return db["Tenants"]

def get_server_name(mongodb_uri: str) -> str:
    """
    This function receives a MongoDB connection URI and uses regex to extract the server name.
    Returns the server name.
    """
    match = re.search(r'mongodb\+srv:\/\/[^@]+@([^\/]+)', mongodb_uri)
    if match:
        return match.group(1)
    return "Unknown Server"

@router.get("/mongohealth", response_model=List[MongoDbServerStatus], dependencies=[Depends(get_api_key)])
async def health_check(server: Optional[List[str]] = Query(default=None)):
    """
    This route checks the status of the MongoDB(s).
    - If 'server' is provided, checks only the specified servers.
    - If 'server' is omitted, checks all servers.

    Ps: Server URI(s) must be defined in the configuration file as MONGODB_URIS, separated by commas. The server name is extracted from the URI for display purposes.
    """
    
    if not settings.MONGODB_URIS:
        return [{
            "server": "N/A",
            "status": "error",
            "error": "No MongoDB URIs configured. Please set MONGODB_URIS in your configuration file."
        }]
    
    all_uris = [uri.strip() for uri in settings.MONGODB_URIS.split(",") if uri.strip()]

    if server:
        uris_to_check = [uri for uri in all_uris if get_server_name(uri) in server]
        not_found = [s for s in server if s not in [get_server_name(uri) for uri in all_uris]]
        if not_found:
            for s in not_found:
                print(f'{datetime.now()} - Error: Server not found in configuration: {s}')
                
            return [{
                "server": s,
                "status": "error",
                "error": "Server not found in configuration"
            } for s in not_found]
    else:
        uris_to_check = all_uris

    results = []
    print()
    
    for uri in uris_to_check:
        server_name = get_server_name(uri)
        print(f'{datetime.now()} - Checking: {server_name}')
        
        try:
            collection = get_mongodb_collection(uri)
            collection.database.client.admin.command('ping')
            collection.find_one()
            results.append({ "server": server_name, "status": "ok" })
        except Exception as e:
            results.append({
                "server": server_name,
                "status": "error",
                "error": str(e)
            })
        finally:
            if 'collection' in locals() and collection.database.client:
                collection.database.client.close()
                print(f'{datetime.now()} - Closing connection.\n')

    return results
