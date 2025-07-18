import os

# Definindo as variáveis de ambiente:
    # Chave de API.
    # URIs de conexão com o MongoDB
class Settings:
    API_KEY: str = os.getenv("API_KEY", None)
    MONGODB_URIS = os.getenv("MONGODB_URIS", None)
    
    # Verificando se as variáveis de ambiente existem
    def __init__(self):
        if not self.MONGODB_URIS:
            raise ValueError("Missing environment variable: MONGODB_URIS")
        if not self.API_KEY:
            raise ValueError("Missing environment variable: API_KEY")

settings = Settings()
