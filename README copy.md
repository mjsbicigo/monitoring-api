# Woopi Monitoring

Esta API fornece uma interface centralizada para o monitoramento contínuo de ativos de infraestrutura da Woopi. Projetada para ser extensível, a API atualmente suporta:

- Verificação detalhada de saúde de clusters MongoDB
- Validação de disponibilidade de endpoints genéricos (HTTP/HTTPS)

---

## Funcionalidades

### 🗄️ Monitoramento MongoDB
- Verificação de status de múltiplos servidores
- Consulta de todo o cluster ou apenas nós específicos

### 🌐 Monitoramento Genérico
- Validação de disponibilidade de URLs e serviços externos via HTTP/HTTPS

### ⚙️ Configuração Dinâmica
- Gerenciamento de alvos e credenciais via variáveis de ambiente

### 🔐 Segurança
- Proteção de todas as rotas de consulta utilizando **API Key**

### ☸️ Prontidão para Orquestração
- Endpoints dedicados para **liveness** e **readiness probes**

---

## 📋 Pré-requisitos

- Python **3.13** instalado
- `pip` (gerenciador de pacotes do Python) atualizado

### Variáveis de Ambiente Necessárias

| Variável | Descrição |
|----------|------------|
| `API_KEY` | Chave de autenticação da API |
| `MONGODB_URIS` | Lista separada por vírgulas das URIs de conexão MongoDB |

---

**⚠️ Aviso de Segurança (IMPORTANTE)**

- **`API_KEY`**: para facilitar testes e desenvolvimento a aplicação define um valor padrão `default-insecure-key` quando a variável `API_KEY` não é fornecida. Esse comportamento **é somente para ambientes de desenvolvimento/teste**. Em ambientes de produção a variável `API_KEY` é **estritamente necessária** por motivos de segurança — não execute a API em produção com a chave padrão.

- **`MONGODB_URIS`**: Variável opcional. Se não estiver configurada, as requisições feitas para o endpoint `/v2/mongohealth` retornam um payload informando que os URIs não foram configurados:

```json
[
  {
    "server": "N/A",
    "status": "error",
    "error": "No MongoDB URIs configured. Please set MONGODB_URIS in your configuration file."
  }
]
```

## 🛠️ Instalação

### 1️⃣ Clone o repositório

```bash
git clone https://github.com/woopi-operacoes/monitoring-api.git
cd monitoring-api
```

### 2️⃣ Instale as dependências

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure as variáveis de ambiente

#### Linux/macOS

```bash
export API_KEY="sua_api_key_aqui"
export MONGODB_URIS="uri_mongo1,uri_mongo2"
```

#### Windows (PowerShell)

```powershell
$Env:API_KEY="sua_api_key_aqui"
$Env:MONGODB_URIS="uri_mongo1,uri_mongo2"
```

---

## ▶️ Uso Local

Execute a aplicação localmente com:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

A aplicação ficará disponível em:

```
http://localhost:8080
```

---

# 📡 Rotas da API (v2)

## 🔎 `/v2/mongohealth`

### 📌 Descrição

Verifica a saúde de um ou mais servidores MongoDB, retornando o status de conectividade individual de cada nó (`ok` ou `error`).

### 🧭 Método

```
GET /v2/mongohealth
```

### 🔍 Parâmetros de Query (Opcional)

| Parâmetro | Descrição |
|------------|------------|
| `server` | Nome do servidor (ou múltiplos), conforme extraído da URI |

**Exemplo:**

```
/v2/mongohealth?server=cluster1.mongodb.net&server=cluster2.mongodb.net
```

Se omitido, a API verifica todos os servidores definidos na variável `MONGODB_URIS`.

### 🔐 Autenticação

Obrigatória via header:

```http
x-api-key: sua_api_key_aqui
```

### ✅ Exemplo de Resposta — Sucesso

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

### ❌ Exemplo de Resposta — Falha / Servidor Não Encontrado

```json
[
  {
    "server": "cluster1.mongodb.net",
    "status": "error",
    "error": "timed out"
  },
  {
    "server": "cluster_inexistente.mongodb.net",
    "status": "error",
    "error": "Server not found in configuration"
  }
]
```

---

## 🌐 `/v2/generic`

### 📌 Descrição

Realiza uma verificação de disponibilidade em um serviço ou endpoint HTTP/HTTPS genérico, retornando o status da conexão.

Ideal para monitorar:
- APIs de terceiros
- Serviços internos da infraestrutura

### 🧭 Método

```
POST /v2/generic
```

### 🔍 Corpo da Requisição (JSON)

O endpoint aceita um payload JSON compatível com o modelo `GenericRequest`. Exemplo quando se espera receber um `response` do target:

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

> Observação: ainda é possível chamar via query string apenas com `url` (ex.: `/v2/generic?url=https://api.exemplo.com/health`), porém o uso do corpo JSON permite métodos diferentes de `GET`, headers, payload e informações de autenticação.

### 🔐 Autenticação

Obrigatória via header:

```http
x-api-key: sua_api_key_aqui
```

### ✅ Exemplo de Resposta

O endpoint retorna um objeto compatível com o modelo `ApiStatus`:

```json
{
  "url": "https://api.exemplo.com/health",
  "status": "ok",
  "status_code": 200,
  "response": {"message": "healthy"}
}
```

---

## ❤️ `/v2/isalive`

### 📌 Descrição

Verifica se a própria API de monitoramento está em execução.

- Não exige autenticação
- Projetado para uso como **liveness probe** em deployments Kubernetes

### 🧭 Método

```
GET /v2/isalive
```

### ✅ Resposta

```json
{
  "status": "true"
}
```

---

# 🧩 Modelos de Dados Principais

## 🗄️ `ServerStatus`

```python
class MongoDbServerStatus(BaseModel):
  server: str
  status: str  # "ok" ou "error"
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
  auth: Optional[Dict[str, str]] = None       # ex.: {"username": "...", "password": "..."}
```

---

# 📌 Considerações Finais

- Todas as rotas de monitoramento exigem autenticação via `API_KEY`
- Endpoint `/v2/isalive` é público para integração com orquestradores
- A API foi projetada para ser facilmente extensível para novos tipos de monitoramento

---