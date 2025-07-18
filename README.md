# MongoDB Monitoring API

This API's main functionality is to monitor the status of multiple MongoDB servers, allowing individual or batch queries, with authentication via API Key and dynamic configuration through environment variables.

> **Note:**  
> This solution was developed to work in conjunction with the Elasticsearch monitoring feature, enabling continuous querying of MongoDB server status and sending alerts through various contact channels if any server becomes unavailable.  
> The API architecture allows for future enhancements to monitor other types of applications beyond MongoDB, expanding its usefulness for different monitoring scenarios.

## Features

- Status check of multiple MongoDB servers.
- Ability to check all servers or only specific ones.
- Dynamic configuration via environment variables.
- Route protection with API Key.
- Detailed response with the individual status of each queried server.

## Prerequisites

- Python 3.7 or higher installed.
- Pip (Python package manager) installed.
- Required environment variables:
  - `API_KEY` – API authentication key.
  - `MONGODB_URIS` – comma-separated list of MongoDB connection URIs.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/stefanini-applications/mongodb-monitoring-api.git
    cd mongodb-monitoring-api
    ```

2. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set the environment variables:

    **Windows (PowerShell):**
    ```powershell
    $Env:API_KEY="your_api_key_here"
    $Env:MONGODB_URIS="mongo_uri1,mongo_uri2"
    ```

    **Linux/macOS:**
    ```bash
    export API_KEY="your_api_key_here"
    export MONGODB_URIS="mongo_uri1,mongo_uri2"
    ```

## Usage

Run the application with:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

The application will be available at `http://localhost:8080`.

## API Routes

### `/v1/mongohealth`

#### Description
Checks the health of one or more MongoDB servers, returning the individual status of each (OK or error).

#### Method
`GET /v1/mongohealth`

#### Query Parameters (optional)

- `server`: server name(s), as extracted from the URI.
  - Example:
    ```
    /v1/mongohealth?server=cluster1.mongodb.net&server=cluster2.mongodb.net
    ```

  - If omitted, **all** servers defined in `MONGODB_URIS` will be checked.

#### Authentication
Required via API Key in the header:
```
x-api-key: your_api_key_here
```

#### Example Response - Success
```json
[
  {
    "server": "cluster1.mongodb.net",
    "status": "ok"
  },
  {
    "server": "cluster2.mongodb.net",
    "status": "ok"
  }
]
```

#### Example Response - Failure
```json
[
  {
    "server": "cluster1.mongodb.net",
    "status": "ok"
  },
  {
    "server": "cluster2.mongodb.net",
    "status": "error",
    "error": "timed out"
  }
]
```

#### Example - Server not found in configuration
```json
[
  {
    "server": "nonexistent_cluster.mongodb.net",
    "status": "error",
    "error": "Server not found in configuration"
  }
]
```

---

### `/v1/isalive`

#### Description
Checks if the API is alive (liveness probe).

#### Method
`GET /v1/isalive`

#### Response
```json
{
  "status": "true"
}
```

---

## Data Models

### `ServerStatus`

```python
class ServerStatus(BaseModel):
    server: str
    status: str  # "ok" or "error"
    error: Optional[str]
```