# AI Defra Search Architecture Summary

## System Overview
The system is a microservices-based AI search application composed of four main repositories.

*   **Core (`ai-defra-search-core`)**: Infrastructure and orchestration.
*   **Agent (`ai-defra-search-agent`)**: Backend API and AI logic.
*   **Knowledge (`ai-defra-search-knowledge`)**: Knowledge groups, document ingest, embeddings, and vector search for RAG.
*   **Frontend (`ai-defra-search-frontend`)**: User interface and session management.

(Legacy `ai-defra-search-data` is not used by the default core compose stack; local dev follows `service-compose/ai-defra-search-knowledge.yml`.)

## Repository Details

### 1. Core (`ai-defra-search-core`)
*   **Role**: Local development orchestration.
*   **Key Files**: `compose.yml`, `service-compose/*.yml`.
*   **Infrastructure Provided**:
    *   **Network**: `ai-defra-search` (Bridge network).
    *   **Databases**: MongoDB (Port 27017), Redis (Port 6379), Postgres (Port 5432).
    *   **AWS Mock**: LocalStack (Port 4566).

### 2. Knowledge (`ai-defra-search-knowledge`)
*   **Role**: Knowledge groups, document registration, ingest from S3 (chunk → embed → store), and semantic search for RAG.
*   **Tech Stack**: Python, FastAPI, UV, pgvector, Liquibase.
*   **Port**: `8085` in-container; default compose publishes host **`8087:8085`** (`service-compose/ai-defra-search-knowledge.yml`).
*   **Traefik**: `knowledge.localhost`.
*   **Key Paths**:
    *   `app/knowledge_group/`: Create/list knowledge groups (`POST /knowledge-group`, `GET /knowledge-groups`; `user-id` header).
    *   `app/document/`: Register uploads (`POST /documents`), ingest status; ingest runs via `app/ingest/` (JSONL plus PDF/DOCX/PPTX extractors).
    *   `app/rag/`: `POST /rag/search` — embed query (Bedrock), vector search in Postgres, enrich from MongoDB documents.
*   **Data Persistence**: Postgres (`knowledge_vectors` / pgvector), MongoDB (`knowledgeGroups`, `documents`).
*   **Dependencies**: Postgres, MongoDB, LocalStack (S3 uploads), Bedrock (embeddings; WireMock/bedrock-mock in local compose).
*   **DB Migrations**: Liquibase (`ai-defra-search-knowledge-db-migrator`) runs before app startup.

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
*   **Integration**: Calls **Knowledge** `POST /rag/search` for RAG (via `KNOWLEDGE_BASE_URL`, `KnowledgeRetriever`).

## Data Flow (Chat Request)
1.  **User** submits question on Frontend.
2.  **Frontend** (`startPostController`) sends `POST /chat` to Agent.
3.  **Agent** (`ChatService`) retrieves/creates conversation in **MongoDB**.
4.  **Agent** (optional RAG) calls **Knowledge** `POST /rag/search` for relevant chunks (via `KnowledgeRetriever`).
5.  **Agent** invokes **AWS Bedrock** (via `BedrockInferenceService`) for LLM response (with RAG context if available).
6.  **Agent** saves updated history to **MongoDB**.
7.  **Agent** returns response to **Frontend**.
8.  **Frontend** renders response via Nunjucks.

## Data Flow (Knowledge Ingestion)
1.  **Client** creates a knowledge group via **`POST /knowledge-group`** (with `user-id`).
2.  **Client** registers files with **`POST /documents`** (metadata including `knowledge_group_id`, `s3_key`, `cdp_upload_id`).
3.  **Knowledge** loads each object from **S3**, extracts chunks (JSONL or office/PDF), generates embeddings via **Bedrock**, writes rows to **Postgres** (pgvector). Document status in **MongoDB** moves `not_started` → `in_progress` → `ready` / `failed`.
4.  **RAG** uses **`POST /rag/search`** with `knowledge_group_ids` — no separate snapshot activation step.

