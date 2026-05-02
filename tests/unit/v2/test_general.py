import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app 
from config import settings

client = TestClient(app)

# Standard Header for tests, including API key if configured. Adjust as needed for your authentication setup.
HEADERS = {"X-API-KEY": settings.API_KEY} if settings.API_KEY else {"X-API-KEY": "test-key"}

### Testing /generic route ###

@patch("api.v2.generic_api_query.requests.request")
def test_generic_api_query_success(mock_request):
    """Test a well successful check of an external API with mocked requests"""
    
    # Mock configuration to simulate a successful response from the target API
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "success"}
    mock_request.return_value = mock_response

    payload = {
        "url": "https://httpbin.org/get",
        "method": "GET"
    }

    response = client.post("/v2/generic", json=payload, headers=HEADERS)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["status_code"] == 200
    assert data["response"] == {"message": "success"}
    mock_request.assert_called_once() # Ensure our mock was called, indicating the route logic reached the point of making the request

def test_generic_api_query_invalid_url():
    """Test the behavior when sending an malformed URL"""
    payload = {
        "url": "wrong-url",
        "method": "GET"
    }

    response = client.post("/v2/generic", json=payload, headers=HEADERS)
    
    assert response.status_code == 422 


### Testing /mongohealth route ###

@patch("api.v2.mongo_health.settings")
def test_mongohealth_missing_uri_env_var(mock_settings):
    """Testing fallback behavior when MONGODB_URIS is not set in the environment variables"""
    
    # Simulando a ausência da variável de ambiente
    mock_settings.MONGODB_URIS = None

    response = client.get("/v2/mongohealth", headers=HEADERS)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["status"] == "error"
    assert "No MongoDB URIs configured" in data[0]["error"]

@patch("api.v2.mongo_health.get_mongodb_collection")
def test_mongohealth_success(mock_get_collection):
    """Testing a successful MongoDB check by mocking the real connection"""
    
    # Setting environment variable for MongoDB URIs
    settings.MONGODB_URIS = "mongodb+srv://user:pass@cluster0.mongodb.net/test"
    
    # Creating a mock collection that simulates a successful ping and find_one operation
    mock_collection = MagicMock()
    mock_collection.database.client.admin.command.return_value = {"ok": 1}
    mock_collection.find_one.return_value = {"_id": "123"}
    mock_get_collection.return_value = mock_collection

    response = client.get("/v2/mongohealth", headers=HEADERS)
    
    assert response.status_code == 200
    data = response.json()
    assert data[0]["status"] == "ok"
    assert data[0]["server"] == "cluster0.mongodb.net"