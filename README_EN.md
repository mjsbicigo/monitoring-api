# Monitoring API

This API provides a centralized interface for continuous monitoring of infrastructure assets inside Kubernetes environments. Designed to be extensible, the API currently supports:

- Detailed health checks for MongoDB clusters
- Availability checks for generic HTTP/HTTPS endpoints

---

## Features

### 🗄️ MongoDB Monitoring
- Status checks for multiple servers
- Ability to query the entire cluster or specific nodes

### 🌐 Generic Monitoring
- Availability checks for URLs and external services over HTTP/HTTPS

### ⚙️ Dynamic Configuration
- Targets and credentials are managed via environment variables

### 🔐 Security
- All query routes are protected with an API key

### ☸️ Orchestration Ready
- Dedicated endpoints for liveness and readiness probes

---

## 📋 Requirements

- Python **3.13**
- `pip` (Python package manager)

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `API_KEY` | API authentication key |
| `MONGODB_URIS` | Comma-separated list of MongoDB connection URIs |

---

**⚠️ Security Notice (IMPORTANT)**

- **`API_KEY`**: For convenience in development and testing, the application defaults to `default-insecure-key` when `API_KEY` is not provided. This behavior is intended only for development/test environments. In production, `API_KEY` is strictly required — do not run the API in production with the default key.

- **`MONGODB_URIS`**: Optional. If not configured, requests to `/v2/mongohealth` will return a payload indicating that URIs are not configured:

```json
[
  {
    "server": "N/A",
    "status": "error",
    "error": "No MongoDB URIs configured. Please set MONGODB_URIS in your configuration file."
  }
]
```

## 🛠️ Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/mjsbicigo/monitoring-api.git
cd monitoring-api
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure environment variables

#### Linux/macOS

```bash
export API_KEY="your_api_key_here"
export MONGODB_URIS="mongo_uri1,mongo_uri2"
```

#### Windows (PowerShell)

```powershell
$Env:API_KEY="your_api_key_here"
$Env:MONGODB_URIS="mongo_uri1,mongo_uri2"
```

---

## ▶️ Run Locally

Start the application locally with:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

The app will be available at:

```
http://localhost:8080
```

---

# 📡 API Routes (v2)

## 🔎 `/v2/mongohealth`

### 📌 Description

Checks the health of one or more MongoDB servers, returning individual node connectivity status (`ok` or `error`).

### 🧭 Method

```
GET /v2/mongohealth
```

### 🔍 Query Parameters (Optional)

| Parameter | Description |
|-----------|-------------|
| `server` | Server name (one or multiple), as parsed from the URI |

Example:

```
/v2/mongohealth?server=cluster1.mongodb.net&server=cluster2.mongodb.net
```

If omitted, the API checks all servers listed in `MONGODB_URIS`.

### 🔐 Authentication

Required via header:

```http
x-api-key: your_api_key_here
```

### ✅ Example Response — Success

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

### ❌ Example Response — Failure / Server Not Found

```json
[
  {
    "server": "cluster1.mongodb.net",
    "status": "error",
    "error": "timed out"
  },
  {
    "server": "nonexistent_cluster.mongodb.net",
    "status": "error",
    "error": "Server not found in configuration"
  }
]
```

---

## 🌐 `/v2/generic`

### 📌 Description

Performs an availability check against a generic HTTP/HTTPS service or endpoint, returning connection status.

Ideal for monitoring:
- Third-party APIs
- Internal infrastructure services

### 🧭 Method

```
POST /v2/generic
```

### 🔍 Request Body (JSON)

The endpoint accepts a JSON payload compatible with the `GenericRequest` model. Example when expecting a response from the target:

```json
{
  "url": "https://example.com/",
  "method": "GET",
  "headers": {
    "additionalProp1": "string",
    "additionalProp2": "string",
    "additionalProp3": "string"
  },
  "payload": "string",
  "auth": {
    "additionalProp1": "string",
    "additionalProp2": "string",
    "additionalProp3": "string"
  }
}
```

Note: You can also call via query string with only `url` (e.g. `/v2/generic?url=https://api.example.com/health`), but sending a JSON body allows methods other than `GET`, custom headers, payloads, and authentication details.

### 🔐 Authentication

Required via header:

```http
x-api-key: your_api_key_here
```

### ✅ Example Response

The endpoint returns an object compatible with the `ApiStatus` model:

```json
{
  "url": "https://api.example.com/health",
  "status": "ok",
  "status_code": 200,
  "response": {"message": "healthy"}
}
```

---

## ❤️ `/v2/isalive`

### 📌 Description

Checks whether the monitoring API itself is running.

- No authentication required
- Intended for use as a liveness probe in Kubernetes deployments

### 🧭 Method

```
GET /v2/isalive
```

### ✅ Response

```json
{
  "status": "true"
}
```

---

# 🧩 Main Data Models

## 🗄️ `ServerStatus`

```python
class MongoDbServerStatus(BaseModel):
  server: str
  status: str  # "ok" or "error"
  error: Optional[str] = None
```

---

## 🌐 `GenericStatus`

```python
class ApiStatus(BaseModel):
  url: str
  status: str  # "ok" or "error"
  status_code: Optional[int] = None
  response: Optional[Any] = None
  error: Optional[str] = None


class GenericRequest(BaseModel):
  url: AnyHttpUrl                             # Provides built-in validation for URLs
  method: Optional[str] = "GET"               # HTTP method to use (default: GET)
  headers: Optional[Dict[str, str]] = None    # Optional headers to include in the request
  payload: Optional[Any] = None               # Optional request body (can be dict, list, str, etc.)
  auth: Optional[Dict[str, str]] = None       # e.g. {"username": "...", "password": "..."}
```

---

# 📌 Final Notes

- All monitoring routes require authentication via `API_KEY`.
- The `/v2/isalive` endpoint is public for orchestrator integration.
- The API is designed to be easily extensible to support new monitoring types.

---