# AI Defra Search Architecture Summary

## System Overview
The system is a microservices-based AI search application composed of four main repositories.

*   **Core (`ai-defra-search-core`)**: Infrastructure and orchestration.
*   **Agent (`ai-defra-search-agent`)**: Backend API and AI logic.
*   **Data (`ai-defra-search-data`)**: Knowledge management, ingestion, and vector search.
*   **Frontend (`ai-defra-search-frontend`)**: User interface and session management.

## Repository Details

### 1. Core (`ai-defra-search-core`)
*   **Role**: Local development orchestration.
*   **Key Files**: `compose.yml`, `service-compose/*.yml`.
*   **Infrastructure Provided**:
    *   **Network**: `ai-defra-search` (Bridge network).
    *   **Databases**: MongoDB (Port 27017), Redis (Port 6379), Postgres (Port 5432).
    *   **AWS Mock**: LocalStack (Port 4566).

### 2. Data (`ai-defra-search-data`)
*   **Role**: Knowledge management, document ingestion, and vector search for RAG.
*   **Tech Stack**: Python, FastAPI, UV, pgvector, Liquibase.
*   **Port**: 8085.
*   **Traefik**: `data.localhost`.
*   **Key Paths**:
    *   `app/knowledge_management/`: Knowledge groups and sources (MongoDB).
    *   `app/ingestion/`: Ingests pre-chunked S3 data, generates embeddings via Bedrock, stores vectors.
    *   `app/snapshot/`: Versioned snapshots; semantic search via `POST /snapshots/query`.
    *   `app/infra/mcp_server.py`: MCP server for AI tool integration.
*   **Data Persistence**: Postgres (pgvector for embeddings), MongoDB (knowledge group metadata).
*   **Dependencies**: Postgres, MongoDB, LocalStack (S3), Bedrock (embeddings).
*   **DB Migrations**: Liquibase (`ai-defra-search-data-db-migrator`) runs before app startup.

### 3. Frontend (`ai-defra-search-frontend`)
*   **Role**: Web server serving the UI.
*   **Tech Stack**: Node.js, Hapi.dev, Nunjucks templates.
*   **Port**: 3000.
*   **Key Paths**:
    *   `src/server/start/controller.js`: Handles form submission.
    *   `src/server/start/chat-api.js`: HTTP client for the Agent API.
*   **Integration**: POSTs user input to `ai-defra-search-agent`.

### 4. Agent (`ai-defra-search-agent`)
*   **Role**: AI Business logic and State management.
*   **Tech Stack**: Python, FastAPI, UV.
*   **Port**: 8086.
*   **Key Paths**:
    *   `app/chat/router.py`: Entry point for `/chat`.
    *   `app/chat/service.py`: Orchestrates conversation flow.
    *   `app/bedrock/service.py`: Interfaces with AWS Bedrock (or LocalStack).
*   **Data Persistence**: Stores conversation history in MongoDB.
*   **Integration**: Calls **Data** `POST /snapshots/query` for RAG (via `KNOWLEDGE_BASE_URL`, `KnowledgeRetriever`).

## Data Flow (Chat Request)
1.  **User** submits question on Frontend.
2.  **Frontend** (`startPostController`) sends `POST /chat` to Agent.
3.  **Agent** (`ChatService`) retrieves/creates conversation in **MongoDB**.
4.  **Agent** (optional RAG) calls **Data** `POST /snapshots/query` for relevant docs (via `KnowledgeRetriever`).
5.  **Agent** invokes **AWS Bedrock** (via `BedrockInferenceService`) for LLM response (with RAG context if available).
6.  **Agent** saves updated history to **MongoDB**.
7.  **Agent** returns response to **Frontend**.
8.  **Frontend** renders response via Nunjucks.

## Data Flow (Knowledge Ingestion)
1.  **Admin** creates knowledge group via `POST /knowledge/groups`, adds sources via `PATCH /knowledge/groups/{id}/sources`.
2.  **Admin** triggers `POST /knowledge/groups/{id}/ingest`.
3.  **Data** reads pre-chunked JSONL from **S3** (LocalStack), generates embeddings via **Bedrock**, stores vectors in **Postgres** (pgvector).
4.  Snapshot created; activate via `PATCH /snapshots/{id}/activate` for RAG use.

