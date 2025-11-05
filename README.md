# AI Defra Search Core

Local development support for orchestrating all AI Defra Search microservices.

This repository contains local development support scripts and documentation for AI Defra Search microservices. It provides a unified development environment that orchestrates all microservices, dependencies, and performs necessary setup tasks.

## Prerequisites

- Docker
- Docker Compose
- [uv](https://docs.astral.sh/uv/getting-started/installation/#installing-uv)
- Python 3.13 or higher - We recommend using uv to manage your Python environment.
- Git

## Repositories

| Service | Type | Language |
|---------|------|----------|
| [ai-defra-search-frontend](https://github.com/DEFRA/ai-defra-search-frontend) | Frontend | JavaScript |
| [ai-defra-search-agent](https://github.com/DEFRA/ai-defra-search-agent) | Backend API | Python |
| [ai-defra-search-data](https://github.com/DEFRA/ai-defra-search-data) | Data Service | Python |

## Local Development

You will need to clone this repository before running any scripts.

```bash
git clone https://github.com/DEFRA/ai-defra-search-core

cd ai-defra-search-core

uv sync --frozen
```

### Cloning Repositories

This project contains a script to clone all the required repositories. This works by checking the service-compose directory for the services and cloning them if they do not exist.

To clone the repositories, run the following command:

```bash
uv run task clone
```

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

Clones the repositories for each microservice into the parent directory.

```bash
uv run task clone
```

### Pull

Pulls the latest remote changes for each microservice.

```bash
uv run task pull
```

### Update

Switches to and pulls the latest main branch for each microservice.

```bash
uv run task update
```
