# AI Defra Search Core

This repository contains scripts and documentation to support AI Defra Search local development.

## Prerequisites

- Docker
- Docker Compose
- uv - [Installation Guide](https://docs.astral.sh/uv/getting-started/installation/#installing-uv)
- Python 3.13 or higher - We recommend using uv to manage your Python environment.
- Git

## Repositories

| Service | Type | Language |
|---------|------|----------|
| [ai-defra-search-frontend](https://github.com/DEFRA/ai-defra-search-frontend) | Frontend | JavaScript |
| [ai-defra-search-agent](https://github.com/DEFRA/ai-defra-search-agent) | Backend API | Python |
| [ai-defra-search-data](https://github.com/DEFRA/ai-defra-search-data) | Data Service | Python |

## Local Development

You will need to clone this repository and sync the environment before running the scripts.

```bash
git clone https://github.com/DEFRA/ai-defra-search-core
cd ai-defra-search-core

uv sync --frozen
```

### Cloning Repositories

This project contains a script to clone all the required service repositories into `services/`:

```bash
uv run task clone
```

Layout after clone:

```
ai-defra-search-core/
  services/
    ai-defra-search-frontend/
    ai-defra-search-agent/
    ai-defra-search-data/
  compose.yml
  traefik/
  scripts/
```

VSCode/Cursor users can open `core.code-workspace` to index and refactor across all repos in one view.

### Environment Configuration
This repository uses a `.env` file for environment variable configuration. This must be created for the Docker Compose project to start.

> [!IMPORTANT]
> The `.env` file should not be committed to version control. Add it to your `.gitignore` file to keep sensitive configuration data secure.

```bash
touch .env
```

Once created, you can populate the `.env` file with the necessary environment variables. Please refer to the documentation for each individual microservice for specific environment variable requirements.

### Starting the Services

A single docker-compose project has been created that orchestrates all microservices, dependencies, and performs any necessary setup tasks such as database migrations.

All configuration is stored in the `.env` file. Before starting the services, ensure that the `.env` file is correctly configured. The services will use default values if no `.env` file is present.

To start all services, run the following command:

```bash
docker-compose up --build
```

To stop the services, run the following command:

```bash
docker-compose down
```

The services can still be started individually directly from their respective repositories. However, this project is intended to streamline local development by having a common entry point for all services.

## Network

All services run on a shared Docker network named `ai-defra-search` to enable inter-service communication.

## Script Documentation

This project contains a number of scripts to streamline local microservice development.

### Clone

Clones the repositories for each microservice into `services/<repo-name>`. Skips if already exists.

```bash
uv run task clone
```

### Pull

Pulls the latest remote changes for each microservice in `services/`.

```bash
uv run task pull
```

### Update

Switches to main and pulls for each microservice in `services/`.

```bash
uv run task update
```
