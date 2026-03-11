# Architecture

This file describes the structure, boundaries, and data flows of the AI Defra Search system.

## Scope

This applies to all work across the service repositories and the core orchestration repository.

## System Shape

The system is a microservices AI search application composed of three main service repositories coordinated by a core repository.

| Repository                    | Role                                              | Port  | Domain                |
|-------------------------------|---------------------------------------------------|-------|-----------------------|
| `ai-defra-search-core`        | Local development orchestration and infrastructure | —     | —                     |
| `ai-defra-search-agent`       | AI business logic and conversation state          | 8086  | —                     |
| `ai-defra-search-knowledge`   | Knowledge management, ingestion, vector search    | 8085  | `knowledge.localhost` |
| `ai-defra-search-frontend`    | Web UI and session management                     | 3000  | —                     |

Additional repositories in the `services/` directory:

| Repository                        | Role                      |
|-----------------------------------|---------------------------|
| `ai-defra-search-journey-tests`   | End-to-end journey tests  |
| `ai-defra-search-perf-tests`      | Performance tests         |

## Core (`ai-defra-search-core`)

- Owns `compose.yml` and `service-compose/*.yml` for local orchestration.
- Provides shared infrastructure: MongoDB (27017), Redis (6379), Postgres (5432), LocalStack/S3 (4566).
- Defines the `ai-defra-search` bridge network all services join.

## Agent (`ai-defra-search-agent`)

- Tech stack: Python, FastAPI, UV.
- Entry point for chat: `app/chat/router.py` → `app/chat/service.py`.
- LLM integration: `app/bedrock/service.py` calls AWS Bedrock (or LocalStack in dev).
- Stores conversation history in MongoDB.
- Calls Knowledge service `POST /rag/search` for RAG context via `KnowledgeRetriever` (`KNOWLEDGE_BASE_URL`).

## Knowledge (`ai-defra-search-knowledge`)

- Tech stack: Python, FastAPI, UV, pgvector, Liquibase.
- `app/knowledge_group/`: CRUD for knowledge groups and sources (MongoDB).
- `app/ingest/`: Reads pre-chunked JSONL from S3, generates embeddings via Bedrock, stores in Postgres (pgvector).
- `app/rag/`: Semantic search via `POST /rag/search`.
- DB migrations run via a Liquibase migrator before app startup.

## Frontend (`ai-defra-search-frontend`)

- Tech stack: Node.js, Hapi.dev, Nunjucks templates.
- `src/server/start/controller.js`: Handles form submission.
- `src/server/start/chat-api.js`: HTTP client posting to Agent API.

## Data Flow: Chat Request

1. User submits question on Frontend.
2. Frontend (`startPostController`) sends `POST /chat` to Agent.
3. Agent (`ChatService`) retrieves or creates conversation in MongoDB.
4. Agent optionally calls Knowledge `POST /rag/search` for relevant documents.
5. Agent invokes Bedrock (`BedrockInferenceService`) for LLM response with RAG context.
6. Agent saves updated history to MongoDB.
7. Agent returns response to Frontend, which renders it via Nunjucks.

## Data Flow: Knowledge Ingestion

1. Admin creates knowledge group via `POST /knowledge/groups`, adds sources via `PATCH /knowledge/groups/{id}/sources`.
2. Admin triggers `POST /knowledge/groups/{id}/ingest`.
3. Knowledge service reads pre-chunked JSONL from S3 (LocalStack), generates embeddings via Bedrock, stores vectors in Postgres.
4. Admin activates snapshot via `PATCH /snapshots/{id}/activate` to make it available for RAG.

## Service Boundaries

- Agent owns conversation state and LLM orchestration — do not embed LLM calls in Frontend or Knowledge.
- Knowledge owns all vector storage and semantic search — Agent must not query Postgres directly.
- Frontend owns only rendering and session — it must not contain business logic.
- Core owns only infrastructure definitions — no application code lives here.
