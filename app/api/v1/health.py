from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from app.models.v1.status_response import StatusResponse
from security.api_key import get_api_key
from pymongo import MongoClient
from config import settings
from datetime import datetime
import re

router = APIRouter()

def get_mongodb_collection(mongodb_uri: str):
    '''
    Essa função recebe uma connection string do MongoDB e define os parâmetros de conexão com o servidor.
    Retorna a collection que será realizada a consulta.
    '''
    client = MongoClient(mongodb_uri)
    db = client["AllTenants"]
    collection = db["Tenants"]
    
    return collection

def get_server_name(mongodb_uri: str) -> str:
    '''
    Essa função recebe uma uri de conexão com o MongoDB e utiliza regex para extrair o nome do servidor.
    Retorna o nome do servidor.
    '''
    match = re.search(r'mongodb\+srv:\/\/[^@]+@([^\/]+)', mongodb_uri)
    if match:
        return match.group(1)
    return "Unknown Server"

@router.get("/health", response_model=StatusResponse, dependencies=[Depends(get_api_key)], status_code=200)
async def health_check():
    '''
    Rota de verificação do status do MongoDB.
    Para cada string de conexão recebida, é feita uma tentativa de ping e leitura da tabela AllTenants.
    
    Caso todos os servidores respondam positivamente, é retornado status code 200 e {"status": "ok").
    Caso ocorra uma exceção, é retornado o erro 500 com os nomes dos servidores que falharam na verificação.
    '''
    MONGODB_URIS = settings.MONGODB_URIS
    MONGODB_URIS = MONGODB_URIS.split(",")
    
    failed_servers = []
    
    for uri in MONGODB_URIS:
        
        server_name = get_server_name(uri)
        
        print(f'{datetime.now()} - Checking: {server_name}')
        
        collection = get_mongodb_collection(uri)
        try:
            # Verificando a conexão com o MongoDB
            ping = collection.database.client.admin.command('ping')
            print(f'{datetime.now()} - Ping: {ping}')
            
            # Realizando uma consulta de teste
            collection.find_one()
            print(f'{datetime.now()} - Query: OK.')
            
        except Exception as e:
            failed_servers.append(server_name)
            print(f'{datetime.now()} - Error: {e}')
        finally:
            if collection.database.client:
                print(f'{datetime.now()} - Closing connection.\n')
                collection.database.client.close()
    
    if failed_servers:
        raise HTTPException(status_code=500, detail=f'Problem checking server status: {", ".join(failed_servers)}')
    else:
        return {"status": "ok"}
